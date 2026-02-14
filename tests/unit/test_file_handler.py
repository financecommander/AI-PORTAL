"""Tests for chat/file_handler.py — file upload processing."""

import base64
import io
from dataclasses import dataclass

import pytest

from chat.file_handler import (
    ALLOWED_EXTENSIONS,
    MAX_FILE_SIZE_MB,
    ChatAttachment,
    _extract_pdf_text,
    process_upload,
)
from portal.errors import ValidationError


@dataclass
class FakeUploadedFile:
    """Minimal stand-in for Streamlit UploadedFile."""

    name: str
    type: str
    _content: bytes

    def read(self) -> bytes:
        return self._content


class TestChatAttachment:
    def test_fields(self):
        att = ChatAttachment(
            filename="test.txt",
            content_type="text/plain",
            content_b64="dGVzdA==",
            size_bytes=4,
            text_content="test",
        )
        assert att.filename == "test.txt"
        assert att.content_type == "text/plain"
        assert att.size_bytes == 4
        assert att.text_content == "test"

    def test_none_text_content(self):
        att = ChatAttachment(
            filename="img.png",
            content_type="image/png",
            content_b64="abc",
            size_bytes=100,
            text_content=None,
        )
        assert att.text_content is None


class TestAllowedExtensions:
    def test_text_extensions_present(self):
        for ext in (".txt", ".csv", ".json", ".py", ".md"):
            assert ext in ALLOWED_EXTENSIONS

    def test_image_extensions_present(self):
        for ext in (".png", ".jpg", ".jpeg"):
            assert ext in ALLOWED_EXTENSIONS

    def test_pdf_present(self):
        assert ".pdf" in ALLOWED_EXTENSIONS


class TestProcessUpload:
    def test_text_file(self):
        content = b"Hello, world!"
        f = FakeUploadedFile(name="readme.txt", type="text/plain", _content=content)
        att = process_upload(f)
        assert att.filename == "readme.txt"
        assert att.content_type == "text/plain"
        assert att.size_bytes == len(content)
        assert att.text_content == "Hello, world!"
        assert base64.b64decode(att.content_b64) == content

    def test_csv_file(self):
        content = b"a,b,c\n1,2,3"
        f = FakeUploadedFile(name="data.csv", type="text/csv", _content=content)
        att = process_upload(f)
        assert att.text_content == "a,b,c\n1,2,3"

    def test_json_file(self):
        content = b'{"key": "value"}'
        f = FakeUploadedFile(name="config.json", type="application/json", _content=content)
        att = process_upload(f)
        assert att.text_content == '{"key": "value"}'

    def test_python_file(self):
        content = b"print('hello')"
        f = FakeUploadedFile(name="script.py", type="text/x-python", _content=content)
        att = process_upload(f)
        assert att.text_content == "print('hello')"

    def test_markdown_file(self):
        content = b"# Title\n\nParagraph"
        f = FakeUploadedFile(name="doc.md", type="text/markdown", _content=content)
        att = process_upload(f)
        assert att.text_content == "# Title\n\nParagraph"

    def test_image_file_no_text_extraction(self):
        content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        f = FakeUploadedFile(name="photo.png", type="image/png", _content=content)
        att = process_upload(f)
        assert att.text_content is None
        assert att.size_bytes == len(content)
        assert att.content_type == "image/png"

    def test_jpeg_file(self):
        content = b"\xff\xd8\xff" + b"\x00" * 50
        f = FakeUploadedFile(name="photo.jpg", type="image/jpeg", _content=content)
        att = process_upload(f)
        assert att.text_content is None
        assert att.filename == "photo.jpg"

    def test_jpeg_extension(self):
        content = b"\xff\xd8\xff" + b"\x00" * 50
        f = FakeUploadedFile(name="photo.jpeg", type="image/jpeg", _content=content)
        att = process_upload(f)
        assert att.filename == "photo.jpeg"

    def test_disallowed_extension(self):
        f = FakeUploadedFile(name="virus.exe", type="application/octet-stream", _content=b"bad")
        with pytest.raises(ValidationError, match="not allowed"):
            process_upload(f)

    def test_disallowed_extension_html(self):
        f = FakeUploadedFile(name="page.html", type="text/html", _content=b"<h1>Hi</h1>")
        with pytest.raises(ValidationError, match="not allowed"):
            process_upload(f)

    def test_file_too_large(self):
        content = b"\x00" * (MAX_FILE_SIZE_MB * 1024 * 1024 + 1)
        f = FakeUploadedFile(name="big.txt", type="text/plain", _content=content)
        with pytest.raises(ValidationError, match="exceeds"):
            process_upload(f)

    def test_file_exactly_at_limit(self):
        content = b"x" * (MAX_FILE_SIZE_MB * 1024 * 1024)
        f = FakeUploadedFile(name="exact.txt", type="text/plain", _content=content)
        att = process_upload(f)
        assert att.size_bytes == MAX_FILE_SIZE_MB * 1024 * 1024

    def test_case_insensitive_extension(self):
        f = FakeUploadedFile(name="README.TXT", type="text/plain", _content=b"hello")
        att = process_upload(f)
        assert att.filename == "README.TXT"

    def test_missing_type_defaults(self):
        """File with no .type attribute should default to application/octet-stream."""

        class NoType:
            name = "data.txt"
            _data = b"foo"
            def read(self):
                return self._data

        f = NoType()
        att = process_upload(f)
        assert att.content_type == "application/octet-stream"

    def test_base64_roundtrip(self):
        content = b"\x00\xff\x42binary data"
        f = FakeUploadedFile(name="data.txt", type="text/plain", _content=content)
        att = process_upload(f)
        assert base64.b64decode(att.content_b64) == content

    def test_utf8_errors_replaced(self):
        content = b"Hello \xff\xfe world"
        f = FakeUploadedFile(name="bad_encoding.txt", type="text/plain", _content=content)
        att = process_upload(f)
        assert att.text_content is not None
        assert "Hello" in att.text_content
        assert "world" in att.text_content


class TestExtractPdfText:
    def test_returns_none_for_invalid_pdf(self):
        assert _extract_pdf_text(b"not a pdf") is None

    def test_returns_none_for_empty_bytes(self):
        assert _extract_pdf_text(b"") is None
