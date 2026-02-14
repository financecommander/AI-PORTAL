"""Tests for the specialists manager module."""

import json

import pytest

from specialists.manager import Pricing, Specialist, SpecialistManager


@pytest.fixture
def tmp_specialists_file(tmp_path):
    """Provide a temporary specialists JSON file."""
    filepath = tmp_path / "specialists.json"
    initial = {
        "specialists": [
            {
                "id": "test-1",
                "name": "Test Specialist",
                "description": "A test specialist",
                "provider": "openai",
                "model": "gpt-4o",
                "system_prompt": "You are a test assistant.",
                "temperature": 0.5,
                "max_tokens": 2048,
                "pricing": {"input_per_1m": 2.50, "output_per_1m": 10.00},
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


class TestPricing:
    def test_defaults(self):
        p = Pricing()
        assert p.input_per_1m == 0.0
        assert p.output_per_1m == 0.0

    def test_custom_values(self):
        p = Pricing(input_per_1m=2.50, output_per_1m=10.00)
        assert p.input_per_1m == 2.50
        assert p.output_per_1m == 10.00


class TestSpecialist:
    def test_defaults(self):
        s = Specialist()
        assert len(s.id) == 36  # UUID v4 format
        assert s.name == "New Specialist"
        assert s.description == ""
        assert s.provider == "openai"
        assert s.model == "gpt-4o"
        assert s.temperature == 0.7
        assert s.max_tokens == 4096
        assert isinstance(s.pricing, Pricing)
        assert s.version == 1
        assert s.prompt_history == []
        assert s.created_at is not None
        assert s.updated_at is not None

    def test_custom_values(self):
        s = Specialist(
            id="custom-id",
            name="Financial Analyst",
            description="Analyzes financial data and trends",
            provider="openai",
            model="gpt-4o",
            system_prompt="You are a financial analyst.",
            temperature=0.3,
            max_tokens=2048,
            pricing=Pricing(input_per_1m=2.50, output_per_1m=10.00),
        )
        assert s.id == "custom-id"
        assert s.name == "Financial Analyst"
        assert s.description == "Analyzes financial data and trends"
        assert s.provider == "openai"
        assert s.temperature == 0.3
        assert s.max_tokens == 2048
        assert s.pricing.input_per_1m == 2.50
        assert s.pricing.output_per_1m == 10.00

    def test_pricing_from_dict(self):
        s = Specialist(pricing={"input_per_1m": 2.50, "output_per_1m": 10.00})
        assert isinstance(s.pricing, Pricing)
        assert s.pricing.input_per_1m == 2.50


class TestSpecialistManager:
    def test_list(self, manager):
        specs = manager.list()
        assert len(specs) == 1
        assert specs[0].id == "test-1"

    def test_get_existing(self, manager):
        spec = manager.get("test-1")
        assert spec is not None
        assert spec.name == "Test Specialist"
        assert spec.description == "A test specialist"
        assert spec.provider == "openai"
        assert spec.max_tokens == 2048
        assert isinstance(spec.pricing, Pricing)
        assert spec.pricing.input_per_1m == 2.50

    def test_get_missing(self, manager):
        assert manager.get("nonexistent") is None

    def test_create(self, manager):
        spec = manager.create(
            id="test-2",
            name="New Spec",
            description="A new specialist",
            system_prompt="Hello",
        )
        assert spec.id == "test-2"
        assert spec.description == "A new specialist"
        assert len(manager.list()) == 2

    def test_update(self, manager):
        updated = manager.update("test-1", name="Updated Name")
        assert updated is not None
        assert updated.name == "Updated Name"
        assert updated.version == 2
        assert manager.get("test-1").name == "Updated Name"

    def test_update_prompt_tracks_history(self, manager):
        updated = manager.update("test-1", system_prompt="New prompt")
        assert updated is not None
        assert updated.system_prompt == "New prompt"
        assert len(updated.prompt_history) == 1
        assert updated.prompt_history[0]["prompt"] == "You are a test assistant."
        assert updated.prompt_history[0]["version"] == 1

    def test_update_missing(self, manager):
        assert manager.update("nonexistent", name="X") is None

    def test_update_invalid_attribute(self, manager):
        with pytest.raises(AttributeError):
            manager.update("test-1", nonexistent_field="X")

    def test_delete(self, manager):
        assert manager.delete("test-1") is True
        assert len(manager.list()) == 0

    def test_delete_missing(self, manager):
        assert manager.delete("nonexistent") is False

    def test_persistence(self, tmp_specialists_file):
        mgr1 = SpecialistManager(filepath=tmp_specialists_file)
        mgr1.create(id="persisted", name="Persisted Specialist")

        mgr2 = SpecialistManager(filepath=tmp_specialists_file)
        assert mgr2.get("persisted") is not None

    def test_load_empty_file(self, tmp_path):
        filepath = tmp_path / "empty.json"
        mgr = SpecialistManager(filepath=str(filepath))
        assert mgr.list() == []

    def test_load_financial_analyst_config(self):
        """Verify the bundled specialists.json loads correctly."""
        import os

        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "config",
            "specialists.json",
        )
        mgr = SpecialistManager(filepath=config_path)
        analyst = mgr.get("financial_analyst")
        assert analyst is not None
        assert analyst.name == "Financial Analyst"
        assert analyst.description == "Analyzes financial data and trends"
        assert analyst.provider == "openai"
        assert analyst.model == "gpt-4o"
        assert analyst.temperature == 0.3
        assert analyst.max_tokens == 2048
        assert analyst.pricing.input_per_1m == 2.50
        assert analyst.pricing.output_per_1m == 10.00
        assert analyst.version == 1
        assert analyst.prompt_history == []
