"""CRUD operations for specialist configurations."""

from __future__ import annotations

import json
import os
import re
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone

from config.settings import (
    MAX_DESCRIPTION_LENGTH,
    MAX_MAX_TOKENS,
    MAX_SPECIALIST_NAME_LENGTH,
    MAX_SYSTEM_PROMPT_LENGTH,
    MIN_MAX_TOKENS,
    SPECIALISTS_FILE,
)


@dataclass
class Pricing:
    """Token pricing for a specialist's model (USD per 1M tokens)."""

    input_per_1m: float = 0.0
    output_per_1m: float = 0.0


@dataclass
class Specialist:
    """A specialist configuration."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "New Specialist"
    description: str = ""
    provider: str = "openai"
    model: str = "gpt-4o"
    base_url: str = ""
    system_prompt: str = "You are a helpful AI assistant."
    temperature: float = 0.7
    max_tokens: int = 4096
    pricing: Pricing = field(default_factory=Pricing)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    version: int = 1
    prompt_history: list[dict] = field(default_factory=list)

    def __post_init__(self) -> None:
        if isinstance(self.pricing, dict):
            self.pricing = Pricing(**self.pricing)


class SpecialistManager:
    """Load, save, and manage specialist definitions."""

    def __init__(self, filepath: str | None = None):
        self.filepath = filepath or SPECIALISTS_FILE
        self._specialists: list[Specialist] = []
        self._load()

    # -- persistence --

    def _load(self) -> None:
        if not os.path.exists(self.filepath):
            self._specialists = []
            return
        with open(self.filepath, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        specialists_data = data.get("specialists", data) if isinstance(data, dict) else data
        self._specialists = [Specialist(**item) for item in specialists_data]

    def _save(self) -> None:
        with open(self.filepath, "w", encoding="utf-8") as fh:
            json.dump(
                {"specialists": [asdict(s) for s in self._specialists]},
                fh,
                indent=2,
            )

    # -- CRUD --

    def list(self) -> list[Specialist]:
        """Return all specialists."""
        return list(self._specialists)

    def get(self, specialist_id: str) -> Specialist | None:
        """Return a specialist by id, or None."""
        for s in self._specialists:
            if s.id == specialist_id:
                return s
        return None

    def create(self, **kwargs) -> Specialist:
        """Create and persist a new specialist."""
        spec = Specialist(**kwargs)
        self._specialists.append(spec)
        self._save()
        return spec

    def update(self, specialist_id: str, **kwargs) -> Specialist | None:
        """Update an existing specialist. Returns None if not found."""
        spec = self.get(specialist_id)
        if spec is None:
            return None
        # Archive current prompt in history when system_prompt changes
        if "system_prompt" in kwargs and kwargs["system_prompt"] != spec.system_prompt:
            spec.prompt_history.append({
                "prompt": spec.system_prompt,
                "version": spec.version,
                "changed_at": datetime.now(timezone.utc).isoformat(),
            })
        for key, value in kwargs.items():
            if not hasattr(spec, key):
                raise AttributeError(
                    f"Specialist has no attribute '{key}'"
                )
            setattr(spec, key, value)
        spec.updated_at = datetime.now(timezone.utc).isoformat()
        spec.version += 1
        self._save()
        return spec

    def delete(self, specialist_id: str) -> bool:
        """Delete a specialist by id. Returns True if found and deleted."""
        for i, s in enumerate(self._specialists):
            if s.id == specialist_id:
                self._specialists.pop(i)
                self._save()
                return True
        return False

    # -- validation --

    VALID_PROVIDERS = {"openai", "anthropic", "google"}

    def validate_specialist(
        self,
        *,
        name: str,
        provider: str,
        model: str,
        system_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        base_url: str = "",
        description: str = "",
        exclude_id: str | None = None,
    ) -> list[str]:
        """Validate specialist fields.

        Returns a list of error strings.  An empty list means valid.
        *exclude_id* is the id of the specialist being edited (so its own
        name doesn't conflict with itself).
        """
        errors: list[str] = []

        # name
        if not name or not name.strip():
            errors.append("Name is required.")
        elif len(name) > MAX_SPECIALIST_NAME_LENGTH:
            errors.append(
                f"Name must be {MAX_SPECIALIST_NAME_LENGTH} characters or fewer."
            )
        else:
            # unique check
            for s in self._specialists:
                if s.name == name.strip() and s.id != exclude_id:
                    errors.append(f"A specialist named '{name}' already exists.")
                    break

        # provider
        if provider not in self.VALID_PROVIDERS:
            errors.append(
                f"Provider must be one of: {', '.join(sorted(self.VALID_PROVIDERS))}."
            )

        # model
        if not model or not model.strip():
            errors.append("Model is required.")

        # system_prompt
        if not system_prompt or not system_prompt.strip():
            errors.append("System prompt is required.")
        elif len(system_prompt) > MAX_SYSTEM_PROMPT_LENGTH:
            errors.append(
                f"System prompt must be {MAX_SYSTEM_PROMPT_LENGTH} characters or fewer."
            )

        # description
        if description and len(description) > MAX_DESCRIPTION_LENGTH:
            errors.append(
                f"Description must be {MAX_DESCRIPTION_LENGTH} characters or fewer."
            )

        # temperature
        if not (0.0 <= temperature <= 2.0):
            errors.append("Temperature must be between 0.0 and 2.0.")

        # max_tokens
        if not (MIN_MAX_TOKENS <= max_tokens <= MAX_MAX_TOKENS):
            errors.append(
                f"Max tokens must be between {MIN_MAX_TOKENS} and {MAX_MAX_TOKENS}."
            )

        # base_url
        if base_url and not base_url.startswith("https://"):
            errors.append("Base URL must start with https://.")

        return errors
