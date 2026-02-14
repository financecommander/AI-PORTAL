"""Chat orchestration and conversation history management."""

from __future__ import annotations

import sys
import time
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field

from chat.logger import UsageLogger
from config.settings import DEFAULT_MODEL, DEFAULT_TEMPERATURE, STREAMING_ENABLED
from providers.base import BaseProvider, ProviderResponse, StreamChunk
from specialists.manager import Specialist


@dataclass
class Message:
    """A single message in a conversation."""

    role: str  # "system", "user", or "assistant"
    content: str


class ChatEngine:
    """Orchestrates conversations with LLM providers.

    Maintains per-session message history and delegates to the
    configured provider for completions.
    """

    def __init__(
        self,
        provider: BaseProvider,
        specialist: Specialist | None = None,
        logger: UsageLogger | None = None,
        user_email: str = "",
    ):
        self.provider = provider
        self.specialist = specialist
        self.logger = logger
        self.user_email = user_email
        self.history: list[Message] = []

        if specialist:
            self.history.append(
                Message(role="system", content=specialist.system_prompt)
            )

    # -- public API --

    async def send(self, user_input: str) -> str:
        """Send a user message and return the assistant reply (non-streaming)."""
        self.history.append(Message(role="user", content=user_input))

        model = self.specialist.model if self.specialist else DEFAULT_MODEL
        temperature = (
            self.specialist.temperature if self.specialist else DEFAULT_TEMPERATURE
        )

        start_ns = time.monotonic_ns()
        success = True
        response: ProviderResponse | None = None

        try:
            response = await self.provider.send_message(
                messages=[
                    {"role": m.role, "content": m.content} for m in self.history
                ],
                model=model,
                system_prompt=self.specialist.system_prompt if self.specialist else "",
                temperature=temperature,
            )
        except Exception:
            success = False
            raise
        finally:
            elapsed_ms = (time.monotonic_ns() - start_ns) // 1_000_000
            self._log(response, model, elapsed_ms, success)

        self.history.append(Message(role="assistant", content=response.content))
        return response.content

    async def send_streaming(
        self, user_input: str
    ) -> AsyncGenerator[StreamChunk, None]:
        """Send a user message and yield streaming chunks.

        The caller is responsible for appending the full assistant reply
        to history after consuming all chunks.
        """
        self.history.append(Message(role="user", content=user_input))

        model = self.specialist.model if self.specialist else DEFAULT_MODEL
        temperature = (
            self.specialist.temperature if self.specialist else DEFAULT_TEMPERATURE
        )

        try:
            async for chunk in self.provider.stream_message(
                messages=[
                    {"role": m.role, "content": m.content} for m in self.history
                ],
                model=model,
                system_prompt=self.specialist.system_prompt if self.specialist else "",
                temperature=temperature,
            ):
                if chunk.is_final:
                    self._log_from_chunk(chunk, model)
                yield chunk
        except Exception:
            # Log the failure
            self._log(None, model, 0, False)
            raise

    def append_assistant_message(self, content: str) -> None:
        """Append a completed assistant response to history."""
        self.history.append(Message(role="assistant", content=content))

    def reset(self) -> None:
        """Clear history and re-apply the system prompt if set."""
        self.history.clear()
        if self.specialist:
            self.history.append(
                Message(role="system", content=self.specialist.system_prompt)
            )

    def get_history(self) -> list[dict]:
        """Return conversation history as a list of dicts."""
        return [{"role": m.role, "content": m.content} for m in self.history]

    def set_specialist(self, specialist: Specialist) -> None:
        """Switch specialist and reset conversation."""
        self.specialist = specialist
        self.reset()

    # -- private helpers --

    def _log(
        self,
        response: ProviderResponse | None,
        model: str,
        elapsed_ms: int,
        success: bool,
    ) -> None:
        if not self.logger:
            return
        self.logger.log(
            user_email=self.user_email,
            specialist_id=self.specialist.id if self.specialist else "",
            specialist_name=self.specialist.name if self.specialist else "",
            provider=self.specialist.provider if self.specialist else "",
            model=response.model if response else model,
            input_tokens=response.input_tokens if response else 0,
            output_tokens=response.output_tokens if response else 0,
            latency_ms=elapsed_ms,
            success=success,
        )

    def _log_from_chunk(self, chunk: StreamChunk, model: str) -> None:
        if not self.logger:
            return
        self.logger.log(
            user_email=self.user_email,
            specialist_id=self.specialist.id if self.specialist else "",
            specialist_name=self.specialist.name if self.specialist else "",
            provider=self.specialist.provider if self.specialist else "",
            model=chunk.model or model,
            input_tokens=chunk.input_tokens,
            output_tokens=chunk.output_tokens,
            latency_ms=int(chunk.latency_ms),
            success=True,
        )
