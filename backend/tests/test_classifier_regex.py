"""Tests for the content classifier regex (Bug #11 fix)."""

import pytest
from backend.pipelines.lex_pipeline import classify_content, _detect_header
from backend.aggregation.lex_aggregation_config import ContentType, AgentOutput


# ─── _detect_header unit tests ───

class TestDetectHeader:
    """Test regex-based header detection."""

    # Positive matches — should detect headers
    def test_plain_factual_claims(self):
        assert _detect_header("FACTUAL CLAIMS") == ContentType.FACTUAL_CLAIM

    def test_factual_claim_singular(self):
        assert _detect_header("FACTUAL CLAIM") == ContentType.FACTUAL_CLAIM

    def test_factual_claims_with_colon(self):
        assert _detect_header("FACTUAL CLAIMS:") == ContentType.FACTUAL_CLAIM

    def test_markdown_bold_factual(self):
        assert _detect_header("**FACTUAL CLAIMS:**") == ContentType.FACTUAL_CLAIM

    def test_markdown_heading_factual(self):
        assert _detect_header("## FACTUAL CLAIMS") == ContentType.FACTUAL_CLAIM

    def test_analysis_header(self):
        assert _detect_header("ANALYSIS") == ContentType.ANALYSIS

    def test_analysis_markdown(self):
        assert _detect_header("## Analysis") == ContentType.ANALYSIS

    def test_recommendations_header(self):
        assert _detect_header("RECOMMENDATIONS") == ContentType.RECOMMENDATION

    def test_recommendation_singular(self):
        assert _detect_header("Recommendation") == ContentType.RECOMMENDATION

    def test_risk_assessment_header(self):
        assert _detect_header("RISK ASSESSMENT") == ContentType.RISK_ASSESSMENT

    def test_risk_assessments_plural(self):
        assert _detect_header("RISK ASSESSMENTS:") == ContentType.RISK_ASSESSMENT

    def test_contrarian_header(self):
        assert _detect_header("CONTRARIAN") == ContentType.CONTRARIAN_VIEW

    def test_alternative_strategy(self):
        assert _detect_header("ALTERNATIVE STRATEGY") == ContentType.CONTRARIAN_VIEW

    def test_alternative_view(self):
        assert _detect_header("Alternative View") == ContentType.CONTRARIAN_VIEW

    def test_alternative_perspective(self):
        assert _detect_header("Alternative Perspective") == ContentType.CONTRARIAN_VIEW

    def test_bullet_prefix(self):
        assert _detect_header("- ANALYSIS") == ContentType.ANALYSIS

    # Negative matches — should NOT detect headers (Bug #11 false positives)
    def test_natural_text_with_risk_word(self):
        """'risk' in normal prose should not trigger RISK_ASSESSMENT."""
        assert _detect_header("There is a risk of regulatory action") is None

    def test_natural_text_with_analysis_word(self):
        """'analysis' mid-sentence should not trigger ANALYSIS."""
        assert _detect_header("Our analysis shows growth") is None

    def test_natural_text_with_claim_word(self):
        """'claim' mid-sentence should not trigger FACTUAL_CLAIM."""
        assert _detect_header("They claim the market is up") is None

    def test_natural_text_with_recommend(self):
        """'recommend' mid-sentence should not trigger RECOMMENDATION."""
        assert _detect_header("We recommend caution here") is None

    def test_natural_text_with_alternative(self):
        """'alternative' alone mid-sentence should not trigger."""
        assert _detect_header("Consider an alternative approach") is None

    def test_empty_string(self):
        assert _detect_header("") is None

    def test_plain_text(self):
        assert _detect_header("The court ruled in favor of the defendant.") is None


# ─── classify_content integration tests ───

class TestClassifyContent:
    """Test full classify_content function."""

    def test_well_structured_response(self):
        """Response with clear section headers is properly classified."""
        raw = """FACTUAL CLAIMS
SEC Rule 10b-5 prohibits securities fraud.
The Dodd-Frank Act was signed in 2010.

ANALYSIS
The regulatory landscape has shifted significantly.
Market participants face increased compliance burden.

RECOMMENDATIONS
Engage external counsel for compliance review.
Update internal policies by Q3."""

        result = classify_content(1, "Lead Researcher", raw)
        assert isinstance(result, AgentOutput)
        assert result.agent_id == 1
        assert len(result.content_blocks) == 3

        types = [b["type"] for b in result.content_blocks]
        assert ContentType.FACTUAL_CLAIM in types
        assert ContentType.ANALYSIS in types
        assert ContentType.RECOMMENDATION in types

    def test_content_before_first_header_not_dropped(self):
        """Content before any header is classified as ANALYSIS (not dropped)."""
        raw = """This is some introductory context.
It provides background before the structured sections.

FACTUAL CLAIMS
The statute was enacted in 2015."""

        result = classify_content(1, "Test Agent", raw)
        assert len(result.content_blocks) >= 2

        # First block should be the intro content, classified as ANALYSIS
        first = result.content_blocks[0]
        assert first["type"] == ContentType.ANALYSIS
        assert "introductory context" in first["content"]

    def test_no_headers_at_all(self):
        """Response with no headers puts everything into a single ANALYSIS block."""
        raw = """The market showed strong growth in Q4.
Revenue increased by 15% year-over-year.
Regulatory compliance costs remained stable."""

        result = classify_content(2, "Financial Analyst", raw)
        assert len(result.content_blocks) == 1
        assert result.content_blocks[0]["type"] == ContentType.ANALYSIS

    def test_markdown_formatted_headers(self):
        """Markdown-style headers (**, ##) are recognized."""
        raw = """## FACTUAL CLAIMS
The law was passed in 2020.

**ANALYSIS:**
This represents a significant shift."""

        result = classify_content(1, "Test", raw)
        types = [b["type"] for b in result.content_blocks]
        assert ContentType.FACTUAL_CLAIM in types
        assert ContentType.ANALYSIS in types

    def test_agent_3_sets_regulatory_flag(self):
        """Agent 3 (Regulatory Scanner) sets binding_constraints on risk/violation."""
        raw = """RISK ASSESSMENT
There is a potential violation of Section 13(a).
The filing risk is substantial."""

        result = classify_content(3, "Regulatory Scanner", raw)
        assert "regulatory_flag" in result.binding_constraints

    def test_agent_3_no_flag_without_keywords(self):
        """Agent 3 without risk/violation keywords has no binding_constraints."""
        raw = """ANALYSIS
The market outlook is positive."""

        result = classify_content(3, "Regulatory Scanner", raw)
        assert result.binding_constraints == []

    def test_non_agent_3_never_sets_flag(self):
        """Non-regulatory agents never set binding_constraints."""
        raw = """There is a huge risk and potential violation here."""

        result = classify_content(1, "Lead Researcher", raw)
        assert result.binding_constraints == []

    def test_confidence_is_set(self):
        """All content blocks have confidence = 0.8."""
        raw = """ANALYSIS
Some content here."""

        result = classify_content(1, "Test", raw)
        for block in result.content_blocks:
            assert block["confidence"] == 0.8
