from decimal import Decimal

import pytest

from ledgerscript.grammar import (
    ComplianceFlag,
    ComplianceGate,
    ComplianceLedger,
    Jurisdiction,
    Money,
    Percentage,
    RegulationExemption,
    SecuritiesClassification,
    TokenStandard,
)


# ============================================================================
# Enum Tests
# ============================================================================

class TestJurisdiction:
    def test_values(self):
        assert Jurisdiction.US.value == "US"
        assert Jurisdiction.EU.value == "EU"
        assert Jurisdiction.CAYMAN.value == "KY"
        assert Jurisdiction.DELAWARE.value == "US-DE"


class TestSecuritiesClassification:
    def test_values(self):
        assert SecuritiesClassification.SECURITY.value == "security"
        assert SecuritiesClassification.UTILITY.value == "utility"
        assert SecuritiesClassification.HYBRID.value == "hybrid"
        assert SecuritiesClassification.UNKNOWN.value == "unknown"


class TestRegulationExemption:
    def test_values(self):
        assert RegulationExemption.REG_D_506B.value == "Reg D 506(b)"
        assert RegulationExemption.REG_D_506C.value == "Reg D 506(c)"
        assert RegulationExemption.REG_A_TIER1.value == "Reg A+ Tier 1"
        assert RegulationExemption.REG_A_TIER2.value == "Reg A+ Tier 2"
        assert RegulationExemption.REG_S.value == "Reg S"
        assert RegulationExemption.REG_CF.value == "Reg CF"


class TestTokenStandard:
    def test_values(self):
        assert TokenStandard.ERC20.value == "ERC-20"
        assert TokenStandard.ERC721.value == "ERC-721"
        assert TokenStandard.ERC1400.value == "ERC-1400"
        assert TokenStandard.SPL_TOKEN.value == "SPL Token"
        assert TokenStandard.CUSTOM.value == "Custom"


# ============================================================================
# Money Tests
# ============================================================================

class TestMoney:
    def test_construction(self):
        m = Money(Decimal("100.50"), "USD")
        assert m.amount == Decimal("100.50")
        assert m.currency == "USD"

    def test_default_currency(self):
        m = Money(Decimal("50"))
        assert m.currency == "USD"

    def test_add_same_currency(self):
        result = Money(Decimal("10"), "USD") + Money(Decimal("20"), "USD")
        assert result == Money(Decimal("30"), "USD")

    def test_add_different_currency_raises(self):
        with pytest.raises(ValueError, match="Cannot add"):
            Money(Decimal("10"), "USD") + Money(Decimal("20"), "EUR")

    def test_sub_same_currency(self):
        result = Money(Decimal("30"), "USD") - Money(Decimal("10"), "USD")
        assert result == Money(Decimal("20"), "USD")

    def test_sub_different_currency_raises(self):
        with pytest.raises(ValueError, match="Cannot subtract"):
            Money(Decimal("30"), "USD") - Money(Decimal("10"), "EUR")

    def test_mul(self):
        result = Money(Decimal("10"), "USD") * 3
        assert result == Money(Decimal("30"), "USD")

    def test_div(self):
        result = Money(Decimal("30"), "USD") / 3
        assert result == Money(Decimal("10"), "USD")

    def test_eq(self):
        assert Money(Decimal("10"), "USD") == Money(Decimal("10"), "USD")
        assert Money(Decimal("10"), "USD") != Money(Decimal("20"), "USD")
        assert Money(Decimal("10"), "USD") != Money(Decimal("10"), "EUR")

    def test_eq_non_money(self):
        assert Money(Decimal("10"), "USD").__eq__("not money") is NotImplemented

    def test_lt(self):
        assert Money(Decimal("10"), "USD") < Money(Decimal("20"), "USD")
        assert not Money(Decimal("20"), "USD") < Money(Decimal("10"), "USD")

    def test_le(self):
        assert Money(Decimal("10"), "USD") <= Money(Decimal("10"), "USD")
        assert Money(Decimal("10"), "USD") <= Money(Decimal("20"), "USD")

    def test_gt(self):
        assert Money(Decimal("20"), "USD") > Money(Decimal("10"), "USD")

    def test_ge(self):
        assert Money(Decimal("20"), "USD") >= Money(Decimal("20"), "USD")
        assert Money(Decimal("20"), "USD") >= Money(Decimal("10"), "USD")

    def test_comparison_different_currency_raises(self):
        with pytest.raises(ValueError, match="Cannot compare"):
            Money(Decimal("10"), "USD") < Money(Decimal("20"), "EUR")
        with pytest.raises(ValueError, match="Cannot compare"):
            Money(Decimal("10"), "USD") <= Money(Decimal("20"), "EUR")
        with pytest.raises(ValueError, match="Cannot compare"):
            Money(Decimal("10"), "USD") > Money(Decimal("20"), "EUR")
        with pytest.raises(ValueError, match="Cannot compare"):
            Money(Decimal("10"), "USD") >= Money(Decimal("20"), "EUR")

    def test_repr(self):
        m = Money(Decimal("10"), "USD")
        assert repr(m) == "Money(10, 'USD')"


