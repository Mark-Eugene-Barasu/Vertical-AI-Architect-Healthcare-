import logging
from fastapi import APIRouter, Depends
from auth.cognito import verify_token
from services.bedrock import get_clinical_decision_support
from models.requests import DecisionSupportRequest
from models.responses import DecisionSupportResponse

router = APIRouter()
logger = logging.getLogger("medimind.decision")


@router.post("/suggest", response_model=DecisionSupportResponse)
async def get_decision_support(
    payload: DecisionSupportRequest,
    claims: dict = Depends(verify_token),
):
    """Get evidence-based clinical decision support powered by AI."""
    suggestions = await get_clinical_decision_support(payload.patient_context, payload.query)
    logger.info("decision_support_query", extra={"clinician_id": claims["sub"]})
    return {"query": payload.query, "suggestions": suggestions}
