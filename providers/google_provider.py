"""Google provider implementation for FinanceCommander AI Portal."""

from __future__ import annotations

import base64
import os
import time
from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING, List

import google.generativeai as genai

from portal.errors import ProviderAPIError
from providers.base import BaseProvider, ProviderResponse, StreamChunk

if TYPE_CHECKING:
    from chat.file_handler import ChatAttachment


class GoogleProvider(BaseProvider):
    """Google AI provider supporting Gemini models."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key required")

        genai.configure(api_key=self.api_key)

    async def send_message(
        self,
        messages: list[dict],
        model: str,
        system_prompt: str,
        **kwargs
    ) -> ProviderResponse:
        """Send message to Google AI API."""
        start_time = time.perf_counter()

        try:
            model_instance = genai.GenerativeModel(
                model, system_instruction=system_prompt
            )
            history, last_msg = self._format_messages(messages)
            chat = model_instance.start_chat(history=history)

            response = await chat.send_message_async(last_msg, **kwargs)

            content = response.text
            input_tokens = getattr(
                getattr(response, "usage_metadata", None),
                "prompt_token_count", self.count_tokens(
                    " ".join(m["content"] for m in messages)
                )
            )
            output_tokens = getattr(
                getattr(response, "usage_metadata", None),
                "candidates_token_count", self.count_tokens(content)
            )
            latency_ms = (time.perf_counter() - start_time) * 1000

            return ProviderResponse(
                content=content,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                model=model,
                latency_ms=latency_ms
            )

        except Exception as e:
            raise ProviderAPIError("google", 500, str(e)) from e

    async def stream_message(
        self,
        messages: list[dict],
        model: str,
        system_prompt: str,
        **kwargs
    ) -> AsyncGenerator[StreamChunk, None]:
        """Yield response chunks as they arrive from Google AI."""
        start = time.perf_counter()

        try:
            model_instance = genai.GenerativeModel(
                model, system_instruction=system_prompt
            )
            history, last_msg = self._format_messages(messages)
            chat = model_instance.start_chat(history=history)

            response = await chat.send_message_async(
                last_msg, stream=True, **kwargs
            )

            total_output = ""
            async for chunk in response:
                if chunk.text:
                    total_output += chunk.text
                    yield StreamChunk(
                        content=chunk.text,
                        is_final=False,
                        input_tokens=0,
                        output_tokens=0,
                        model=model,
                        latency_ms=0,
                    )

            # Final chunk with usage stats
            input_tokens = getattr(
                getattr(response, "usage_metadata", None),
                "prompt_token_count", self.count_tokens(
                    " ".join(m["content"] for m in messages)
                )
            )
            output_tokens = getattr(
                getattr(response, "usage_metadata", None),
                "candidates_token_count", self.count_tokens(total_output)
            )

            yield StreamChunk(
                content="",
                is_final=True,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                model=model,
                latency_ms=(time.perf_counter() - start) * 1000,
            )

        except Exception as e:
            raise ProviderAPIError("google", 500, str(e)) from e

    def _format_messages(
        self, messages: list[dict]
    ) -> tuple[list[dict], str]:
        """Convert chat messages to Gemini format, returning history + last msg."""
        history = []
        for msg in messages[:-1] if messages else []:
            if msg["role"] == "user":
                history.append({"role": "user", "parts": [msg["content"]]})
            elif msg["role"] == "assistant":
                history.append({"role": "model", "parts": [msg["content"]]})
        last_msg = messages[-1]["content"] if messages else "Hello"
        return history, last_msg

    def count_tokens(self, text: str) -> int:
        """Estimate token count for text."""
        return len(text) // 4

    def get_available_models(self) -> List[str]:
        """Return list of available Google models."""
        return [
            "gemini-2.0-flash",
            "gemini-2.0-pro",
            "gemini-1.5-pro",
            "gemini-1.5-flash",
        ]

    def format_attachment(self, attachment: ChatAttachment) -> dict:
        """Format attachment for Google Generative AI API.

        Google supports native multimodal via ``Part.from_data()``.
        Returns a dict with ``mime_type`` and ``data`` keys.
        """
        return {
            "mime_type": attachment.content_type,
            "data": base64.b64decode(attachment.content_b64),
        }