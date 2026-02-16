"""
Email domain-based authentication for v2.0 backend.
"""
from backend.config.settings import settings
from backend.errors import AuthenticationError


def validate_domain(email: str) -> bool:
    """Validate email domain against allowed domains."""
    if not email or "@" not in email:
        return False
    
    domain = email.split("@")[1].lower()
    return domain in settings.ALLOWED_DOMAINS


def process_email(email: str) -> str:
    """Process and validate email, returning normalized email."""
    email = email.strip().lower()
    
    if not validate_domain(email):
        raise AuthenticationError(
            f"Email domain not allowed. Allowed domains: {', '.join(settings.ALLOWED_DOMAINS)}"
        )
    
    return email
