"""PortalError hierarchy. All custom exceptions inherit from PortalError."""


class PortalError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AuthenticationError(PortalError):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class AuthorizationError(PortalError):
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, status_code=403)


class ProviderError(PortalError):
    def __init__(self, provider: str, message: str):
        super().__init__(f"[{provider}] {message}", status_code=502)
        self.provider = provider


class ProviderAuthError(ProviderError):
    def __init__(self, provider: str):
        super().__init__(provider, f"Authentication failed — check {provider} API key")


class ProviderRateLimitError(ProviderError):
    def __init__(self, provider: str, retry_after: float | None = None):
        msg = "Rate limit exceeded"
        if retry_after:
            msg += f" — retry after {retry_after:.0f}s"
        super().__init__(provider, msg)
        self.retry_after = retry_after


class ProviderTimeoutError(ProviderError):
    def __init__(self, provider: str, timeout_seconds: float):
        super().__init__(provider, f"Request timed out after {timeout_seconds:.0f}s")


class PipelineError(PortalError):
    def __init__(self, pipeline_name: str, message: str):
        super().__init__(f"Pipeline '{pipeline_name}': {message}", status_code=500)


class RateLimitError(PortalError):
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status_code=429)


class SpecialistError(PortalError):
    def __init__(self, message: str):
        super().__init__(message, status_code=400)
