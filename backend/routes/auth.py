"""
Authentication routes.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from backend.auth.authenticator import process_email
from backend.auth.jwt_handler import create_access_token
from backend.errors import AuthenticationError


router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    """Login request model."""
    email: EmailStr


class LoginResponse(BaseModel):
    """Login response model."""
    access_token: str
    token_type: str = "bearer"
    email: str


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Authenticate user with email domain validation."""
    try:
        email = process_email(request.email)
        access_token = create_access_token(data={"sub": email})
        
        return LoginResponse(
            access_token=access_token,
            email=email
        )
    except AuthenticationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
