import pytest

from portal.errors import (
    AuthenticationError,
    PortalError,
    ProviderAPIError,
    RateLimitError,
)


class TestPortalError:
    def test_is_exception(self):
        assert issubclass(PortalError, Exception)

    def test_raise_and_catch(self):
        with pytest.raises(PortalError):
            raise PortalError("something went wrong")

    def test_message(self):
        err = PortalError("something went wrong")
        assert str(err) == "something went wrong"


class TestProviderAPIError:
    def test_inherits_portal_error(self):
        assert issubclass(ProviderAPIError, PortalError)

    def test_attributes(self):
        err = ProviderAPIError("OpenAI", 429, "Too many requests")
        assert err.provider == "OpenAI"
        assert err.status_code == 429

    def test_message_format(self):
        err = ProviderAPIError("OpenAI", 429, "Too many requests")
        assert str(err) == "[OpenAI] 429: Too many requests"

    def test_caught_as_portal_error(self):
        with pytest.raises(PortalError):
            raise ProviderAPIError("Anthropic", 500, "Internal error")


class TestAuthenticationError:
    def test_inherits_portal_error(self):
        assert issubclass(AuthenticationError, PortalError)

    def test_raise_and_catch(self):
        with pytest.raises(AuthenticationError):
            raise AuthenticationError("invalid token")

    def test_caught_as_portal_error(self):
        with pytest.raises(PortalError):
            raise AuthenticationError("invalid token")


class TestRateLimitError:
    def test_inherits_portal_error(self):
        assert issubclass(RateLimitError, PortalError)

    def test_raise_and_catch(self):
        with pytest.raises(RateLimitError):
            raise RateLimitError("rate limit exceeded")

    def test_caught_as_portal_error(self):
        with pytest.raises(PortalError):
            raise RateLimitError("rate limit exceeded")
