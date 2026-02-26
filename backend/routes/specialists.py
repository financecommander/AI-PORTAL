"""Specialist CRUD routes."""

from fastapi import APIRouter, Depends
from backend.auth.authenticator import get_current_user
from backend.specialists.manager import (
    load_specialists, get_specialist, create_specialist,
    update_specialist, delete_specialist,
)

router = APIRouter()


@router.get("/")
async def list_specialists(user: dict = Depends(get_current_user)):
    return {"specialists": load_specialists()}


@router.get("/{specialist_id}")
async def get_one(specialist_id: str, user: dict = Depends(get_current_user)):
    return get_specialist(specialist_id)


@router.post("/")
async def create(data: dict, user: dict = Depends(get_current_user)):
    return create_specialist(data)


@router.put("/{specialist_id}")
async def update(specialist_id: str, data: dict, user: dict = Depends(get_current_user)):
    return update_specialist(specialist_id, data)


@router.delete("/{specialist_id}")
async def delete(specialist_id: str, user: dict = Depends(get_current_user)):
    delete_specialist(specialist_id)
    return {"deleted": True}
