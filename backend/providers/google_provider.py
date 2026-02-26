"""Google Gemini provider."""

import time
import google.generativeai as genai
from google.api_core.exceptions import (
    Unauthenticated, ResourceExhausted, DeadlineExceeded, GoogleAPIError,
)

from backend.providers.base import BaseProvider, ProviderResponse
from backend.utils.token_estimator import calculate_cost
from backend.errors.exceptions import ProviderError, ProviderAuthError, ProviderRateLimitError, ProviderTimeoutError


class GoogleProvider(BaseProvider):
    def __init__(self, api_key: str):
        super().__init__("google")
        genai.configure(api_key=api_key)

    async def send_message(
        self, messages: list[dict], model: str,
        temperature: float = 0.7, max_tokens: int = 4096,
        system_prompt: str | None = None,
    ) -> ProviderResponse:
        gemini_messages = [
            {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
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
        try:
            response = gemini_model.generate_content(gemini_messages)
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
