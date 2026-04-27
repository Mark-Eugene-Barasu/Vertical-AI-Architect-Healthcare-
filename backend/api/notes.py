from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from auth.cognito import verify_token
from services.transcribe import transcribe_audio
from services.bedrock import generate_clinical_note
from db.notes_repository import save_note, get_notes, get_note, update_note
from db.timeline_repository import add_timeline_event

router = APIRouter()

@router.post("/transcribe")
async def transcribe_and_generate_note(
    audio: UploadFile = File(...),
    patient_id: str = "",
    claims: dict = Depends(verify_token)
):
    try:
        transcript = await transcribe_audio(audio)
        note = await generate_clinical_note(transcript, patient_id)
        note_id = save_note(patient_id, transcript, note, claims["sub"])
        add_timeline_event(patient_id, "NOTE", "Clinical note generated from audio", {"note_id": note_id}, claims["sub"])
        return {"patient_id": patient_id, "note_id": note_id, "transcript": transcript, "clinical_note": note}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate")
async def generate_note_from_text(payload: dict, claims: dict = Depends(verify_token)):
    transcript = payload.get("transcript", "")
    patient_id = payload.get("patient_id", "")
    if not transcript:
        raise HTTPException(status_code=400, detail="transcript is required")
    note = await generate_clinical_note(transcript, patient_id)
    note_id = save_note(patient_id, transcript, note, claims["sub"])
    add_timeline_event(patient_id, "NOTE", "Clinical note generated from text", {"note_id": note_id}, claims["sub"])
    return {"patient_id": patient_id, "note_id": note_id, "clinical_note": note}

@router.get("/{patient_id}")
def list_patient_notes(patient_id: str, claims: dict = Depends(verify_token)):
    return {"patient_id": patient_id, "notes": get_notes(patient_id)}

@router.get("/{patient_id}/{note_id}")
def get_patient_note(patient_id: str, note_id: str, claims: dict = Depends(verify_token)):
    note = get_note(patient_id, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@router.put("/{patient_id}/{note_id}")
def update_patient_note(patient_id: str, note_id: str, payload: dict, claims: dict = Depends(verify_token)):
    updated_note = payload.get("clinical_note")
    if not updated_note:
        raise HTTPException(status_code=400, detail="clinical_note is required")
    update_note(patient_id, note_id, updated_note)
    add_timeline_event(patient_id, "NOTE", "Clinical note updated", {"note_id": note_id}, claims["sub"])
    return {"status": "updated"}
