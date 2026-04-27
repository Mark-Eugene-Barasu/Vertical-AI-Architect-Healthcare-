import boto3
import os
import logging
from fastapi import APIRouter, HTTPException, Depends
from auth.tenant import get_org_context, require_admin, require_super_admin
from db.org_repository import create_org, get_org

router = APIRouter()
logger = logging.getLogger(__name__)
cognito = boto3.client("cognito-idp", region_name=os.getenv("AWS_REGION", "us-east-1"))
USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")

VALID_ROLES = frozenset(["clinician", "admin"])

@router.post("/register")
def register_org(payload: dict, claims: dict = Depends(require_super_admin)):
    """Register a new hospital/clinic organization."""
    required = ["name", "email", "admin_email"]
    if not all(payload.get(k) for k in required):
        raise HTTPException(status_code=400, detail=f"Required fields: {required}")

    org = create_org(payload["name"], payload["email"], payload["admin_email"])

    cognito.admin_create_user(
        UserPoolId=USER_POOL_ID,
        Username=payload["admin_email"],
        UserAttributes=[
            {"Name": "email",          "Value": payload["admin_email"]},
            {"Name": "custom:org_id",  "Value": org["org_id"]},
            {"Name": "custom:role",    "Value": "admin"},
            {"Name": "email_verified", "Value": "true"},
        ],
        DesiredDeliveryMediums=["EMAIL"],
    )
    logger.info("Organization registered", extra={"org_id": org["org_id"], "by": claims["sub"]})
    return {"org_id": org["org_id"], "message": "Organization created. Admin invite sent."}

@router.get("/me")
def get_my_org(ctx: dict = Depends(get_org_context)):
    org = get_org(ctx["org_id"])
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    # Strip sensitive billing fields from response
    return {k: v for k, v in org.items() if k not in ("stripe_customer_id", "subscription_id")}

@router.get("/clinicians")
def list_clinicians(ctx: dict = Depends(require_admin)):
    response = cognito.list_users(
        UserPoolId=USER_POOL_ID,
        Filter=f'custom:org_id = "{ctx["org_id"]}"',
    )
    return {"clinicians": [
        {
            "username": u["Username"],
            "email":    next((a["Value"] for a in u["Attributes"] if a["Name"] == "email"), ""),
            "role":     next((a["Value"] for a in u["Attributes"] if a["Name"] == "custom:role"), "clinician"),
            "status":   u["UserStatus"],
        }
        for u in response.get("Users", [])
    ]}

@router.post("/clinicians/invite")
def invite_clinician(payload: dict, ctx: dict = Depends(require_admin)):
    email = payload.get("email")
    role = payload.get("role", "clinician")
    if not email:
        raise HTTPException(status_code=400, detail="email is required")
    if role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail=f"Invalid role. Allowed: {list(VALID_ROLES)}")

    cognito.admin_create_user(
        UserPoolId=USER_POOL_ID,
        Username=email,
        UserAttributes=[
            {"Name": "email",          "Value": email},
            {"Name": "custom:org_id",  "Value": ctx["org_id"]},
            {"Name": "custom:role",    "Value": role},
            {"Name": "email_verified", "Value": "true"},
        ],
        DesiredDeliveryMediums=["EMAIL"],
    )
    logger.info("Clinician invited", extra={"email": email, "org_id": ctx["org_id"]})
    return {"message": f"Invite sent to {email}"}

@router.delete("/clinicians/{username}")
def remove_clinician(username: str, ctx: dict = Depends(require_admin)):
    cognito.admin_disable_user(UserPoolId=USER_POOL_ID, Username=username)
    logger.info("Clinician disabled", extra={"username": username, "org_id": ctx["org_id"]})
    return {"message": f"Clinician {username} disabled"}
