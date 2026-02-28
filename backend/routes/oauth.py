"""OAuth 2.0 routes for Google, Apple, and X (Twitter) social login."""

import hashlib
import hmac
import json
import time
from typing import Optional
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import RedirectResponse

from backend.auth.jwt_handler import create_access_token
from backend.config.settings import settings

router = APIRouter()

# ── Provider configuration ─────────────────────────────────────

_PROVIDERS = {
    "google": {
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "userinfo_url": "https://www.googleapis.com/oauth2/v3/userinfo",
        "scope": "openid email profile",
    },
    "apple": {
        "auth_url": "https://appleid.apple.com/auth/authorize",
        "token_url": "https://appleid.apple.com/auth/token",
        "userinfo_url": None,  # Apple embeds user info in the id_token
        "scope": "name email",
    },
    "x": {
        "auth_url": "https://twitter.com/i/oauth2/authorize",
        "token_url": "https://api.twitter.com/2/oauth2/token",
        "userinfo_url": "https://api.twitter.com/2/users/me",
        "scope": "users.read tweet.read offline.access",
    },
}


def _get_client_credentials(provider: str) -> tuple[str, str]:
    """Return (client_id, client_secret) for the given provider."""
    if provider == "google":
        return settings.google_oauth_client_id, settings.google_oauth_client_secret
    if provider == "apple":
        return settings.apple_oauth_client_id, settings.apple_oauth_client_secret
    if provider == "x":
        return settings.x_oauth_client_id, settings.x_oauth_client_secret
    raise HTTPException(status_code=404, detail=f"Unknown OAuth provider: {provider}")


def _callback_url(request: Request, provider: str) -> str:
    """Build the absolute callback URL that the OAuth provider will redirect back to.

    Uses the request's base URL so the URL always points to the backend host,
    not the frontend.
    """
    base = str(request.base_url).rstrip("/")
    return f"{base}/auth/oauth/{provider}/callback"


# ── State helpers (HMAC-signed, timestamp-bound) ───────────────

def _make_state(provider: str) -> str:
    """Generate a signed state parameter to prevent CSRF."""
    ts = str(int(time.time()))
    payload = f"{provider}:{ts}"
    sig = hmac.new(
        settings.oauth_state_secret.encode(),
        payload.encode(),
        hashlib.sha256,
    ).hexdigest()
    return f"{payload}:{sig}"


def _verify_state(provider: str, state: str, max_age_seconds: int = 600) -> bool:
    """Verify the HMAC-signed state and its age."""
    try:
        parts = state.split(":", 2)
        if len(parts) != 3:
            return False
        state_provider, ts, sig = parts
        if state_provider != provider:
            return False
        if abs(time.time() - int(ts)) > max_age_seconds:
            return False
        expected_payload = f"{state_provider}:{ts}"
        expected_sig = hmac.new(
            settings.oauth_state_secret.encode(),
            expected_payload.encode(),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected_sig, sig)
    except Exception:
        return False


# ── Routes ─────────────────────────────────────────────────────

@router.get("/{provider}/authorize")
async def oauth_authorize(provider: str, request: Request):
    """
    Redirect the browser to the OAuth provider's authorization page.

    Supported providers: google, apple, x
    """
    if provider not in _PROVIDERS:
        raise HTTPException(status_code=404, detail=f"Unknown OAuth provider: {provider}")

    client_id, _ = _get_client_credentials(provider)
    if not client_id:
        raise HTTPException(
            status_code=503,
            detail=f"OAuth provider '{provider}' is not configured on this server.",
        )

    cfg = _PROVIDERS[provider]
    state = _make_state(provider)
    callback = _callback_url(request, provider)

    params: dict[str, str] = {
        "client_id": client_id,
        "redirect_uri": callback,
        "response_type": "code",
        "scope": cfg["scope"],
        "state": state,
    }

    # Apple requires response_mode=form_post for web flows
    if provider == "apple":
        params["response_mode"] = "form_post"

    return RedirectResponse(url=f"{cfg['auth_url']}?{urlencode(params)}")


