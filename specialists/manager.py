"""CRUD operations for specialist configurations."""

import json
import os
import uuid
from dataclasses import asdict, dataclass, field

from config.settings import SPECIALISTS_FILE


@dataclass
class Specialist:
    """A specialist configuration."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "New Specialist"
    system_prompt: str = "You are a helpful AI assistant."
    model: str = "gpt-4o"
    temperature: float = 0.7


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
        self._specialists = [Specialist(**item) for item in data]

    def _save(self) -> None:
        with open(self.filepath, "w", encoding="utf-8") as fh:
            json.dump(
                [asdict(s) for s in self._specialists],
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
        for key, value in kwargs.items():
            if not hasattr(spec, key):
                raise AttributeError(
                    f"Specialist has no attribute '{key}'"
                )
            setattr(spec, key, value)
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
