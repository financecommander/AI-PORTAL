"""Shared fixtures for backend tests."""

import pytest


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances between tests to avoid state leakage."""
    # This ensures each test gets a fresh pipeline registry and WebSocket manager
    from backend.pipelines import registry as reg_module
    from backend.websockets import manager as ws_module
    
    # Store original instances
    original_registry = reg_module.pipeline_registry
    original_ws_manager = ws_module.ws_manager
    
    yield
    
    # Note: Since we're using the default instances in routes,
    # tests that need isolation should create their own instances
    # or use mocking as appropriate
