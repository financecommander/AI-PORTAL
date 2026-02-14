"""Tests for specialist duplication, pinning, sorting, and usage stats."""

import csv
import json

import pytest

from chat.logger import UsageLogger
from specialists.manager import Specialist, SpecialistManager


@pytest.fixture
def tmp_specialists_file(tmp_path):
    filepath = tmp_path / "specialists.json"
    initial = {
        "specialists": [
            {
                "id": "alpha",
                "name": "Alpha Bot",
                "description": "First",
                "provider": "openai",
                "model": "gpt-4o",
                "system_prompt": "You are Alpha.",
                "temperature": 0.5,
                "max_tokens": 2048,
                "pricing": {"input_per_1m": 2.50, "output_per_1m": 10.00},
                "created_at": "2026-01-01T00:00:00+00:00",
                "updated_at": "2026-01-01T00:00:00+00:00",
                "version": 1,
                "prompt_history": [],
            },
            {
                "id": "beta",
                "name": "Beta Bot",
                "description": "Second",
                "provider": "anthropic",
                "model": "claude-3-sonnet",
                "system_prompt": "You are Beta.",
                "temperature": 0.3,
                "max_tokens": 4096,
                "pricing": {"input_per_1m": 3.00, "output_per_1m": 15.00},
                "created_at": "2026-01-02T00:00:00+00:00",
                "updated_at": "2026-01-02T00:00:00+00:00",
                "version": 2,
                "prompt_history": [{"prompt": "Old prompt", "version": 1, "changed_at": "2026-01-01T12:00:00+00:00"}],
            },
        ]
    }
    filepath.write_text(json.dumps(initial))
    return str(filepath)


@pytest.fixture
def manager(tmp_specialists_file):
    return SpecialistManager(filepath=tmp_specialists_file)


# -- Duplication --


class TestDuplicate:
    def test_basic_duplicate(self, manager):
        clone = manager.duplicate("alpha")
        assert clone is not None
        assert clone.name == "Alpha Bot (Copy)"
        assert clone.id != "alpha"
        assert len(clone.id) == 36  # UUID format
        assert clone.provider == "openai"
        assert clone.model == "gpt-4o"
        assert clone.system_prompt == "You are Alpha."
        assert clone.temperature == 0.5
        assert clone.max_tokens == 2048
        assert clone.version == 1
        assert clone.prompt_history == []

    def test_duplicate_persists(self, tmp_specialists_file):
        mgr1 = SpecialistManager(filepath=tmp_specialists_file)
        clone = mgr1.duplicate("alpha")

        mgr2 = SpecialistManager(filepath=tmp_specialists_file)
        assert mgr2.get(clone.id) is not None
        assert len(mgr2.list()) == 3

    def test_duplicate_nonexistent(self, manager):
        assert manager.duplicate("nonexistent") is None

    def test_duplicate_has_new_timestamps(self, manager):
        original = manager.get("alpha")
        clone = manager.duplicate("alpha")
        assert clone.created_at != original.created_at

    def test_duplicate_preserves_pricing(self, manager):
        clone = manager.duplicate("alpha")
        assert clone.pricing.input_per_1m == 2.50
        assert clone.pricing.output_per_1m == 10.00

    def test_duplicate_clears_prompt_history(self, manager):
        """Even if source has prompt history, clone starts fresh."""
        clone = manager.duplicate("beta")
        assert clone.prompt_history == []
        assert clone.name == "Beta Bot (Copy)"

    def test_duplicate_increases_list_count(self, manager):
        assert len(manager.list()) == 2
        manager.duplicate("alpha")
        assert len(manager.list()) == 3


# -- Pinning --


class TestTogglePin:
    def test_pin(self):
        pinned: set[str] = set()
        result = SpecialistManager.toggle_pin("alpha", pinned)
        assert result is True
        assert "alpha" in pinned

    def test_unpin(self):
        pinned: set[str] = {"alpha"}
        result = SpecialistManager.toggle_pin("alpha", pinned)
        assert result is False
        assert "alpha" not in pinned

    def test_toggle_cycle(self):
        pinned: set[str] = set()
        assert SpecialistManager.toggle_pin("x", pinned) is True
        assert SpecialistManager.toggle_pin("x", pinned) is False
        assert SpecialistManager.toggle_pin("x", pinned) is True

    def test_multiple_pins(self):
        pinned: set[str] = set()
        SpecialistManager.toggle_pin("a", pinned)
        SpecialistManager.toggle_pin("b", pinned)
        assert pinned == {"a", "b"}


