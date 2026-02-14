"""File upload handling for chat attachments.

Processes uploaded files into a standardized ChatAttachment format
suitable for submission to any LLM provider. Supports text, CSV, JSON,
Python, Markdown, PDF, and image files.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass
from pathlib import Path

from portal.errors import ValidationError

ALLOWED_EXTENSIONS: set[str] = {
    ".txt", ".csv", ".json", ".py", ".md",
    ".pdf", ".png", ".jpg", ".jpeg",
}

MAX_FILE_SIZE_MB: int = 10

# Extensions whose raw bytes can be decoded as UTF-8 text
_TEXT_EXTENSIONS: set[str] = {".txt", ".csv", ".json", ".py", ".md"}


@dataclass
class ChatAttachment:
    """Processed file attachment ready for provider submission."""

    filename: str
    content_type: str       # MIME type
    content_b64: str        # Base64-encoded raw content
    size_bytes: int
    text_content: str | None  # Extracted text (None for binary-only files)


def process_upload(uploaded_file) -> ChatAttachment:
    """Process a Streamlit UploadedFile into a ChatAttachment.

    Validates file extension and size, extracts text content where
    possible, and base64-encodes the raw content for provider submission.

    Args:
        uploaded_file: A Streamlit ``UploadedFile`` object (or any object
            with ``.name``, ``.type``, and ``.read()``).

    Returns:
        A fully populated ``ChatAttachment``.

    Raises:
        ValidationError: If the file type is not allowed or exceeds the
            size limit.
    """
    ext = Path(uploaded_file.name).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            f"File type {ext} not allowed. "
            f"Supported: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    content: bytes = uploaded_file.read()

    max_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise ValidationError(f"File exceeds {MAX_FILE_SIZE_MB}MB limit")

    text_content: str | None = None
    if ext in _TEXT_EXTENSIONS:
        text_content = content.decode("utf-8", errors="replace")
    elif ext == ".pdf":
        text_content = _extract_pdf_text(content)

    return ChatAttachment(
        filename=uploaded_file.name,
        content_type=getattr(uploaded_file, "type", None) or "application/octet-stream",
        content_b64=base64.b64encode(content).decode(),
        size_bytes=len(content),
        text_content=text_content,
    )


def _extract_pdf_text(pdf_bytes: bytes) -> str | None:
    """Extract text from PDF bytes using pdfplumber.

    Returns the concatenated text of all pages, or *None* if extraction
    fails or produces empty output.
    """
    try:
        import io
        import pdfplumber

        pages: list[str] = []
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages.append(text)
        return "\n\n".join(pages) if pages else None
    except Exception:
        return None
