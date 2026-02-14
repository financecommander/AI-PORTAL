class PortalError(Exception):
    """Base error for all portal operations."""
    pass


class ProviderAPIError(PortalError):
    """Raised when an LLM provider API call fails."""
    def __init__(self, provider: str, status_code: int, message: str):
        self.provider = provider
        self.status_code = status_code
        super().__init__(f"[{provider}] {status_code}: {message}")


class AuthenticationError(PortalError):
    """Raised when user authentication fails."""
    pass


class RateLimitError(PortalError):
    """Raised when user exceeds rate limits."""
    pass
