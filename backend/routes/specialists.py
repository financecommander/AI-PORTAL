"""Specialist CRUD routes."""

from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from backend.auth.authenticator import get_current_user
from backend.specialists.manager import (
    load_specialists, get_specialist, create_specialist,
    update_specialist, delete_specialist,
)

router = APIRouter()


class SpecialistCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)
    provider: str = Field(..., pattern=r"^(openai|anthropic|google|grok|groq|deepseek|mistral|llama)$")
    model: str = Field(..., min_length=1, max_length=100)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4096, ge=1, le=32768)
    system_prompt: str = Field(..., min_length=1, max_length=10000)


class SpecialistUpdateRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    provider: Optional[str] = Field(default=None, pattern=r"^(openai|anthropic|google|grok|groq|deepseek|mistral|llama)$")
    model: Optional[str] = Field(default=None, min_length=1, max_length=100)
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, ge=1, le=32768)
    system_prompt: Optional[str] = Field(default=None, min_length=1, max_length=10000)


@router.get("/")
async def list_specialists(user: dict = Depends(get_current_user)):
    return {"specialists": load_specialists()}


@router.get("/{specialist_id}")
async def get_one(specialist_id: str, user: dict = Depends(get_current_user)):
    return get_specialist(specialist_id)


@router.post("/")
async def create(data: SpecialistCreateRequest, user: dict = Depends(get_current_user)):
    return create_specialist(data.model_dump())


@router.put("/{specialist_id}")
async def update(specialist_id: str, data: SpecialistUpdateRequest, user: dict = Depends(get_current_user)):
    # Only send fields that were explicitly provided (not None)
    return update_specialist(specialist_id, data.model_dump(exclude_none=True))


@router.delete("/{specialist_id}")
async def delete(specialist_id: str, user: dict = Depends(get_current_user)):
    delete_specialist(specialist_id)
    return {"deleted": True}
