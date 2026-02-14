"""Google provider implementation for FinanceCommander AI Portal."""

import os
from typing import List

import google.generativeai as genai

from portal.errors import ProviderAPIError
from providers.base import BaseProvider, ProviderResponse


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
        import time
        start_time = time.time()

        try:
            # Initialize model
            model_instance = genai.GenerativeModel(model)

            # Build conversation history
            history = []
            for msg in messages:
                if msg["role"] == "user":
                    history.append({"role": "user", "parts": [msg["content"]]})
                elif msg["role"] == "assistant":
                    history.append({"role": "model", "parts": [msg["content"]]})

            # Start chat with system prompt
            chat = model_instance.start_chat(history=history)

            # Send message
            response = await chat.send_message_async(
                messages[-1]["content"] if messages else "Hello",
                **kwargs
            )

            content = response.text
            # Estimate tokens (Google doesn't provide exact counts)
            input_tokens = self.count_tokens(" ".join([m["content"] for m in messages]))
            output_tokens = self.count_tokens(content)
            latency_ms = (time.time() - start_time) * 1000

            return ProviderResponse(
                content=content,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                model=model,
                latency_ms=latency_ms
            )

        except Exception as e:
            raise ProviderAPIError("google", 500, str(e)) from e

    def count_tokens(self, text: str) -> int:
        """Estimate token count for text."""
        # Simple estimation: ~4 characters per token
        return len(text) // 4

    def get_available_models(self) -> List[str]:
        """Return list of available Google models."""
        return [
            "gemini-1.5-pro",
            "gemini-1.5-flash"
        ]