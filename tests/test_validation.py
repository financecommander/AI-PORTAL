"""Tests for specialist validation logic."""

import json

import pytest

from specialists.manager import Specialist, SpecialistManager


@pytest.fixture
def tmp_specialists_file(tmp_path):
    filepath = tmp_path / "specialists.json"
    initial = {
        "specialists": [
            {
                "id": "existing",
                "name": "Existing Specialist",
                "description": "Already there",
                "provider": "openai",
                "model": "gpt-4o",
                "system_prompt": "You are helpful.",
                "temperature": 0.7,
                "max_tokens": 2048,
                "pricing": {"input_per_1m": 0, "output_per_1m": 0},
                "created_at": "2026-01-01T00:00:00+00:00",
                "updated_at": "2026-01-01T00:00:00+00:00",
                "version": 1,
                "prompt_history": [],
            }
        ]
    }
    filepath.write_text(json.dumps(initial))
    return str(filepath)


@pytest.fixture
def manager(tmp_specialists_file):
    return SpecialistManager(filepath=tmp_specialists_file)


class TestValidateSpecialist:
    def test_valid_specialist(self, manager):
        errors = manager.validate_specialist(
            name="New Bot",
            provider="openai",
            model="gpt-4o",
            system_prompt="Be helpful.",
        )
        assert errors == []

    def test_empty_name(self, manager):
        errors = manager.validate_specialist(
            name="", provider="openai", model="gpt-4o",
            system_prompt="Be helpful.",
        )
        assert any("Name is required" in e for e in errors)

    def test_whitespace_only_name(self, manager):
        errors = manager.validate_specialist(
            name="   ", provider="openai", model="gpt-4o",
            system_prompt="Be helpful.",
        )
        assert any("Name is required" in e for e in errors)

    def test_name_too_long(self, manager):
        errors = manager.validate_specialist(
            name="A" * 101, provider="openai", model="gpt-4o",
            system_prompt="Be helpful.",
        )
        assert any("100 characters" in e for e in errors)

    def test_duplicate_name(self, manager):
        errors = manager.validate_specialist(
            name="Existing Specialist", provider="openai",
            model="gpt-4o", system_prompt="Be helpful.",
        )
        assert any("already exists" in e for e in errors)

    def test_duplicate_name_excluded_for_self(self, manager):
        """When editing, the specialist's own name should not conflict."""
        errors = manager.validate_specialist(
            name="Existing Specialist", provider="openai",
            model="gpt-4o", system_prompt="Be helpful.",
            exclude_id="existing",
        )
        assert errors == []

    def test_invalid_provider(self, manager):
        errors = manager.validate_specialist(
            name="Bot", provider="invalid", model="m",
            system_prompt="Prompt",
        )
        assert any("Provider must be one of" in e for e in errors)

    def test_valid_providers(self, manager):
        for prov in ("openai", "anthropic", "google"):
            errors = manager.validate_specialist(
                name=f"Bot_{prov}", provider=prov, model="m",
                system_prompt="Prompt",
            )
            assert not any("Provider" in e for e in errors)

    def test_empty_model(self, manager):
        errors = manager.validate_specialist(
            name="Bot", provider="openai", model="",
            system_prompt="Prompt",
        )
        assert any("Model is required" in e for e in errors)

    def test_empty_system_prompt(self, manager):
        errors = manager.validate_specialist(
            name="Bot", provider="openai", model="gpt-4o",
            system_prompt="",
        )
        assert any("System prompt is required" in e for e in errors)

    def test_system_prompt_too_long(self, manager):
        errors = manager.validate_specialist(
            name="Bot", provider="openai", model="gpt-4o",
            system_prompt="X" * 4001,
        )
        assert any("4000 characters" in e for e in errors)

    def test_description_too_long(self, manager):
        errors = manager.validate_specialist(
            name="Bot", provider="openai", model="gpt-4o",
            system_prompt="Prompt", description="D" * 501,
        )
        assert any("500 characters" in e for e in errors)

    def test_temperature_too_low(self, manager):
        errors = manager.validate_specialist(
            name="Bot", provider="openai", model="gpt-4o",
            system_prompt="Prompt", temperature=-0.1,
        )
        assert any("Temperature" in e for e in errors)

    def test_temperature_too_high(self, manager):
        errors = manager.validate_specialist(
            name="Bot", provider="openai", model="gpt-4o",
            system_prompt="Prompt", temperature=2.1,
        )
        assert any("Temperature" in e for e in errors)

    def test_temperature_boundaries(self, manager):
        for temp in (0.0, 1.0, 2.0):
            errors = manager.validate_specialist(
                name=f"Bot_{temp}", provider="openai", model="m",
                system_prompt="P", temperature=temp,
            )
            assert not any("Temperature" in e for e in errors)

    def test_max_tokens_too_low(self, manager):
        errors = manager.validate_specialist(
            name="Bot", provider="openai", model="gpt-4o",
            system_prompt="Prompt", max_tokens=100,
        )
        assert any("Max tokens" in e for e in errors)

    def test_max_tokens_too_high(self, manager):
        errors = manager.validate_specialist(
            name="Bot", provider="openai", model="gpt-4o",
            system_prompt="Prompt", max_tokens=10000,
        )
        assert any("Max tokens" in e for e in errors)

    def test_max_tokens_boundaries(self, manager):
        for mt in (256, 4096, 8192):
            errors = manager.validate_specialist(
                name=f"Bot_{mt}", provider="openai", model="m",
                system_prompt="P", max_tokens=mt,
            )
            assert not any("Max tokens" in e for e in errors)

    def test_base_url_must_be_https(self, manager):
        errors = manager.validate_specialist(
            name="Bot", provider="openai", model="gpt-4o",
            system_prompt="Prompt", base_url="http://example.com",
        )
        assert any("https://" in e for e in errors)

    def test_base_url_https_ok(self, manager):
        errors = manager.validate_specialist(
            name="Bot", provider="openai", model="gpt-4o",
            system_prompt="Prompt", base_url="https://api.example.com",
        )
        assert not any("https" in e for e in errors)

    def test_empty_base_url_ok(self, manager):
        errors = manager.validate_specialist(
            name="Bot", provider="openai", model="gpt-4o",
            system_prompt="Prompt", base_url="",
        )
        assert not any("https" in e for e in errors)

    def test_multiple_errors_at_once(self, manager):
        errors = manager.validate_specialist(
            name="", provider="invalid", model="",
            system_prompt="", temperature=5.0, max_tokens=1,
            base_url="http://bad",
        )
        assert len(errors) >= 6
