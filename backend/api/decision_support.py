from fastapi import APIRouter, HTTPException, Depends
from auth.cognito import verify_token
from services.bedrock import get_clinical_decision_support

router = APIRouter()

@router.post("/suggest")
async def get_decision_support(payload: dict, claims: dict = Depends(verify_token)):
    patient_context = payload.get("patient_context", "")
    query = payload.get("query", "")
    if not patient_context or not query:
        raise HTTPException(status_code=400, detail="patient_context and query are required")
    suggestions = await get_clinical_decision_support(patient_context, query)
    return {"query": query, "suggestions": suggestions}
