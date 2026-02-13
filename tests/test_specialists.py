"""Tests for the specialists manager module."""

import json

import pytest

from specialists.manager import Specialist, SpecialistManager


@pytest.fixture
def tmp_specialists_file(tmp_path):
    """Provide a temporary specialists JSON file."""
    filepath = tmp_path / "specialists.json"
    initial = [
        {
            "id": "test-1",
            "name": "Test Specialist",
            "system_prompt": "You are a test assistant.",
            "model": "gpt-4o",
            "temperature": 0.5,
        }
    ]
    filepath.write_text(json.dumps(initial))
    return str(filepath)


@pytest.fixture
def manager(tmp_specialists_file):
    return SpecialistManager(filepath=tmp_specialists_file)


class TestSpecialistManager:
    def test_list(self, manager):
        specs = manager.list()
        assert len(specs) == 1
        assert specs[0].id == "test-1"

    def test_get_existing(self, manager):
        spec = manager.get("test-1")
        assert spec is not None
        assert spec.name == "Test Specialist"

    def test_get_missing(self, manager):
        assert manager.get("nonexistent") is None

    def test_create(self, manager):
        spec = manager.create(
            id="test-2", name="New Spec", system_prompt="Hello"
        )
        assert spec.id == "test-2"
        assert len(manager.list()) == 2

    def test_update(self, manager):
        updated = manager.update("test-1", name="Updated Name")
        assert updated is not None
        assert updated.name == "Updated Name"
        assert manager.get("test-1").name == "Updated Name"

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
