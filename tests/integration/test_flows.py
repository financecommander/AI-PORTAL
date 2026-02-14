"""Integration tests exercising multi-component workflows.

These tests wire together real (non-mocked) objects across module
boundaries to verify end-to-end behaviour.  External API calls are
avoided by using the StubProvider from conftest.
"""

from __future__ import annotations

import asyncio
import base64
import json

import pytest

from chat.engine import ChatEngine
from chat.file_handler import ChatAttachment, process_upload
from chat.logger import UsageLogger
from chat.search import search_history
from specialists.manager import SpecialistManager


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class FakeUpload:
    """Minimal file-like object mimicking Streamlit UploadedFile."""

    def __init__(self, name: str, content: bytes, ftype: str = "text/plain"):
        self.name = name
        self.type = ftype
        self._content = content

    def read(self):
        return self._content


# ---------------------------------------------------------------------------
# Chat flow integration
# ---------------------------------------------------------------------------


class TestChatFlowIntegration:
    """Combines ChatEngine + StubProvider + UsageLogger + Specialist."""

    def test_full_send_and_log(self, specialist_manager, log_dir, stub_provider):
        specialist = specialist_manager.get("fin_analyst")
        logger = UsageLogger(log_dir=log_dir)
        engine = ChatEngine(
            provider=stub_provider,
            specialist=specialist,
            logger=logger,
            user_email="test@dev.com",
        )

        reply = asyncio.run(engine.send("Hi"))
        assert reply == "stub response"

        # History should have system + user + assistant
        history = engine.get_history()
        assert len(history) == 3
        assert history[0]["role"] == "system"
        assert history[1]["role"] == "user"
        assert history[2]["role"] == "assistant"

        # Logger should have recorded the request
        stats = logger.get_specialist_stats("fin_analyst")
        assert stats["total_requests"] == 1
        assert stats["success_rate"] == 1.0

    def test_multi_turn_conversation(self, specialist_manager, log_dir, stub_provider):
        specialist = specialist_manager.get("fin_analyst")
        logger = UsageLogger(log_dir=log_dir)
        engine = ChatEngine(
            provider=stub_provider,
            specialist=specialist,
            logger=logger,
            user_email="test@dev.com",
        )

        async def two_turns():
            await engine.send("Turn 1")
            await engine.send("Turn 2")

        asyncio.run(two_turns())

        history = engine.get_history()
        # system + (user + assistant) * 2
        assert len(history) == 5

        stats = logger.get_specialist_stats("fin_analyst")
        assert stats["total_requests"] == 2

    def test_switch_specialist_resets(self, specialist_manager, stub_provider):
        engine = ChatEngine(
            provider=stub_provider,
            specialist=specialist_manager.get("fin_analyst"),
        )

        asyncio.run(engine.send("Hello"))
        assert len(engine.get_history()) == 3  # system + user + assistant

        engine.set_specialist(specialist_manager.get("code_helper"))
        # After switching, only the new system prompt should remain
        assert len(engine.get_history()) == 1
        assert engine.get_history()[0]["content"] == "You are a coding assistant."


# ---------------------------------------------------------------------------
# Streaming flow integration
# ---------------------------------------------------------------------------


class TestStreamingFlowIntegration:
    """Combines ChatEngine.send_streaming + StubProvider + Logger."""

    def test_streaming_collects_full_response(
        self, specialist_manager, log_dir, stub_provider
    ):
        specialist = specialist_manager.get("fin_analyst")
        logger = UsageLogger(log_dir=log_dir)
        engine = ChatEngine(
            provider=stub_provider,
            specialist=specialist,
            logger=logger,
            user_email="test@dev.com",
        )

        chunks = []

        async def collect():
            async for chunk in engine.send_streaming("Summarize"):
                chunks.append(chunk)

        asyncio.run(collect())

        assert len(chunks) >= 1
        assert chunks[-1].is_final is True

        # Reconstruct full text
        full_text = "".join(c.content for c in chunks)
        assert "stub" in full_text

        # Append to history manually (as the UI would)
        engine.append_assistant_message(full_text)
        assert len(engine.get_history()) == 3  # system + user + assistant


# ---------------------------------------------------------------------------
# File upload flow integration
# ---------------------------------------------------------------------------


