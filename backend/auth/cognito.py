import os
import time
import requests
from jose import jwk, jwt
from jose.utils import base64url_decode
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

REGION = os.getenv("AWS_REGION", "us-east-1")
USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")
CLIENT_ID = os.getenv("COGNITO_CLIENT_ID")
JWKS_URL = f"https://cognito-idp.{REGION}.amazonaws.com/{USER_POOL_ID}/.well-known/jwks.json"
EXPECTED_ISSUER = f"https://cognito-idp.{REGION}.amazonaws.com/{USER_POOL_ID}"

security = HTTPBearer()
_jwks_cache = None

def _get_jwks() -> list:
    global _jwks_cache
    if not _jwks_cache:
        resp = requests.get(JWKS_URL, timeout=5, verify=True)
        resp.raise_for_status()
        _jwks_cache = resp.json()["keys"]
    return _jwks_cache

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    token = credentials.credentials
    try:
        headers = jwt.get_unverified_headers(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Malformed token")

    key = next((k for k in _get_jwks() if k["kid"] == headers["kid"]), None)
    if not key:
        raise HTTPException(status_code=401, detail="Invalid token key")

    public_key = jwk.construct(key)
    message, encoded_sig = token.rsplit(".", 1)
    decoded_sig = base64url_decode(encoded_sig.encode())

    if not public_key.verify(message.encode(), decoded_sig):
        raise HTTPException(status_code=401, detail="Token signature invalid")

    claims = jwt.get_unverified_claims(token)

    # Validate expiry
    if claims.get("exp", 0) < int(time.time()):
        raise HTTPException(status_code=401, detail="Token has expired")

    # Validate issuer
    if claims.get("iss") != EXPECTED_ISSUER:
        raise HTTPException(status_code=401, detail="Token issuer invalid")

    # Validate audience
    if claims.get("aud") != CLIENT_ID:
        raise HTTPException(status_code=401, detail="Token audience mismatch")

    # Validate token_use — must be 'id' token
    if claims.get("token_use") != "id":
        raise HTTPException(status_code=401, detail="Invalid token type")

    return claims
