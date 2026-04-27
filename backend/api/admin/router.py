import boto3
import os
import logging
from fastapi import APIRouter, Depends, HTTPException
from auth.tenant import require_super_admin
from db.org_repository import get_org
from services.billing.usage_tracker import get_usage

dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION", "us-east-1"))
orgs_table = dynamodb.Table("medimind-organizations")
logger = logging.getLogger(__name__)

router = APIRouter()

def _scan_all_orgs() -> list[dict]:
    """Paginated scan to avoid truncation on large tables."""
    items = []
    kwargs: dict = {}
    while True:
        response = orgs_table.scan(**kwargs)
        items.extend(response.get("Items", []))
        last_key = response.get("LastEvaluatedKey")
        if not last_key:
            break
        kwargs["ExclusiveStartKey"] = last_key
    return items

@router.get("/overview")
def platform_overview(claims: dict = Depends(require_super_admin)):
    orgs = _scan_all_orgs()
    total_orgs = len(orgs)
    active_orgs = sum(1 for o in orgs if o.get("status") == "active")
    plans: dict[str, int] = {"starter": 0, "growth": 0, "enterprise": 0}
    plan_prices = {"starter": 499, "growth": 1499, "enterprise": 5000}
    mrr = 0

    for org in orgs:
        plan = org.get("plan", "starter")
        plans[plan] = plans.get(plan, 0) + 1
        if org.get("status") == "active":
            mrr += plan_prices.get(plan, 0)

    return {
        "total_organizations": total_orgs,
        "active_organizations": active_orgs,
        "plan_breakdown": plans,
        "estimated_mrr": mrr,
        "estimated_arr": mrr * 12,
    }

@router.get("/organizations")
def list_all_orgs(claims: dict = Depends(require_super_admin)):
    orgs = _scan_all_orgs()
    # Strip sensitive billing fields before returning
    safe_orgs = [
        {k: v for k, v in org.items() if k not in ("stripe_customer_id", "subscription_id")}
        for org in orgs
    ]
    return {"organizations": safe_orgs}

@router.get("/organizations/{org_id}")
def get_org_detail(org_id: str, claims: dict = Depends(require_super_admin)):
    org = get_org(org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    usage = get_usage(org_id)
    safe_org = {k: v for k, v in org.items() if k not in ("stripe_customer_id", "subscription_id")}
    return {"org": safe_org, "current_usage": usage}

@router.put("/organizations/{org_id}/status")
def update_org_status(org_id: str, payload: dict, claims: dict = Depends(require_super_admin)):
    status = payload.get("status")
    if status not in ("active", "suspended", "cancelled"):
        raise HTTPException(status_code=400, detail="Invalid status")
    orgs_table.update_item(
        Key={"org_id": org_id},
        UpdateExpression="SET #s = :s",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={":s": status},
    )
    logger.info("Org status updated", extra={"org_id": org_id, "status": status, "by": claims["sub"]})
    return {"org_id": org_id, "status": status}

@router.put("/organizations/{org_id}/plan")
def override_org_plan(org_id: str, payload: dict, claims: dict = Depends(require_super_admin)):
    plan = payload.get("plan")
    if plan not in ("starter", "growth", "enterprise"):
        raise HTTPException(status_code=400, detail="Invalid plan")
    orgs_table.update_item(
        Key={"org_id": org_id},
        UpdateExpression="SET plan = :p",
        ExpressionAttributeValues={":p": plan},
    )
    logger.info("Org plan overridden", extra={"org_id": org_id, "plan": plan, "by": claims["sub"]})
    return {"org_id": org_id, "plan": plan}
