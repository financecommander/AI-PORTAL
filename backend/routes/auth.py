"""Authentication routes."""

import hashlib
from fastapi import APIRouter
from pydantic import BaseModel

from backend.auth.jwt_handler import create_access_token

router = APIRouter()

ALLOWED_DOMAINS = ["financecommander.com"]


class LoginRequest(BaseModel):
    email: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    email = request.email.lower().strip()
    domain = email.split("@")[-1]
    if domain not in ALLOWED_DOMAINS:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail=f"Domain '{domain}' is not authorized")

    email_hash = hashlib.sha256(email.encode()).hexdigest()
    token = create_access_token({"sub": email_hash, "domain": domain})
    return LoginResponse(access_token=token)


@router.get("/verify")
async def verify_token(user: dict = Depends(get_current_user)):
    return {"user": user}
