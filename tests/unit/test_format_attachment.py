"""Tests for provider format_attachment methods and ValidationError."""

import base64

import pytest

from chat.file_handler import ChatAttachment
from portal.errors import PortalError, ValidationError
from providers.base import BaseProvider


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_attachment(
    *,
    filename: str = "data.txt",
    content_type: str = "text/plain",
    content_b64: str | None = None,
    text_content: str | None = None,
    size_bytes: int = 100,
) -> ChatAttachment:
    if content_b64 is None:
        content_b64 = base64.b64encode(b"dummy").decode()
    return ChatAttachment(
        filename=filename,
        content_type=content_type,
        content_b64=content_b64,
        text_content=text_content,
        size_bytes=size_bytes,
    )


def _concrete_provider_class():
    """Create a minimal concrete subclass of BaseProvider for testing."""

    class _ConcreteProvider(BaseProvider):
        async def send_message(self, messages, model, system_prompt, **kwargs):
            raise NotImplementedError

        async def stream_message(self, messages, model, system_prompt, **kwargs):
            yield  # pragma: no cover

        def count_tokens(self, text):
            return len(text) // 4

        def get_available_models(self):
            return ["test-model"]

    return _ConcreteProvider()


# ---------------------------------------------------------------------------
# BaseProvider.format_attachment
# ---------------------------------------------------------------------------


class TestBaseFormatAttachment:
    def test_text_attachment(self):
        provider = _concrete_provider_class()
        att = _make_attachment(text_content="Hello world")
        result = provider.format_attachment(att)
        assert result["type"] == "text"
        assert "Hello world" in result["text"]
        assert "data.txt" in result["text"]

    def test_binary_attachment_no_text(self):
        provider = _concrete_provider_class()
        att = _make_attachment(text_content=None)
        result = provider.format_attachment(att)
        assert result["type"] == "text"
        assert "100 bytes" in result["text"]

    def test_empty_text_treated_as_no_text(self):
        provider = _concrete_provider_class()
        att = _make_attachment(text_content="")
        result = provider.format_attachment(att)
        # Empty string is falsy → falls through to binary path
        assert "bytes" in result["text"]


# ---------------------------------------------------------------------------
# OpenAIProvider.format_attachment
# ---------------------------------------------------------------------------


class TestOpenAIFormatAttachment:
    @pytest.fixture(autouse=True)
    def provider(self):
        from providers.openai_provider import OpenAIProvider

        self.prov = OpenAIProvider(api_key="sk-test-key")

    def test_image_attachment(self):
        att = _make_attachment(
            filename="photo.png",
            content_type="image/png",
            content_b64="iVBORw==",
        )
        result = self.prov.format_attachment(att)
        assert result["type"] == "image_url"
        assert result["image_url"]["url"].startswith("data:image/png;base64,")

    def test_jpeg_attachment(self):
        att = _make_attachment(
            filename="photo.jpg",
            content_type="image/jpeg",
            content_b64="abc123",
        )
        result = self.prov.format_attachment(att)
        assert result["type"] == "image_url"
        assert "image/jpeg" in result["image_url"]["url"]

    def test_text_fallback(self):
        att = _make_attachment(text_content="CSV data here")
        result = self.prov.format_attachment(att)
        assert result["type"] == "text"
        assert "CSV data here" in result["text"]


# ---------------------------------------------------------------------------
# AnthropicProvider.format_attachment
# ---------------------------------------------------------------------------


class TestAnthropicFormatAttachment:
    @pytest.fixture(autouse=True)
    def provider(self):
        from providers.anthropic_provider import AnthropicProvider

        self.prov = AnthropicProvider(api_key="sk-ant-test-key")

    def test_image_attachment(self):
        att = _make_attachment(
            filename="photo.png",
            content_type="image/png",
            content_b64="iVBORw==",
        )
        result = self.prov.format_attachment(att)
        assert result["type"] == "image"
        assert result["source"]["type"] == "base64"
        assert result["source"]["media_type"] == "image/png"
        assert result["source"]["data"] == "iVBORw=="

    def test_pdf_attachment(self):
        att = _make_attachment(
            filename="report.pdf",
            content_type="application/pdf",
            content_b64="JVBERi==",
        )
        result = self.prov.format_attachment(att)
        assert result["type"] == "document"
        assert result["source"]["media_type"] == "application/pdf"

    def test_text_fallback(self):
        att = _make_attachment(text_content="Some text")
        result = self.prov.format_attachment(att)
        assert result["type"] == "text"


# ---------------------------------------------------------------------------
# GoogleProvider.format_attachment
# ---------------------------------------------------------------------------


class TestGoogleFormatAttachment:
    @pytest.fixture(autouse=True)
    def provider(self):
        from providers.google_provider import GoogleProvider

        self.prov = GoogleProvider(api_key="AIzaSy-test-key")

    def test_any_attachment(self):
        raw = b"binary data here"
        att = _make_attachment(
            filename="file.bin",
            content_type="application/octet-stream",
            content_b64=base64.b64encode(raw).decode(),
        )
        result = self.prov.format_attachment(att)
        assert result["mime_type"] == "application/octet-stream"
        assert result["data"] == raw

    def test_image_attachment(self):
        raw = b"\x89PNG"
        att = _make_attachment(
            filename="img.png",
            content_type="image/png",
            content_b64=base64.b64encode(raw).decode(),
        )
        result = self.prov.format_attachment(att)
        assert result["mime_type"] == "image/png"
        assert result["data"] == raw


# ---------------------------------------------------------------------------
# ValidationError
# ---------------------------------------------------------------------------


class TestValidationError:
    def test_is_portal_error(self):
        assert issubclass(ValidationError, PortalError)

    def test_raise_and_catch(self):
        with pytest.raises(ValidationError, match="bad input"):
            raise ValidationError("bad input")

    def test_catch_as_portal_error(self):
        with pytest.raises(PortalError):
            raise ValidationError("also caught")

    def test_message_preserved(self):
        err = ValidationError("file too large")
        assert str(err) == "file too large"
