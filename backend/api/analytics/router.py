from fastapi import APIRouter, Depends, HTTPException, Query
from auth.cognito import verify_token
from services.analytics.metrics import get_org_metrics, get_usage_trend, get_alert_summary

router = APIRouter()

def _get_org_id(claims: dict) -> str:
    org_id = claims.get("custom:org_id")
    if not org_id:
        raise HTTPException(status_code=403, detail="No organization associated with this account")
    return org_id

@router.get("/metrics")
def org_metrics(claims: dict = Depends(verify_token)):
    return get_org_metrics(_get_org_id(claims))

@router.get("/trend")
def usage_trend(
    months: int = Query(default=6, ge=1, le=24),
    claims: dict = Depends(verify_token)
):
    return {"trend": get_usage_trend(_get_org_id(claims), months)}

@router.get("/alerts")
def alert_summary(claims: dict = Depends(verify_token)):
    return get_alert_summary(_get_org_id(claims))
