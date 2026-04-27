import logging
from fastapi import APIRouter, HTTPException, Depends
from auth.cognito import verify_token
from services.comprehend_medical import check_drug_interactions, extract_medications
from services.alerts import build_alert, publish_sns_alert, alert_manager, AlertSeverity, AlertType
from db.timeline_repository import add_timeline_event
from models.requests import DrugCheckRequest, DrugExtractRequest
from models.responses import DrugCheckResponse, MedicationExtractResponse

router = APIRouter()
logger = logging.getLogger("medimind.drugs")


@router.post("/check", response_model=DrugCheckResponse)
async def check_interactions(
    payload: DrugCheckRequest,
    claims: dict = Depends(verify_token),
):
    """Check for drug interactions from a medication list or clinical text."""
    medications = payload.medications
    clinical_text = payload.clinical_text or ""
    patient_id = payload.patient_id or ""

    if not medications and not clinical_text:
        raise HTTPException(status_code=400, detail="medications or clinical_text is required")
    if clinical_text and not medications:
        medications = await extract_medications(clinical_text)

    interactions = await check_drug_interactions(medications)

    if patient_id:
        add_timeline_event(
            patient_id, "DRUG_CHECK",
            "Drug interaction check performed",
            {"medications": medications, "interactions_found": len(interactions)},
            claims["sub"],
        )

    for interaction in interactions:
        severity = AlertSeverity.CRITICAL if interaction["severity"] == "HIGH" else AlertSeverity.MEDIUM
        alert = build_alert(
            alert_type=AlertType.DRUG_INTERACTION,
            severity=severity,
            patient_id=patient_id,
            clinician_id=claims["sub"],
            message=interaction["warning"],
            details={"drugs": interaction["drugs"]},
        )
        await alert_manager.send_alert(claims["sub"], alert)
        publish_sns_alert(alert)

    logger.info(
        "drug_check_completed",
        extra={"patient_id": patient_id, "medication_count": len(medications), "interaction_count": len(interactions)},
    )
    return {"medications": medications, "interactions": interactions}


@router.post("/extract", response_model=MedicationExtractResponse)
async def extract_meds_from_text(
    payload: DrugExtractRequest,
    claims: dict = Depends(verify_token),
):
    """Extract medication names from clinical text using NLP."""
    medications = await extract_medications(payload.text)
    return {"medications": medications}
