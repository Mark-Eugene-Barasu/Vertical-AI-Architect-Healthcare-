from fastapi import HTTPException, Depends
from auth.cognito import verify_token

def get_org_context(claims: dict = Depends(verify_token)) -> dict:
    """Extract and validate org context from JWT claims."""
    org_id = claims.get("custom:org_id")
    role = claims.get("custom:role", "clinician")
    if not org_id:
        raise HTTPException(status_code=403, detail="No organization associated with this account")
    return {
        "org_id": org_id,
        "clinician_id": claims["sub"],
        "role": role,
        "email": claims.get("email"),
    }

def require_admin(ctx: dict = Depends(get_org_context)) -> dict:
    """Require admin role for sensitive operations."""
    if ctx["role"] not in ("admin", "super_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    return ctx

def require_super_admin(claims: dict = Depends(verify_token)) -> dict:
    """Require super_admin role for platform-level operations."""
    if claims.get("custom:role") != "super_admin":
        raise HTTPException(status_code=403, detail="Super admin access required")
    return claims