class TestListSorted:
    def test_no_pins_alphabetical(self, manager):
        result = manager.list_sorted()
        names = [s.name for s in result]
        assert names == ["Alpha Bot", "Beta Bot"]

    def test_pinned_first(self, manager):
        result = manager.list_sorted(pinned={"beta"})
        names = [s.name for s in result]
        assert names == ["Beta Bot", "Alpha Bot"]

    def test_both_pinned_alphabetical(self, manager):
        result = manager.list_sorted(pinned={"alpha", "beta"})
        names = [s.name for s in result]
        assert names == ["Alpha Bot", "Beta Bot"]

    def test_empty_pinned_set(self, manager):
        result = manager.list_sorted(pinned=set())
        names = [s.name for s in result]
        assert names == ["Alpha Bot", "Beta Bot"]

    def test_nonexistent_pin_ignored(self, manager):
        result = manager.list_sorted(pinned={"nonexistent"})
        names = [s.name for s in result]
        assert names == ["Alpha Bot", "Beta Bot"]


# -- Usage Stats --


class TestGetSpecialistStats:
    def test_no_logs(self, tmp_path):
        logger = UsageLogger(log_dir=str(tmp_path))
        stats = logger.get_specialist_stats("alpha")
        assert stats["total_requests"] == 0
        assert stats["total_tokens"] == 0
        assert stats["total_cost"] == 0.0
        assert stats["avg_latency_ms"] == 0.0
        assert stats["success_rate"] == 0.0
        assert stats["last_used"] is None

    def test_single_entry(self, tmp_path):
        logger = UsageLogger(log_dir=str(tmp_path))
        logger.log("u@test.com", "alpha", "Alpha Bot", "openai", "gpt-4o", 100, 200, 150, True)

        stats = logger.get_specialist_stats("alpha")
        assert stats["total_requests"] == 1
        assert stats["total_tokens"] == 300
        assert stats["total_cost"] > 0
        assert stats["avg_latency_ms"] == 150.0
        assert stats["success_rate"] == 1.0
        assert stats["last_used"] is not None

    def test_multiple_entries(self, tmp_path):
        logger = UsageLogger(log_dir=str(tmp_path))
        logger.log("u@test.com", "alpha", "Alpha Bot", "openai", "gpt-4o", 100, 200, 100, True)
        logger.log("u@test.com", "alpha", "Alpha Bot", "openai", "gpt-4o", 50, 100, 200, True)
        logger.log("u@test.com", "alpha", "Alpha Bot", "openai", "gpt-4o", 0, 0, 50, False)

        stats = logger.get_specialist_stats("alpha")
        assert stats["total_requests"] == 3
        assert stats["total_tokens"] == 450
        assert stats["avg_latency_ms"] == pytest.approx(116.67, abs=1)
        assert stats["success_rate"] == pytest.approx(2 / 3, abs=0.01)

    def test_filters_by_specialist(self, tmp_path):
        logger = UsageLogger(log_dir=str(tmp_path))
        logger.log("u@test.com", "alpha", "Alpha Bot", "openai", "gpt-4o", 100, 200, 100, True)
        logger.log("u@test.com", "beta", "Beta Bot", "anthropic", "claude-3-sonnet", 50, 100, 200, True)

        alpha_stats = logger.get_specialist_stats("alpha")
        beta_stats = logger.get_specialist_stats("beta")
        assert alpha_stats["total_requests"] == 1
        assert beta_stats["total_requests"] == 1

    def test_nonexistent_specialist(self, tmp_path):
        logger = UsageLogger(log_dir=str(tmp_path))
        logger.log("u@test.com", "alpha", "Alpha Bot", "openai", "gpt-4o", 100, 200, 100, True)
        stats = logger.get_specialist_stats("nonexistent")
        assert stats["total_requests"] == 0

    def test_empty_log_dir(self, tmp_path):
        """A valid but empty log directory returns zero stats."""
        empty_dir = tmp_path / "empty_logs"
        empty_dir.mkdir()
        logger = UsageLogger(log_dir=str(empty_dir))
        stats = logger.get_specialist_stats("alpha")
        assert stats["total_requests"] == 0