# ============================================================================
# Percentage Tests
# ============================================================================

class TestPercentage:
    def test_construction(self):
        p = Percentage(5000)
        assert p.bps == 5000
        assert p.decimal == Decimal("0.5")

    def test_from_decimal(self):
        p = Percentage.from_decimal(0.25)
        assert p.bps == 2500
        assert p.decimal == Decimal("0.25")

    def test_full_percentage(self):
        p = Percentage(10000)
        assert p.decimal == Decimal("1")

    def test_repr(self):
        p = Percentage(250)
        assert repr(p) == "Percentage(bps=250)"


# ============================================================================
# Compliance Tests
# ============================================================================

class TestComplianceFlag:
    def test_values(self):
        assert ComplianceFlag.SECURITIES_LAW.value == "securities_law"
        assert ComplianceFlag.AML_KYC.value == "aml_kyc"
        assert ComplianceFlag.ACCREDITED_ONLY.value == "accredited_only"
        assert ComplianceFlag.TRANSFER_RESTRICTIONS.value == "transfer_restrictions"
        assert ComplianceFlag.REVENUE_SHARE.value == "revenue_share"
        assert ComplianceFlag.GOVERNANCE_RIGHTS.value == "governance_rights"
        assert ComplianceFlag.PROFIT_PARTICIPATION.value == "profit_participation"


class TestComplianceGate:
    def setup_method(self):
        ComplianceLedger.clear()

    def test_construction(self):
        gate = ComplianceGate(
            gate_id="gate_1",
            description="Test gate",
            flags=[ComplianceFlag.SECURITIES_LAW],
            required_reviewers=["securities_attorney"],
        )
        assert gate.gate_id == "gate_1"
        assert gate.description == "Test gate"
        assert gate.flags == [ComplianceFlag.SECURITIES_LAW]
        assert gate.required_reviewers == ["securities_attorney"]
        assert gate.blocking is True

    def test_non_blocking(self):
        gate = ComplianceGate(
            gate_id="gate_2",
            description="Non-blocking gate",
            flags=[ComplianceFlag.AML_KYC],
            required_reviewers=["compliance_officer"],
            blocking=False,
        )
        assert gate.blocking is False

    def test_auto_registers_in_ledger(self):
        gate = ComplianceGate(
            gate_id="gate_3",
            description="Auto-registered",
            flags=[ComplianceFlag.ACCREDITED_ONLY],
            required_reviewers=["securities_attorney", "tax_counsel"],
        )
        assert ComplianceLedger.get_gate("gate_3") is gate

    def test_ledger_all_gates(self):
        gate1 = ComplianceGate(
            gate_id="g1",
            description="Gate 1",
            flags=[ComplianceFlag.SECURITIES_LAW],
            required_reviewers=["securities_attorney"],
        )
        gate2 = ComplianceGate(
            gate_id="g2",
            description="Gate 2",
            flags=[ComplianceFlag.AML_KYC],
            required_reviewers=["compliance_officer"],
        )
        all_gates = ComplianceLedger.all_gates()
        assert len(all_gates) == 2
        assert all_gates["g1"] is gate1
        assert all_gates["g2"] is gate2

    def test_ledger_clear(self):
        ComplianceGate(
            gate_id="temp",
            description="Temporary",
            flags=[ComplianceFlag.REVENUE_SHARE],
            required_reviewers=["tax_counsel"],
        )
        assert len(ComplianceLedger.all_gates()) == 1
        ComplianceLedger.clear()
        assert len(ComplianceLedger.all_gates()) == 0
