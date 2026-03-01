"""Google Gemini provider."""

import asyncio
import time
from functools import partial
from typing import AsyncGenerator
import google.generativeai as genai
from google.api_core.exceptions import (
    Unauthenticated, ResourceExhausted, DeadlineExceeded, GoogleAPIError,
)

from backend.providers.base import BaseProvider, ProviderResponse, StreamChunk
from backend.utils.token_estimator import calculate_cost
from backend.errors.exceptions import ProviderError, ProviderAuthError, ProviderRateLimitError, ProviderTimeoutError


class GoogleProvider(BaseProvider):
    def __init__(self, api_key: str):
        super().__init__("google")
        genai.configure(api_key=api_key)

    @staticmethod
    def _content_to_parts(content) -> list:
        """Convert a message's content field to Gemini parts format.

        Handles both simple strings and rich content arrays (with images).
        """
        if isinstance(content, str):
            return [content]

        if isinstance(content, list):
            parts: list = []
            for block in content:
                if not isinstance(block, dict):
                    parts.append(str(block))
                elif block.get("type") == "text":
                    parts.append(block["text"])
                elif block.get("type") == "inline_data":
                    parts.append({
                        "inline_data": {
                            "mime_type": block["inline_data"]["mime_type"],
                            "data": block["inline_data"]["data"],
                        }
                    })
                # Skip unsupported block types gracefully
            return parts

        return [str(content)]

    async def send_message(
        self, messages: list[dict], model: str,
        temperature: float = 0.7, max_tokens: int = 4096,
        system_prompt: str | None = None,
    ) -> ProviderResponse:
        gemini_messages = [
            {
                "role": "user" if m["role"] == "user" else "model",
                "parts": self._content_to_parts(m["content"]),
            }
            for m in messages
        ]
        gemini_model = genai.GenerativeModel(
            model_name=model,
            system_instruction=system_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature, max_output_tokens=max_tokens,
            ),
        )
        start = time.perf_counter()
        loop = asyncio.get_event_loop()
        try:
            response = await loop.run_in_executor(
                None, partial(gemini_model.generate_content, gemini_messages)
            )
        except Unauthenticated:
            raise ProviderAuthError(self.name)
        except ResourceExhausted:
            raise ProviderRateLimitError(self.name)
        except DeadlineExceeded:
            raise ProviderTimeoutError(self.name, 60.0)
        except GoogleAPIError as e:
            raise ProviderError(self.name, str(e))

        latency = (time.perf_counter() - start) * 1000
        input_tokens = getattr(response.usage_metadata, "prompt_token_count", 0) if hasattr(response, "usage_metadata") and response.usage_metadata else 0
        output_tokens = getattr(response.usage_metadata, "candidates_token_count", 0) if hasattr(response, "usage_metadata") and response.usage_metadata else 0

        return ProviderResponse(
            content=response.text or "", model=model,
            input_tokens=input_tokens, output_tokens=output_tokens,
            latency_ms=latency, cost_usd=calculate_cost(model, input_tokens, output_tokens),
        )

    async def stream_message(
        self, messages: list[dict], model: str,
        temperature: float = 0.7, max_tokens: int = 4096,
        system_prompt: str | None = None,
    ) -> AsyncGenerator[StreamChunk, None]:
        gemini_messages = [
            {
                "role": "user" if m["role"] == "user" else "model",
                "parts": self._content_to_parts(m["content"]),
            }
            for m in messages
        ]
        gemini_model = genai.GenerativeModel(
            model_name=model,
            system_instruction=system_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature, max_output_tokens=max_tokens,
            ),
        )

        start = time.perf_counter()
        loop = asyncio.get_event_loop()

        try:
            response = await loop.run_in_executor(
                None, partial(gemini_model.generate_content, gemini_messages, stream=True)
            )
        except Unauthenticated:
            raise ProviderAuthError(self.name)
        except ResourceExhausted:
            raise ProviderRateLimitError(self.name)
        except DeadlineExceeded:
            raise ProviderTimeoutError(self.name, 60.0)
        except GoogleAPIError as e:
            raise ProviderError(self.name, str(e))

        input_tokens = 0
        output_tokens = 0

        # Iterate chunks in a thread since the Gemini SDK uses synchronous iteration
        def _iter_chunks():
            chunks = []
            for chunk in response:
                chunks.append(chunk)
            return chunks

        try:
            chunks = await loop.run_in_executor(None, _iter_chunks)
        except Unauthenticated:
            raise ProviderAuthError(self.name)
        except ResourceExhausted:
            raise ProviderRateLimitError(self.name)
        except DeadlineExceeded:
            raise ProviderTimeoutError(self.name, 60.0)
        except GoogleAPIError as e:
            raise ProviderError(self.name, str(e))

        for i, chunk in enumerate(chunks):
            text = ""
            if chunk.parts:
                text = chunk.parts[0].text or ""

            # Usage metadata is typically on the last chunk
            if hasattr(chunk, "usage_metadata") and chunk.usage_metadata:
                input_tokens = getattr(chunk.usage_metadata, "prompt_token_count", 0) or 0
                output_tokens = getattr(chunk.usage_metadata, "candidates_token_count", 0) or 0

            is_last = i == len(chunks) - 1
            if is_last:
                latency = (time.perf_counter() - start) * 1000
                yield StreamChunk(
                    content=text, is_final=True,
                    input_tokens=input_tokens, output_tokens=output_tokens,
                    model=model, latency_ms=latency,
                    cost_usd=calculate_cost(model, input_tokens, output_tokens),
                )
            else:
                yield StreamChunk(content=text)
