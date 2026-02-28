"""Specialist CRUD manager. Reads/writes backend/config/specialists.json."""

import json
import uuid
from pathlib import Path
from datetime import datetime, timezone

from backend.errors.exceptions import SpecialistError

_SPECIALISTS_FILE = Path(__file__).parent.parent / "config" / "specialists.json"
_VALID_PROVIDERS = {"openai", "anthropic", "google", "grok", "groq", "deepseek", "mistral", "llama"}


def _load() -> list[dict]:
    if not _SPECIALISTS_FILE.exists():
        return []
    with open(_SPECIALISTS_FILE) as f:
        return json.load(f).get("specialists", [])


def _save(specialists: list[dict]) -> None:
    with open(_SPECIALISTS_FILE, "w") as f:
        json.dump({"specialists": specialists}, f, indent=2)


def load_specialists() -> list[dict]:
    return _load()


def get_specialist(specialist_id: str) -> dict:
    for s in _load():
        if s["id"] == specialist_id:
            return s
    raise SpecialistError(f"Specialist '{specialist_id}' not found")


def create_specialist(data: dict) -> dict:
    specialists = _load()
    _validate(data)
    now = datetime.now(timezone.utc).isoformat()
    specialist = {
        "id": str(uuid.uuid4()),
        "name": data["name"].strip(),
        "description": data.get("description", ""),
        "provider": data["provider"],
        "model": data["model"],
        "temperature": float(data.get("temperature", 0.7)),
        "max_tokens": int(data.get("max_tokens", 4096)),
        "system_prompt": data["system_prompt"],
        "version": 1,
        "created_at": now,
        "updated_at": now,
    }
    specialists.append(specialist)
    _save(specialists)
    return specialist


def update_specialist(specialist_id: str, data: dict) -> dict:
    specialists = _load()
    for i, s in enumerate(specialists):
        if s["id"] == specialist_id:
            for key in ("name", "description", "provider", "model", "temperature", "max_tokens", "system_prompt"):
                if key in data:
                    s[key] = data[key]
            s["version"] = s.get("version", 0) + 1
            s["updated_at"] = datetime.now(timezone.utc).isoformat()
            specialists[i] = s
            _save(specialists)
            return s
    raise SpecialistError(f"Specialist '{specialist_id}' not found")


def delete_specialist(specialist_id: str) -> bool:
    specialists = _load()
    filtered = [s for s in specialists if s["id"] != specialist_id]
    if len(filtered) == len(specialists):
        raise SpecialistError(f"Specialist '{specialist_id}' not found")
    _save(filtered)
    return True


def _validate(data: dict) -> None:
    if not data.get("name", "").strip():
        raise SpecialistError("Name is required")
    if data.get("provider", "") not in _VALID_PROVIDERS:
        raise SpecialistError(f"Provider must be one of: {_VALID_PROVIDERS}")
    if not data.get("model", ""):
        raise SpecialistError("Model is required")
    if not data.get("system_prompt", ""):
        raise SpecialistError("System prompt is required")
    temp = float(data.get("temperature", 0.7))
    if not 0.0 <= temp <= 2.0:
        raise SpecialistError("Temperature must be 0.0-2.0")
    tokens = int(data.get("max_tokens", 4096))
    if not 1 <= tokens <= 32768:
        raise SpecialistError("Max tokens must be 1-32768")
