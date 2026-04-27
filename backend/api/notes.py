import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from auth.cognito import verify_token
from services.transcribe import transcribe_audio
from services.bedrock import generate_clinical_note
from db.notes_repository import save_note, get_notes, get_note, update_note
from db.timeline_repository import add_timeline_event
from models.requests import NoteGenerateRequest, NoteUpdateRequest
from models.responses import NoteResponse, NoteListResponse

router = APIRouter()
logger = logging.getLogger("medimind.notes")


@router.post("/transcribe", response_model=NoteResponse)
async def transcribe_and_generate_note(
    audio: UploadFile = File(...),
    patient_id: str = "",
    claims: dict = Depends(verify_token),
):
    """Upload audio and generate a structured SOAP note via transcription."""
    try:
        transcript = await transcribe_audio(audio)
        note = await generate_clinical_note(transcript, patient_id)
        note_id = save_note(patient_id, transcript, note, claims["sub"])
        add_timeline_event(
            patient_id, "NOTE",
            "Clinical note generated from audio",
            {"note_id": note_id},
            claims["sub"],
        )
        logger.info("note_generated_from_audio", extra={"patient_id": patient_id, "note_id": note_id})
        return {"patient_id": patient_id, "note_id": note_id, "transcript": transcript, "clinical_note": note}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("transcribe_failed", extra={"patient_id": patient_id, "error": str(e)})
        raise HTTPException(status_code=500, detail="Failed to transcribe and generate note")


@router.post("/generate", response_model=NoteResponse)
async def generate_note_from_text(
    payload: NoteGenerateRequest,
    claims: dict = Depends(verify_token),
):
    """Generate a structured SOAP note from a text transcript."""
    note = await generate_clinical_note(payload.transcript, payload.patient_id)
    note_id = save_note(payload.patient_id, payload.transcript, note, claims["sub"])
    add_timeline_event(
        payload.patient_id, "NOTE",
        "Clinical note generated from text",
        {"note_id": note_id},
        claims["sub"],
    )
    logger.info("note_generated_from_text", extra={"patient_id": payload.patient_id, "note_id": note_id})
    return {"patient_id": payload.patient_id, "note_id": note_id, "clinical_note": note}


@router.get("/{patient_id}", response_model=NoteListResponse)
def list_patient_notes(patient_id: str, claims: dict = Depends(verify_token)):
    """List all clinical notes for a patient."""
    return {"patient_id": patient_id, "notes": get_notes(patient_id)}


@router.get("/{patient_id}/{note_id}", response_model=NoteResponse)
def get_patient_note(patient_id: str, note_id: str, claims: dict = Depends(verify_token)):
    """Retrieve a specific clinical note."""
    note = get_note(patient_id, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.put("/{patient_id}/{note_id}")
def update_patient_note(
    patient_id: str,
    note_id: str,
    payload: NoteUpdateRequest,
    claims: dict = Depends(verify_token),
):
    """Update an existing clinical note."""
    update_note(patient_id, note_id, payload.clinical_note)
    add_timeline_event(
        patient_id, "NOTE",
        "Clinical note updated",
        {"note_id": note_id},
        claims["sub"],
    )
    logger.info("note_updated", extra={"patient_id": patient_id, "note_id": note_id})
    return {"status": "updated"}
