"""
Tests for token counting and cost estimation.
"""
import pytest
from config.pricing import estimate_cost, MODEL_PRICING


class TestTokenEstimator:
    """Tests for token counting and cost calculation."""
    
    def test_estimate_cost_gpt4o(self):
        """Test cost estimation for GPT-4o."""
        cost = estimate_cost("gpt-4o", input_tokens=1_000_000, output_tokens=1_000_000)
        expected = 2.50 + 10.00  # $12.50
        assert cost == pytest.approx(expected, rel=1e-9)
    
    def test_estimate_cost_gpt4o_mini(self):
        """Test cost estimation for GPT-4o-mini."""
        cost = estimate_cost("gpt-4o-mini", input_tokens=1_000_000, output_tokens=1_000_000)
        expected = 0.15 + 0.60  # $0.75
        assert cost == pytest.approx(expected, rel=1e-9)
    
    def test_estimate_cost_claude_opus(self):
        """Test cost estimation for Claude Opus."""
        cost = estimate_cost("claude-opus-4-6", input_tokens=1_000_000, output_tokens=1_000_000)
        expected = 15.00 + 75.00  # $90.00
        assert cost == pytest.approx(expected, rel=1e-9)
    
    def test_estimate_cost_small_usage(self):
        """Test cost estimation for small token usage."""
        cost = estimate_cost("gpt-4o", input_tokens=1000, output_tokens=500)
        # (1000/1M * 2.50) + (500/1M * 10.00) = 0.0025 + 0.005 = 0.0075
        expected = 0.0075
        assert cost == pytest.approx(expected, rel=1e-9)
    
    def test_estimate_cost_unknown_model(self):
        """Test cost estimation for unknown model returns 0."""
        cost = estimate_cost("unknown-model", input_tokens=1000, output_tokens=500)
        assert cost == 0.0
    
    def test_estimate_cost_zero_tokens(self):
        """Test cost estimation with zero tokens."""
        cost = estimate_cost("gpt-4o", input_tokens=0, output_tokens=0)
        assert cost == 0.0
    
    def test_model_pricing_contains_all_major_models(self):
        """Test MODEL_PRICING contains major models."""
        required_models = [
            "gpt-4o",
            "gpt-4o-mini",
            "claude-opus-4-6",
            "claude-sonnet-4-5",
            "gemini-2.0-flash",
            "grok-3",
        ]
        
        for model in required_models:
            assert model in MODEL_PRICING, f"Model {model} not found in MODEL_PRICING"
    
    def test_pricing_format(self):
        """Test pricing format is (input_price, output_price) tuples."""
        for model, pricing in MODEL_PRICING.items():
            assert isinstance(pricing, tuple), f"Pricing for {model} is not a tuple"
            assert len(pricing) == 2, f"Pricing for {model} doesn't have exactly 2 values"
            assert all(isinstance(p, (int, float)) for p in pricing), \
                f"Pricing for {model} contains non-numeric values"
