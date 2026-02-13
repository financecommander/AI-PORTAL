"""Chat orchestration and conversation history management."""

from __future__ import annotations

from dataclasses import dataclass, field

from chat.logger import UsageLogger
from providers.base import BaseProvider, ChatResponse
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

    def send(self, user_input: str) -> str:
        """Send a user message and return the assistant reply."""
        self.history.append(Message(role="user", content=user_input))

        model = (
            self.specialist.model if self.specialist else "gpt-4o"
        )
        temperature = (
            self.specialist.temperature
            if self.specialist
            else 0.7
        )

        response: ChatResponse = self.provider.chat(
            messages=[
                {"role": m.role, "content": m.content}
                for m in self.history
            ],
            model=model,
            temperature=temperature,
        )

        self.history.append(
            Message(role="assistant", content=response.content)
        )

        if self.logger:
            self.logger.log(
                user_email=self.user_email,
                specialist_id=(
                    self.specialist.id if self.specialist else ""
                ),
                model=response.model,
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens,
            )

        return response.content

    def reset(self) -> None:
        """Clear history and re-apply the system prompt if set."""
        self.history.clear()
        if self.specialist:
            self.history.append(
                Message(
                    role="system", content=self.specialist.system_prompt
                )
            )

    def get_history(self) -> list[dict]:
        """Return conversation history as a list of dicts."""
        return [
            {"role": m.role, "content": m.content}
            for m in self.history
        ]

    def set_specialist(self, specialist: Specialist) -> None:
        """Switch specialist and reset conversation."""
        self.specialist = specialist
        self.reset()
