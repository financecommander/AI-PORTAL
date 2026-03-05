"""Google Gemini provider — unified google-genai SDK.

Migrated from deprecated google.generativeai to the new google-genai SDK
which provides native async via client.aio (no more run_in_executor).
"""

import logging
import time
from typing import AsyncGenerator

from google import genai
from google.genai import types

from backend.providers.base import BaseProvider, ProviderResponse, StreamChunk
from backend.utils.token_estimator import calculate_cost
from backend.errors.exceptions import (
    ProviderError, ProviderAuthError,
    ProviderRateLimitError, ProviderTimeoutError,
)

logger = logging.getLogger(__name__)


class GoogleProvider(BaseProvider):
    def __init__(self, api_key: str):
        super().__init__("google")
        self.client = genai.Client(api_key=api_key)

    # ── Content helpers ──────────────────────────────────────────

    @staticmethod
    def _content_to_parts(content) -> list:
        """Convert a message's content field to Gemini parts format.

        Handles both simple strings and rich content arrays (with images).
        Returns a list of dicts suitable for the google-genai SDK.
        """
        if isinstance(content, str):
            return [{"text": content}]

        if isinstance(content, list):
            parts: list = []
            for block in content:
                if not isinstance(block, dict):
                    parts.append({"text": str(block)})
                elif block.get("type") == "text":
                    parts.append({"text": block["text"]})
                elif block.get("type") == "inline_data":
                    parts.append({
                        "inline_data": {
                            "mime_type": block["inline_data"]["mime_type"],
                            "data": block["inline_data"]["data"],
                        }
                    })
                # Skip unsupported block types gracefully
            return parts

        return [{"text": str(content)}]

    @staticmethod
    def _to_contents(messages: list[dict]) -> list[dict]:
        """Convert chat message list to Gemini contents format."""
        return [
            {
                "role": "user" if m["role"] == "user" else "model",
                "parts": GoogleProvider._content_to_parts(m["content"]),
            }
            for m in messages
        ]

    # ── Error mapping ────────────────────────────────────────────

    def _handle_error(self, e: Exception) -> None:
        """Map SDK / API errors to our ProviderError hierarchy."""
        msg = str(e).lower()
        if "unauthenticated" in msg or "401" in msg or "api key" in msg:
            raise ProviderAuthError(self.name) from e
        if "resource exhausted" in msg or "429" in msg or "quota" in msg:
            raise ProviderRateLimitError(self.name) from e
        if "deadline" in msg or "timeout" in msg or "504" in msg:
            raise ProviderTimeoutError(self.name, 60.0) from e
        raise ProviderError(self.name, str(e)) from e

    # ── Usage metadata extraction ────────────────────────────────

    @staticmethod
    def _extract_tokens(usage_metadata) -> tuple[int, int]:
        """Pull input/output token counts from usage_metadata."""
        if not usage_metadata:
            return 0, 0
        inp = getattr(usage_metadata, "prompt_token_count", 0) or 0
        out = getattr(usage_metadata, "candidates_token_count", 0) or 0
        return inp, out

    # ── Send (non-streaming) ─────────────────────────────────────

    async def send_message(
        self, messages: list[dict], model: str,
        temperature: float = 0.7, max_tokens: int = 4096,
        system_prompt: str | None = None,
    ) -> ProviderResponse:
        contents = self._to_contents(messages)
        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            system_instruction=system_prompt,
        )

        start = time.perf_counter()
        try:
            response = await self.client.aio.models.generate_content(
                model=model, contents=contents, config=config,
            )
        except Exception as e:
            self._handle_error(e)

        latency = (time.perf_counter() - start) * 1000
        input_tokens, output_tokens = self._extract_tokens(
            getattr(response, "usage_metadata", None)
        )

        return ProviderResponse(
            content=response.text or "", model=model,
            input_tokens=input_tokens, output_tokens=output_tokens,
            latency_ms=latency,
            cost_usd=calculate_cost(model, input_tokens, output_tokens),
        )

    # ── Stream ───────────────────────────────────────────────────

    async def stream_message(
        self, messages: list[dict], model: str,
        temperature: float = 0.7, max_tokens: int = 4096,
        system_prompt: str | None = None,
    ) -> AsyncGenerator[StreamChunk, None]:
        contents = self._to_contents(messages)
        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            system_instruction=system_prompt,
        )

        start = time.perf_counter()
        input_tokens = 0
        output_tokens = 0

        try:
            async for chunk in await self.client.aio.models.generate_content_stream(
                model=model, contents=contents, config=config,
            ):
                text = ""
                if hasattr(chunk, "text") and chunk.text:
                    text = chunk.text

                # Usage metadata usually arrives on the last chunk
                inp, out = self._extract_tokens(
                    getattr(chunk, "usage_metadata", None)
                )
                if inp:
                    input_tokens = inp
                if out:
                    output_tokens = out

                yield StreamChunk(content=text)
        except Exception as e:
            self._handle_error(e)

        # Final chunk with accumulated metrics
        latency = (time.perf_counter() - start) * 1000
        yield StreamChunk(
            content="", is_final=True,
            input_tokens=input_tokens, output_tokens=output_tokens,
            model=model, latency_ms=latency,
            cost_usd=calculate_cost(model, input_tokens, output_tokens),
        )