@router.get("/{provider}/callback")
async def oauth_callback(
    provider: str,
    request: Request,
    code: str = Query(...),
    state: str = Query(...),
    error: Optional[str] = Query(default=None),
):
    """
    Handle the OAuth provider's authorization callback.

    Exchanges the authorization code for an access token, retrieves the user's
    email, issues our own JWT, and redirects the browser to the frontend with
    the token in the query string.
    """
    if provider not in _PROVIDERS:
        raise HTTPException(status_code=404, detail=f"Unknown OAuth provider: {provider}")

    # Surface provider-reported errors
    if error:
        frontend_error_url = f"{settings.frontend_url}/oauth/callback?error={urlencode({'error': error})[6:]}"
        return RedirectResponse(url=frontend_error_url)

    # Validate state to prevent CSRF
    if not _verify_state(provider, state):
        raise HTTPException(status_code=400, detail="Invalid or expired OAuth state parameter.")

    client_id, client_secret = _get_client_credentials(provider)
    cfg = _PROVIDERS[provider]
    callback = _callback_url(request, provider)

    # ── Exchange code for tokens ───────────────────────────────
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            if provider == "x":
                # X uses Basic auth for token exchange; no PKCE for confidential clients
                token_resp = await client.post(
                    cfg["token_url"],
                    auth=(client_id, client_secret),
                    data={
                        "code": code,
                        "grant_type": "authorization_code",
                        "redirect_uri": callback,
                    },
                )
            else:
                token_resp = await client.post(
                    cfg["token_url"],
                    data={
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "code": code,
                        "grant_type": "authorization_code",
                        "redirect_uri": callback,
                    },
                )

            if token_resp.status_code != 200:
                raise HTTPException(status_code=502, detail="Token exchange with OAuth provider failed.")

            token_data = token_resp.json()
            access_token = token_data.get("access_token", "")

            # ── Fetch user info ────────────────────────────────
            email: Optional[str] = None
            name: Optional[str] = None

            if provider == "apple":
                # Apple embeds email in the id_token (JWT payload, base64-encoded).
                # NOTE: In production, verify the id_token signature against Apple's
                # public keys (https://appleid.apple.com/auth/keys) before trusting it.
                id_token = token_data.get("id_token", "")
                if id_token:
                    import base64 as _b64

                    parts = id_token.split(".")
                    if len(parts) >= 2:
                        padded = parts[1] + "=" * (4 - len(parts[1]) % 4)
                        claims = json.loads(_b64.urlsafe_b64decode(padded))
                        email = claims.get("email")

            elif provider == "google" and cfg["userinfo_url"]:
                info_resp = await client.get(
                    cfg["userinfo_url"],
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                if info_resp.status_code == 200:
                    info = info_resp.json()
                    email = info.get("email")
                    name = info.get("name")

            elif provider == "x" and cfg["userinfo_url"]:
                info_resp = await client.get(
                    cfg["userinfo_url"],
                    params={"user.fields": "name"},
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                if info_resp.status_code == 200:
                    info = info_resp.json().get("data", {})
                    name = info.get("name")
                    # X doesn't expose email without special permission;
                    # use a deterministic placeholder keyed to the user id.
                    x_id = info.get("id", "unknown")
                    email = f"x_{x_id}@x.oauth"

    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"OAuth provider unreachable: {exc}") from exc

    if not email:
        raise HTTPException(status_code=400, detail="Could not retrieve email from OAuth provider.")

    # ── Issue our own JWT ──────────────────────────────────────
    user_hash = hashlib.sha256(email.encode()).hexdigest()
    our_token = create_access_token({
        "sub": user_hash,
        "email_hint": email.split("@")[0],
        "oauth_provider": provider,
        **({"name": name} if name else {}),
    })

    # ── Redirect to frontend ───────────────────────────────────
    return RedirectResponse(url=f"{settings.frontend_url}/oauth/callback?token={our_token}")
