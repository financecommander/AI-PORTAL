"""Authentication routes."""
import hashlib
import re
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from backend.auth.jwt_handler import create_access_token

router = APIRouter()
ALLOWED_DOMAINS = {"gradeesolutions.com", "calculusresearch.io"}

# RFC 5322 simplified: local@domain with at least one dot in domain
_EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


class LoginRequest(BaseModel):
    email: str

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        v = v.lower().strip()
        if not _EMAIL_RE.match(v):
            raise ValueError("Invalid email format")
        return v


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    email = request.email  # already lowered/stripped by validator
    domain = email.split("@")[1]
    if domain not in ALLOWED_DOMAINS:
        raise HTTPException(status_code=401, detail="Email domain is not authorized")
    email_hash = hashlib.sha256(email.encode()).hexdigest()
    token = create_access_token({"sub": email_hash, "domain": domain})
    return LoginResponse(access_token=token)
