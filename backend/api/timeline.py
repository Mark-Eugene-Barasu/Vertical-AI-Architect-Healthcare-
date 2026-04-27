from fastapi import APIRouter, HTTPException, Depends, Query
from auth.cognito import verify_token
from db.timeline_repository import (
    add_timeline_event, get_patient_timeline,
    get_timeline_by_type, VALID_EVENT_TYPES
)

router = APIRouter()

@router.get("/{patient_id}")
def get_timeline(
    patient_id: str,
    limit: int = Query(default=50, ge=1, le=100),
    claims: dict = Depends(verify_token)
):
    return {"patient_id": patient_id, "timeline": get_patient_timeline(patient_id, limit)}

@router.get("/{patient_id}/{event_type}")
def get_timeline_filtered(patient_id: str, event_type: str, claims: dict = Depends(verify_token)):
    if event_type not in VALID_EVENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid event_type. Allowed: {sorted(VALID_EVENT_TYPES)}"
        )
    return {
        "patient_id":  patient_id,
        "event_type":  event_type,
        "timeline":    get_timeline_by_type(patient_id, event_type),
    }

@router.post("/{patient_id}/event")
def add_event(patient_id: str, payload: dict, claims: dict = Depends(verify_token)):
    required = ["event_type", "title", "data"]
    if not all(payload.get(k) for k in required):
        raise HTTPException(status_code=400, detail=f"Required fields: {required}")
    if payload["event_type"] not in VALID_EVENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid event_type. Allowed: {sorted(VALID_EVENT_TYPES)}"
        )
    return add_timeline_event(
        patient_id=patient_id,
        event_type=payload["event_type"],
        title=payload["title"],
        data=payload["data"],
        clinician_id=claims["sub"],
    )
