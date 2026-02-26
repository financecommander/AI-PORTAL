"""Tests for token estimator."""

import pytest
from backend.utils.token_estimator import (
    calculate_cost,
    estimate_tokens,
    get_model_pricing
)


def test_calculate_cost_known_model():
    """Test cost calculation for known models."""
    # GPT-4o: (2.50, 10.00) per 1M tokens
    cost = calculate_cost("gpt-4o", 1000, 500)
    expected = (1000 * 2.50 + 500 * 10.00) / 1_000_000
    assert cost == pytest.approx(expected)


def test_calculate_cost_unknown_model():
    """Test cost calculation for unknown models uses default pricing."""
    cost = calculate_cost("unknown-model", 1000, 500)
    expected = (1000 * 3.0 + 500 * 15.0) / 1_000_000
    assert cost == pytest.approx(expected)


def test_estimate_tokens():
    """Test token estimation (1 token ≈ 4 characters)."""
    text = "a" * 400
    tokens = estimate_tokens(text)
    assert tokens == 100


def test_get_model_pricing_exists():
    """Test getting pricing for existing model."""
    pricing = get_model_pricing("gpt-4o")
    assert pricing == (2.50, 10.00)


def test_get_model_pricing_not_exists():
    """Test getting pricing for non-existent model."""
    pricing = get_model_pricing("unknown-model")
    assert pricing is None