class TestFileUploadFlowIntegration:
    """Combines file_handler.process_upload + provider.format_attachment."""

    def test_text_file_round_trip(self, stub_provider):
        upload = FakeUpload("notes.txt", b"Meeting notes for Q4.")
        attachment = process_upload(upload)

        assert attachment.text_content == "Meeting notes for Q4."
        assert attachment.filename == "notes.txt"

        # Format for provider
        block = stub_provider.format_attachment(attachment)
        assert block["type"] == "text"
        assert "Meeting notes for Q4." in block["text"]

    def test_csv_file_processes(self, stub_provider):
        csv_data = b"date,amount\n2026-01-01,100.00\n2026-01-02,200.00"
        upload = FakeUpload("data.csv", csv_data, "text/csv")
        attachment = process_upload(upload)

        assert "date,amount" in attachment.text_content
        block = stub_provider.format_attachment(attachment)
        assert block["type"] == "text"

    def test_image_file_binary(self, stub_provider):
        upload = FakeUpload("chart.png", b"\x89PNG fake", "image/png")
        attachment = process_upload(upload)
        assert attachment.text_content is None

        # Stub provider uses base text fallback
        block = stub_provider.format_attachment(attachment)
        assert block["type"] == "text"
        assert "bytes" in block["text"]

    def test_json_file_content(self, stub_provider):
        data = json.dumps({"key": "value"}).encode()
        upload = FakeUpload("config.json", data, "application/json")
        attachment = process_upload(upload)
        assert '"key"' in attachment.text_content


# ---------------------------------------------------------------------------
# Specialist CRUD flow integration
# ---------------------------------------------------------------------------


class TestSpecialistCRUDFlowIntegration:
    """Tests create → update → duplicate → delete → verify persistence."""

    def test_full_crud_lifecycle(self, specialists_file):
        mgr = SpecialistManager(filepath=specialists_file)
        assert len(mgr.list()) == 2

        # Create
        new_spec = mgr.create(
            name="Tax Advisor",
            description="Tax help",
            provider="openai",
            model="gpt-4o-mini",
            system_prompt="You are a tax advisor.",
        )
        assert len(mgr.list()) == 3

        # Update
        updated = mgr.update(new_spec.id, system_prompt="You are an expert tax advisor.")
        assert updated.system_prompt == "You are an expert tax advisor."
        assert updated.version == 2

        # Duplicate
        clone = mgr.duplicate(new_spec.id)
        assert clone.name == "Tax Advisor (Copy)"
        assert len(mgr.list()) == 4

        # Delete original
        assert mgr.delete(new_spec.id) is True
        assert len(mgr.list()) == 3
        assert mgr.get(new_spec.id) is None
        # Clone still exists
        assert mgr.get(clone.id) is not None

        # Persistence check
        mgr2 = SpecialistManager(filepath=specialists_file)
        assert len(mgr2.list()) == 3
        assert mgr2.get(clone.id).name == "Tax Advisor (Copy)"

    def test_pinning_integration(self, specialists_file):
        mgr = SpecialistManager(filepath=specialists_file)
        pinned: set[str] = set()

        # Pin code_helper
        SpecialistManager.toggle_pin("code_helper", pinned)

        sorted_list = mgr.list_sorted(pinned=pinned)
        # Code Helper should be first (pinned)
        assert sorted_list[0].id == "code_helper"
        assert sorted_list[1].id == "fin_analyst"


# ---------------------------------------------------------------------------
# Search + chat history integration
# ---------------------------------------------------------------------------


class TestSearchIntegration:
    """Combines ChatEngine history with search_history()."""

    def test_search_engine_history(self, specialist_manager, stub_provider):
        engine = ChatEngine(
            provider=stub_provider,
            specialist=specialist_manager.get("fin_analyst"),
        )

        async def two_sends():
            await engine.send("What is the P/E ratio?")
            await engine.send("Explain EBITDA")

        asyncio.run(two_sends())

        history = engine.get_history()
        results = search_history(history, "stub")
        # Both assistant replies contain "stub response"
        assert len(results) >= 2
        for r in results:
            assert r["role"] == "assistant"

    def test_search_user_messages(self, specialist_manager, stub_provider):
        engine = ChatEngine(
            provider=stub_provider,
            specialist=specialist_manager.get("fin_analyst"),
        )

        asyncio.run(engine.send("What is ROI?"))

        history = engine.get_history()
        results = search_history(history, "ROI")
        assert len(results) == 1
        assert results[0]["role"] == "user"
