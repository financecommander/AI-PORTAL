"""Tests for the aggregation synthesizer and _check_expansion fix (Bug #12)."""

import pytest
from backend.aggregation.lex_aggregation_config import (
    ConvergenceSynthesizer,
    AgentOutput,
    SynthesizedOutput,
    ContentType,
    PipelineAggMode,
)


def _make_agent(agent_id, blocks, constraints=None):
    """Helper to build an AgentOutput."""
    return AgentOutput(
        agent_id=agent_id,
        agent_name=f"Agent-{agent_id}",
        content_blocks=blocks,
        overall_confidence=0.8,
        binding_constraints=constraints or [],
    )


# ─── _check_expansion tests (Bug #12) ───

class TestCheckExpansion:
    """Test that _check_expansion correctly detects expansion."""

    def setup_method(self):
        self.synth = ConvergenceSynthesizer()

    def test_expansion_via_intersection_filtering(self):
        """Claims filtered > 0 means expansion occurred."""
        agents = [_make_agent(1, []), _make_agent(2, [])]
        result = SynthesizedOutput(
            sections=[{"claims_filtered": 2, "perspectives_combined": 0}],
            agents_contributing=[1, 2],
        )
        assert self.synth._check_expansion(agents, result) is True

    def test_expansion_via_multi_agent_perspectives(self):
        """Multiple perspectives combined in any section means expansion."""
        agents = [_make_agent(1, []), _make_agent(2, [])]
        result = SynthesizedOutput(
            sections=[{"claims_filtered": 0, "perspectives_combined": 3}],
            agents_contributing=[1, 2],
        )
        assert self.synth._check_expansion(agents, result) is True

    def test_expansion_via_regulatory_gates(self):
        """Regulatory flags present means expansion (gated addition worked)."""
        agents = [_make_agent(1, []), _make_agent(3, [], ["regulatory_flag"])]
        result = SynthesizedOutput(
            sections=[{
                "claims_filtered": 0,
                "perspectives_combined": 0,
                "regulatory_flags": ["regulatory_flag"],
            }],
            agents_contributing=[1, 3],
        )
        assert self.synth._check_expansion(agents, result) is True

    def test_no_expansion_when_nothing_happened(self):
        """No filtering, no multi-agent, no gates = no expansion."""
        agents = [_make_agent(1, [])]
        result = SynthesizedOutput(
            sections=[{"claims_filtered": 0, "perspectives_combined": 1}],
            agents_contributing=[1],
        )
        assert self.synth._check_expansion(agents, result) is False

    def test_no_expansion_with_empty_sections(self):
        """Empty sections list = no expansion."""
        agents = [_make_agent(1, [])]
        result = SynthesizedOutput(sections=[], agents_contributing=[1])
        assert self.synth._check_expansion(agents, result) is False

    def test_expansion_single_perspective_is_not_expansion(self):
        """perspectives_combined == 1 is NOT expansion (only one agent)."""
        agents = [_make_agent(1, [])]
        result = SynthesizedOutput(
            sections=[{"claims_filtered": 0, "perspectives_combined": 1}],
            agents_contributing=[1],
        )
        assert self.synth._check_expansion(agents, result) is False


# ─── Full synthesize() integration tests ───

