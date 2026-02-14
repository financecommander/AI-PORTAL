from typing import Literal
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum


# ============================================================================
# Type System Foundation
# ============================================================================

class Jurisdiction(Enum):
    US = "US"
    EU = "EU"
    CAYMAN = "KY"
    DELAWARE = "US-DE"


class SecuritiesClassification(Enum):
    SECURITY = "security"              # Definite security
    UTILITY = "utility"                # Utility token (rare)
    HYBRID = "hybrid"                  # Needs case-by-case analysis
    UNKNOWN = "unknown"                # Requires legal determination


class RegulationExemption(Enum):
    REG_D_506B = "Reg D 506(b)"       # 35 non-accredited max
    REG_D_506C = "Reg D 506(c)"       # Accredited only, general solicitation OK
    REG_A_TIER1 = "Reg A+ Tier 1"     # $20M cap
    REG_A_TIER2 = "Reg A+ Tier 2"     # $75M cap
    REG_S = "Reg S"                    # Offshore only
    REG_CF = "Reg CF"                  # Crowdfunding, $5M cap


class TokenStandard(Enum):
    ERC20 = "ERC-20"                   # Fungible
    ERC721 = "ERC-721"                 # Non-fungible
    ERC1400 = "ERC-1400"               # Security token
    SPL_TOKEN = "SPL Token"            # Solana
    CUSTOM = "Custom"


# ============================================================================
# Primitive Types
# ============================================================================

class Money:
    """Type-safe monetary amount with currency"""
    def __init__(self, amount: Decimal, currency: str = "USD"):
        self.amount = Decimal(amount)
        self.currency = currency

    def __add__(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError(f"Cannot add {self.currency} and {other.currency}")
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError(f"Cannot subtract {self.currency} and {other.currency}")
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, factor: Decimal) -> 'Money':
        return Money(self.amount * Decimal(factor), self.currency)

    def __truediv__(self, divisor: Decimal) -> 'Money':
        return Money(self.amount / Decimal(divisor), self.currency)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount == other.amount and self.currency == other.currency

    def __lt__(self, other: 'Money') -> bool:
        if self.currency != other.currency:
            raise ValueError(f"Cannot compare {self.currency} and {other.currency}")
        return self.amount < other.amount

    def __le__(self, other: 'Money') -> bool:
        if self.currency != other.currency:
            raise ValueError(f"Cannot compare {self.currency} and {other.currency}")
        return self.amount <= other.amount

    def __gt__(self, other: 'Money') -> bool:
        if self.currency != other.currency:
            raise ValueError(f"Cannot compare {self.currency} and {other.currency}")
        return self.amount > other.amount

    def __ge__(self, other: 'Money') -> bool:
        if self.currency != other.currency:
            raise ValueError(f"Cannot compare {self.currency} and {other.currency}")
        return self.amount >= other.amount

    def __repr__(self) -> str:
        return f"Money({self.amount}, '{self.currency}')"


class Percentage:
    """Basis point precision percentage"""
    def __init__(self, bps: int):
        self.bps = bps  # 10000 bps = 100%
        self.decimal = Decimal(bps) / Decimal(10000)

    @classmethod
    def from_decimal(cls, decimal: float) -> 'Percentage':
        return cls(int(decimal * 10000))

    def __repr__(self) -> str:
        return f"Percentage(bps={self.bps})"


# ============================================================================
# Annotation Types for Compliance
# ============================================================================

class ComplianceFlag(Enum):
    SECURITIES_LAW = "securities_law"
    AML_KYC = "aml_kyc"
    ACCREDITED_ONLY = "accredited_only"
    TRANSFER_RESTRICTIONS = "transfer_restrictions"
    REVENUE_SHARE = "revenue_share"
    GOVERNANCE_RIGHTS = "governance_rights"
    PROFIT_PARTICIPATION = "profit_participation"


class ComplianceLedger:
    """Global registry of compliance gates"""
    _gates: dict[str, 'ComplianceGate'] = {}

    @classmethod
    def register_gate(cls, gate: 'ComplianceGate') -> None:
        cls._gates[gate.gate_id] = gate

    @classmethod
    def get_gate(cls, gate_id: str) -> 'ComplianceGate':
        return cls._gates[gate_id]

    @classmethod
    def all_gates(cls) -> dict[str, 'ComplianceGate']:
        return dict(cls._gates)

    @classmethod
    def clear(cls) -> None:
        cls._gates.clear()


@dataclass
class ComplianceGate:
    """Mandatory human review checkpoint"""
    gate_id: str
    description: str
    flags: list[ComplianceFlag]
    required_reviewers: list[Literal["securities_attorney", "tax_counsel", "compliance_officer"]]
    blocking: bool = True  # Prevents downstream actions if not cleared

    def __post_init__(self) -> None:
        # Auto-register in global compliance ledger
        ComplianceLedger.register_gate(self)
