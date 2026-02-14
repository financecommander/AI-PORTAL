"""Performance benchmarks for critical paths.

Run with: python -m pytest tests/performance/ -v --tb=short
These tests assert that operations complete within reasonable time bounds.
"""

from __future__ import annotations

import asyncio
import json
import time

import pytest

from chat.engine import ChatEngine
from chat.file_handler import ChatAttachment, process_upload
from chat.search import search_history
from specialists.manager import SpecialistManager


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class FakeUpload:
    def __init__(self, name: str, content: bytes, ftype: str = "text/plain"):
        self.name = name
        self.type = ftype
        self._content = content

    def read(self):
        return self._content


def _large_history(n: int) -> list[dict]:
    """Generate a history with *n* user/assistant pairs."""
    history = []
    for i in range(n):
        history.append({"role": "user", "content": f"Question {i}: What about topic {i}?"})
        history.append(
            {"role": "assistant", "content": f"Answer {i}: Here is the explanation for topic {i}."}
        )
    return history


# ---------------------------------------------------------------------------
# Benchmarks
# ---------------------------------------------------------------------------


class TestSearchPerformance:
    """search_history must stay fast even with large histories."""

    def test_search_1000_messages_under_50ms(self):
        history = _large_history(500)  # 1000 messages
        start = time.perf_counter()
        results = search_history(history, "topic 42")
        elapsed = (time.perf_counter() - start) * 1000
        assert elapsed < 50, f"Search took {elapsed:.1f}ms (limit 50ms)"
        assert len(results) >= 2  # user + assistant for topic 42

    def test_search_5000_messages_under_200ms(self):
        history = _large_history(2500)  # 5000 messages
        start = time.perf_counter()
        results = search_history(history, "topic 999")
        elapsed = (time.perf_counter() - start) * 1000
        assert elapsed < 200, f"Search took {elapsed:.1f}ms (limit 200ms)"

    def test_search_no_match_fast(self):
        history = _large_history(1000)
        start = time.perf_counter()
        results = search_history(history, "xyznonexistent")
        elapsed = (time.perf_counter() - start) * 1000
        assert elapsed < 50, f"No-match search took {elapsed:.1f}ms (limit 50ms)"
        assert len(results) == 0


class TestFileProcessingPerformance:
    """File uploads should process quickly."""

    def test_1mb_text_under_100ms(self):
        content = b"x" * (1024 * 1024)
        upload = FakeUpload("big.txt", content)
        start = time.perf_counter()
        attachment = process_upload(upload)
        elapsed = (time.perf_counter() - start) * 1000
        assert elapsed < 100, f"1MB text took {elapsed:.1f}ms (limit 100ms)"
        assert attachment.text_content is not None

    def test_5mb_text_under_500ms(self):
        content = b"row," * (1024 * 1024)  # ~4MB
        upload = FakeUpload("data.csv", content, "text/csv")
        start = time.perf_counter()
        attachment = process_upload(upload)
        elapsed = (time.perf_counter() - start) * 1000
        assert elapsed < 500, f"~4MB CSV took {elapsed:.1f}ms (limit 500ms)"


class TestSpecialistManagerPerformance:
    """Specialist CRUD operations must stay snappy."""

    def test_load_100_specialists_under_100ms(self, tmp_path):
        specialists = {
            "specialists": [
                {
                    "id": f"spec_{i}",
                    "name": f"Specialist {i}",
                    "description": f"Desc {i}",
                    "provider": "openai",
                    "model": "gpt-4o",
                    "system_prompt": f"You are specialist {i}.",
                    "temperature": 0.5,
                    "max_tokens": 2048,
                    "pricing": {"input_per_1m": 2.50, "output_per_1m": 10.00},
                    "created_at": "2026-01-01T00:00:00+00:00",
                    "updated_at": "2026-01-01T00:00:00+00:00",
                    "version": 1,
                    "prompt_history": [],
                }
                for i in range(100)
            ]
        }
        filepath = tmp_path / "specs.json"
        filepath.write_text(json.dumps(specialists))

        start = time.perf_counter()
        mgr = SpecialistManager(filepath=str(filepath))
        elapsed = (time.perf_counter() - start) * 1000
        assert elapsed < 100, f"Load 100 specialists took {elapsed:.1f}ms (limit 100ms)"
        assert len(mgr.list()) == 100

    def test_list_sorted_100_under_10ms(self, tmp_path):
        specialists = {
            "specialists": [
                {
                    "id": f"spec_{i}",
                    "name": f"Specialist {i:03d}",
                    "description": f"Desc {i}",
                    "provider": "openai",
                    "model": "gpt-4o",
                    "system_prompt": f"Prompt {i}",
                    "temperature": 0.5,
                    "max_tokens": 2048,
                    "pricing": {"input_per_1m": 2.50, "output_per_1m": 10.00},
                    "created_at": "2026-01-01T00:00:00+00:00",
                    "updated_at": "2026-01-01T00:00:00+00:00",
                    "version": 1,
                    "prompt_history": [],
                }
                for i in range(100)
            ]
        }
        filepath = tmp_path / "specs.json"
        filepath.write_text(json.dumps(specialists))
        mgr = SpecialistManager(filepath=str(filepath))

        pinned = {f"spec_{i}" for i in range(10)}
        start = time.perf_counter()
        sorted_list = mgr.list_sorted(pinned=pinned)
        elapsed = (time.perf_counter() - start) * 1000
        assert elapsed < 10, f"list_sorted took {elapsed:.1f}ms (limit 10ms)"
        assert len(sorted_list) == 100


class TestChatEnginePerformance:
    """ChatEngine operations with StubProvider should be near-instant."""

    def test_50_turn_conversation_under_100ms(self, stub_provider, specialist_manager):
        specialist = specialist_manager.get("fin_analyst")
        engine = ChatEngine(provider=stub_provider, specialist=specialist)

        async def run_turns():
            for i in range(50):
                await engine.send(f"Turn {i}")

        start = time.perf_counter()
        asyncio.run(run_turns())
        elapsed = (time.perf_counter() - start) * 1000
        assert elapsed < 100, f"50 turns took {elapsed:.1f}ms (limit 100ms)"
        # system + 50*(user + assistant) = 101
        assert len(engine.get_history()) == 101

    def test_reset_clears_instantly(self, stub_provider, specialist_manager):
        specialist = specialist_manager.get("fin_analyst")
        engine = ChatEngine(provider=stub_provider, specialist=specialist)

        async def run_turns():
            for i in range(20):
                await engine.send(f"Turn {i}")

        asyncio.run(run_turns())

        start = time.perf_counter()
        engine.reset()
        elapsed = (time.perf_counter() - start) * 1000
        assert elapsed < 1, f"Reset took {elapsed:.1f}ms (limit 1ms)"
        assert len(engine.get_history()) == 1  # only system prompt