class TestSynthesizeIntegration:
    """Test synthesize() with realistic AgentOutput objects."""

    def setup_method(self):
        self.synth = ConvergenceSynthesizer()

    def test_synthesize_with_matching_factual_claims(self):
        """Two agents with the same claim → claim is kept (intersection)."""
        agents = [
            _make_agent(1, [{
                "type": ContentType.FACTUAL_CLAIM,
                "content": "The Dodd-Frank Act was signed in 2010",
                "confidence": 0.9,
            }]),
            _make_agent(2, [{
                "type": ContentType.FACTUAL_CLAIM,
                "content": "The Dodd-Frank Act was signed in 2010",
                "confidence": 0.85,
            }]),
        ]

        result = self.synth.synthesize(agents)

        # The confirmed claim should appear
        factual_sections = [
            s for s in result.sections
            if s.get("type") == ContentType.FACTUAL_CLAIM
        ]
        assert len(factual_sections) == 1
        assert "Dodd-Frank" in factual_sections[0]["content"]
        # Both agents confirmed it
        assert set(factual_sections[0]["sources"]) == {1, 2}
        # 0 claims filtered (both agreed)
        assert factual_sections[0]["claims_filtered"] == 0

    def test_synthesize_filters_unconfirmed_claims(self):
        """Claims only from one agent are filtered out (intersection)."""
        agents = [
            _make_agent(1, [{
                "type": ContentType.FACTUAL_CLAIM,
                "content": "The statute was enacted in 2015",
                "confidence": 0.8,
            }]),
            _make_agent(2, [{
                "type": ContentType.FACTUAL_CLAIM,
                "content": "Revenue grew 20% in Q4",
                "confidence": 0.8,
            }]),
        ]

        result = self.synth.synthesize(agents)
        factual = [s for s in result.sections if s.get("type") == ContentType.FACTUAL_CLAIM]
        assert len(factual) == 1
        # Both claims are unconfirmed (no overlap) → both filtered
        assert factual[0]["claims_filtered"] == 2
        assert factual[0]["content"] == ""  # No confirmed claims

    def test_synthesize_addition_combines_analysis(self):
        """Analysis blocks from multiple agents are combined (addition)."""
        agents = [
            _make_agent(1, [{
                "type": ContentType.ANALYSIS,
                "content": "Market trends indicate growth",
                "confidence": 0.8,
            }]),
            _make_agent(2, [{
                "type": ContentType.ANALYSIS,
                "content": "Financial indicators are positive",
                "confidence": 0.7,
            }]),
        ]

        result = self.synth.synthesize(agents)
        analysis = [s for s in result.sections if s.get("type") == ContentType.ANALYSIS]
        assert len(analysis) == 1
        assert analysis[0]["perspectives_combined"] == 2
        assert "Market trends" in analysis[0]["content"]
        assert "Financial indicators" in analysis[0]["content"]

    def test_synthesize_gated_addition_with_regulatory_flag(self):
        """Gated addition reduces confidence when regulatory flags present."""
        agents = [
            _make_agent(1, [{
                "type": ContentType.RECOMMENDATION,
                "content": "Proceed with the merger",
                "confidence": 0.8,
            }]),
            _make_agent(3, [{
                "type": ContentType.RECOMMENDATION,
                "content": "File SEC disclosure first",
                "confidence": 0.7,
            }], constraints=["regulatory_flag"]),
        ]

        result = self.synth.synthesize(agents)
        recs = [s for s in result.sections if s.get("type") == ContentType.RECOMMENDATION]
        assert len(recs) == 1
        assert "regulatory_flags" in recs[0]
        assert recs[0]["mode_used"] == PipelineAggMode.GATED_ADDITION

    def test_synthesize_expansion_achieved_with_multi_agent(self):
        """Expansion is detected when multiple agents contribute analysis."""
        agents = [
            _make_agent(1, [{
                "type": ContentType.ANALYSIS,
                "content": "Perspective A",
                "confidence": 0.8,
            }]),
            _make_agent(2, [{
                "type": ContentType.ANALYSIS,
                "content": "Perspective B",
                "confidence": 0.7,
            }]),
        ]

        result = self.synth.synthesize(agents)
        assert result.expansion_achieved is True

    def test_synthesize_no_expansion_single_agent(self):
        """No expansion with only one agent."""
        agents = [
            _make_agent(1, [{
                "type": ContentType.ANALYSIS,
                "content": "Solo perspective",
                "confidence": 0.8,
            }]),
        ]

        result = self.synth.synthesize(agents)
        assert result.expansion_achieved is False

    def test_synthesize_agents_contributing_tracked(self):
        """agents_contributing lists all input agent IDs."""
        agents = [
            _make_agent(1, []),
            _make_agent(2, []),
            _make_agent(4, []),
        ]

        result = self.synth.synthesize(agents)
        assert set(result.agents_contributing) == {1, 2, 4}

    def test_synthesize_mechanism_log_populated(self):
        """mechanism_log records which aggregation mode was used."""
        agents = [
            _make_agent(1, [{
                "type": ContentType.FACTUAL_CLAIM,
                "content": "Fact A",
                "confidence": 0.8,
            }]),
            _make_agent(2, [{
                "type": ContentType.ANALYSIS,
                "content": "Analysis A",
                "confidence": 0.8,
            }]),
        ]

        result = self.synth.synthesize(agents)
        assert any("INTERSECT" in log for log in result.mechanism_log)
        assert any("ADD" in log for log in result.mechanism_log)


# ─── Agent weight tests ───

class TestAgentWeights:
    """Test that agent weights are correctly applied."""

    def test_default_weights_sum_to_0_90(self):
        """Default weights for agents 1-4 sum to 0.90 (leaving 0.10 headroom)."""
        synth = ConvergenceSynthesizer()
        total = sum(synth.agent_weights.values())
        assert abs(total - 0.90) < 0.01

    def test_custom_weights_override(self):
        """Custom weights are used when provided."""
        custom = {1: 0.5, 2: 0.5}
        synth = ConvergenceSynthesizer(agent_weights=custom)
        assert synth.agent_weights == custom

    def test_unknown_agent_gets_low_weight(self):
        """Agent not in weights dict gets fallback 0.1."""
        synth = ConvergenceSynthesizer()
        agents = [
            _make_agent(99, [{
                "type": ContentType.ANALYSIS,
                "content": "Unknown agent perspective",
                "confidence": 0.8,
            }]),
        ]
        result = synth.synthesize(agents)
        # Should still work — unknown agent uses weight 0.1
        assert len(result.sections) == 1
