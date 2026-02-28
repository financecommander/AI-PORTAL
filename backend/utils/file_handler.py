"""File attachment processing for chat messages.

Validates attachments, extracts text from documents, and formats
content blocks per LLM provider API requirements.

Adapted from legacy chat/file_handler.py for the FastAPI backend.
"""

import base64
import io
import logging

logger = logging.getLogger(__name__)

# ── Allowed types ──────────────────────────────────────────────

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_DOC_TYPES = {"application/pdf", "text/plain", "text/csv", "text/markdown"}
ALL_ALLOWED_TYPES = ALLOWED_IMAGE_TYPES | ALLOWED_DOC_TYPES

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


# ── Validation ─────────────────────────────────────────────────

def validate_attachment(filename: str, content_type: str, size_bytes: int) -> None:
    """Raise ValueError if the attachment is invalid."""
    if content_type not in ALL_ALLOWED_TYPES:
        raise ValueError(f"Unsupported file type: {content_type} for {filename}")
    if size_bytes > MAX_FILE_SIZE:
        raise ValueError(
            f"File {filename} exceeds 10 MB limit "
            f"({size_bytes / 1024 / 1024:.1f} MB)"
        )


# ── Text extraction ────────────────────────────────────────────

def extract_text_from_document(
    data_base64: str, content_type: str, filename: str,
) -> str | None:
    """Extract text content from document attachments.

    Returns extracted text, or None for images / binary files.
    """
    raw_bytes = base64.b64decode(data_base64)

    if content_type in ("text/plain", "text/csv", "text/markdown"):
        return raw_bytes.decode("utf-8", errors="replace")

    if content_type == "application/pdf":
        return _extract_pdf_text(raw_bytes)

    return None  # Images — no text extraction


def _extract_pdf_text(pdf_bytes: bytes) -> str | None:
    """Extract text from PDF bytes using pdfplumber.

    Returns the concatenated text of all pages, or *None* if extraction
    fails or produces empty output.
    """
    try:
        import pdfplumber

        pages: list[str] = []
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages.append(text)
        return "\n\n".join(pages) if pages else None
    except Exception as e:
        logger.warning(f"PDF text extraction failed for document: {e}")
        return None


# ── Provider formatting ────────────────────────────────────────

def process_attachments(attachments: list, provider_name: str) -> list[dict]:
    """Process attachment payloads into provider-specific content blocks.

    Args:
        attachments: List of AttachmentPayload pydantic models.
        provider_name: One of "openai", "anthropic", "google", "grok", etc.

    Returns:
        List of content block dicts ready to append to a message's
        content array.
    """
    blocks: list[dict] = []
    for att in attachments:
        validate_attachment(att.filename, att.content_type, att.size_bytes)

        if att.content_type in ALLOWED_IMAGE_TYPES:
            blocks.append(_format_image(att, provider_name))
        else:
            blocks.append(_format_document(att, provider_name))

    return blocks


def _format_image(att, provider_name: str) -> dict:
    """Format an image attachment for the target provider API."""

    if provider_name in ("openai", "grok", "xai"):
        # OpenAI vision format
        return {
            "type": "image_url",
            "image_url": {
                "url": f"data:{att.content_type};base64,{att.data_base64}",
            },
        }

    if provider_name == "anthropic":
        # Anthropic vision format
        return {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": att.content_type,
                "data": att.data_base64,
            },
        }

    if provider_name in ("google", "gemini"):
        # Google Gemini inline_data format
        return {
            "type": "inline_data",
            "inline_data": {
                "mime_type": att.content_type,
                "data": att.data_base64,
            },
        }

    # Fallback for local-ternary or unknown providers — text description
    return {
        "type": "text",
        "text": f"[Attached image: {att.filename} ({att.size_bytes / 1024:.1f} KB)]",
    }


def _format_document(att, provider_name: str) -> dict:
    """Format a document attachment — extract text and inject as context."""
    text_content = extract_text_from_document(
        att.data_base64, att.content_type, att.filename,
    )

    if text_content:
        return {
            "type": "text",
            "text": f"[Attached file: {att.filename}]\n\n{text_content}",
        }

    # Text extraction failed (e.g. scanned PDF) — try Anthropic native PDF
    if att.content_type == "application/pdf" and provider_name == "anthropic":
        return {
            "type": "document",
            "source": {
                "type": "base64",
                "media_type": "application/pdf",
                "data": att.data_base64,
            },
        }

    # Ultimate fallback
    return {
        "type": "text",
        "text": (
            f"[Attached file: {att.filename} "
            f"({att.size_bytes / 1024:.1f} KB) — could not extract text]"
        ),
    }
