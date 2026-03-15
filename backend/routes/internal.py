"""
Internal API — machine-to-machine routes for swarm services.
Authenticated via X-Internal-Key header (shared secret, GCP-internal only).
Never exposed externally — nginx should block /internal/* from public internet.
"""

import os
from fastapi import APIRouter, Header, HTTPException

from backend.config.settings import settings

router = APIRouter()

INTERNAL_KEY = os.getenv("PORTAL_INTERNAL_KEY", "")

_PROVIDER_KEY_MAP = {
    "anthropic": lambda: settings.anthropic_api_key,
    "openai":    lambda: settings.openai_api_key,
    "google":    lambda: settings.google_api_key,
    "grok":      lambda: settings.xai_api_key,
    "deepseek":  lambda: settings.deepseek_api_key,
    "mistral":   lambda: settings.mistral_api_key,
    "groq":      lambda: settings.groq_api_key,
}


def _auth(x_internal_key: str = Header(default="")):
    if not INTERNAL_KEY:
        raise HTTPException(503, "Internal key not configured on portal")
    if x_internal_key != INTERNAL_KEY:
        raise HTTPException(403, "Invalid internal key")


@router.get("/keys/{provider}")
async def get_provider_key(provider: str, x_internal_key: str = Header(default="")):
    """Return API key for a given provider. Swarm-internal use only."""
    _auth(x_internal_key)
    getter = _PROVIDER_KEY_MAP.get(provider.lower())
    if not getter:
        raise HTTPException(404, f"Unknown provider: {provider}")
    key = getter()
    if not key:
        raise HTTPException(503, f"{provider} API key not configured on portal")
    return {"provider": provider, "key": key}


@router.get("/keys")
async def list_configured_providers(x_internal_key: str = Header(default="")):
    """List which providers have keys configured (no key values returned)."""
    _auth(x_internal_key)
    return {
        "providers": [
            p for p, getter in _PROVIDER_KEY_MAP.items() if getter()
        ]
    }
