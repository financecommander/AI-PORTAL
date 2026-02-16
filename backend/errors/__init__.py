"""
Portal-specific error types for v2.0 backend.
"""
from typing import Optional


class PortalError(Exception):
    """Base exception for all portal errors."""
    
    def __init__(self, message: str, status_code: int = 500, details: Optional[dict] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(PortalError):
    """Authentication-related errors."""
    
    def __init__(self, message: str = "Authentication failed", details: Optional[dict] = None):
        super().__init__(message, status_code=401, details=details)


class AuthorizationError(PortalError):
    """Authorization-related errors."""
    
    def __init__(self, message: str = "Access denied", details: Optional[dict] = None):
        super().__init__(message, status_code=403, details=details)


class ValidationError(PortalError):
    """Validation errors."""
    
    def __init__(self, message: str = "Validation failed", details: Optional[dict] = None):
        super().__init__(message, status_code=422, details=details)


class NotFoundError(PortalError):
    """Resource not found errors."""
    
    def __init__(self, message: str = "Resource not found", details: Optional[dict] = None):
        super().__init__(message, status_code=404, details=details)


class ProviderError(PortalError):
    """LLM provider errors."""
    
    def __init__(self, message: str = "Provider error", details: Optional[dict] = None):
        super().__init__(message, status_code=502, details=details)
