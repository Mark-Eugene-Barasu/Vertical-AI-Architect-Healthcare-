import logging
from fastapi import APIRouter, HTTPException, Depends
from botocore.exceptions import ClientError
from requests.exceptions import RequestException
from auth.cognito import verify_token
from services.fhir import (
    get_patient,
    create_patient,
    create_clinical_note_document,
    get_patient_conditions,
    get_patient_medications,
)

router = APIRouter()
logger = logging.getLogger(__name__)

def _handle_fhir_error(e: Exception, context: str) -> None:
    """Translate FHIR/network errors into safe HTTP responses."""
    if isinstance(e, RequestException):
        logger.error("FHIR request failed", extra={"context": context, "error": str(e)})
        raise HTTPException(status_code=502, detail="EHR service unavailable. Please try again.")
    if isinstance(e, ClientError):
        logger.error("AWS client error", extra={"context": context, "error": str(e)})
        raise HTTPException(status_code=502, detail="Cloud service error. Please try again.")
    logger.error("Unexpected FHIR error", extra={"context": context, "error": str(e)})
    raise HTTPException(status_code=500, detail="An unexpected error occurred.")

@router.get("/patient/{patient_id}")
def fetch_patient(patient_id: str, claims: dict = Depends(verify_token)):
    try:
        return get_patient(patient_id)
    except Exception as e:
        _handle_fhir_error(e, f"fetch_patient:{patient_id}")

@router.post("/patient")
def register_patient(payload: dict, claims: dict = Depends(verify_token)):
    name   = payload.get("name")
    dob    = payload.get("dob")
    gender = payload.get("gender")
    if not all([name, dob, gender]):
        raise HTTPException(status_code=400, detail="name, dob, and gender are required")
    try:
        return create_patient(name, dob, gender)
    except Exception as e:
        _handle_fhir_error(e, "register_patient")

@router.post("/patient/{patient_id}/note")
def store_note_to_ehr(patient_id: str, payload: dict, claims: dict = Depends(verify_token)):
    note_text = payload.get("note_text")
    if not note_text:
        raise HTTPException(status_code=400, detail="note_text is required")
    try:
        return create_clinical_note_document(patient_id, note_text, claims["sub"])
    except Exception as e:
        _handle_fhir_error(e, f"store_note:{patient_id}")

@router.get("/patient/{patient_id}/conditions")
def fetch_conditions(patient_id: str, claims: dict = Depends(verify_token)):
    try:
        return get_patient_conditions(patient_id)
    except Exception as e:
        _handle_fhir_error(e, f"fetch_conditions:{patient_id}")

@router.get("/patient/{patient_id}/medications")
def fetch_medications(patient_id: str, claims: dict = Depends(verify_token)):
    try:
        return get_patient_medications(patient_id)
    except Exception as e:
        _handle_fhir_error(e, f"fetch_medications:{patient_id}")
