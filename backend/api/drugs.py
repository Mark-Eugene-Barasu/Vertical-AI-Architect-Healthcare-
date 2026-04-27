from fastapi import APIRouter, HTTPException, Depends
from auth.cognito import verify_token
from services.comprehend_medical import check_drug_interactions, extract_medications
from services.alerts import build_alert, publish_sns_alert, alert_manager, AlertSeverity, AlertType
from db.timeline_repository import add_timeline_event

router = APIRouter()

@router.post("/check")
async def check_interactions(payload: dict, claims: dict = Depends(verify_token)):
    medications = payload.get("medications", [])
    clinical_text = payload.get("clinical_text", "")
    patient_id = payload.get("patient_id", "")

    if not medications and not clinical_text:
        raise HTTPException(status_code=400, detail="medications or clinical_text is required")
    if clinical_text and not medications:
        medications = await extract_medications(clinical_text)

    interactions = await check_drug_interactions(medications)

    if patient_id:
        add_timeline_event(patient_id, "DRUG_CHECK", "Drug interaction check performed",
                           {"medications": medications, "interactions_found": len(interactions)}, claims["sub"])

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

    return {"medications": medications, "interactions": interactions}

@router.post("/extract")
async def extract_meds_from_text(payload: dict, claims: dict = Depends(verify_token)):
    text = payload.get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="text is required")
    medications = await extract_medications(text)
    return {"medications": medications}
