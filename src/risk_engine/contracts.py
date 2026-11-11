"""Data contracts, domain models, and Enums for the Day-0 Risk Engine."""

from dataclasses import dataclass, asdict
from enum import Enum
from typing import Optional, Dict, Any

class RiskTier(str, Enum):
    TIER_1_LOW = "TIER_1_LOW"
    TIER_2_MODERATE = "TIER_2_MODERATE"
    TIER_3_HIGH = "TIER_3_HIGH"
    TIER_4_CRITICAL = "TIER_4_CRITICAL"

@dataclass(frozen=True)
class EnrolleeIntake:
    """Snapshot of enrollee attributes available strictly on Day 0 of onboarding."""
    age: int
    sex: str                          # 'M' or 'F'
    relationship: str                 # 'PRINCIPAL', 'SPOUSE', 'CHILD'
    state: str                        # Nigerian State (e.g., 'Lagos', 'FCT Abuja')
    lga: str                          # Local Government Area
    scheme_type: str                  # Formal Sector Private, Formal Sector Public, Retail, etc.
    sector: str                       # Banking, Oil & Gas, FMCG, Retail / Individual, etc.
    plan_tier: str                    # Bronze / Vital, Silver / Standard, Gold, Platinum
    co_pay_pct: float                 # 0.0, 5.0, 10.0
    pcp_level: str                    # 'Primary', 'Secondary', 'Tertiary'
    enrollee_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass(frozen=True)
class UnderwritingAction:
    """Actionable business logic decision produced by the policy rule engine."""
    risk_tier: RiskTier
    retail_premium_surcharge_pct: float
    recommended_waiting_period_days: int
    proactive_care_management_required: bool
    recommended_pcp_gatekeeper_tier: str
    underwriting_notes: str

@dataclass(frozen=True)
class RiskScoreResult:
    """Comprehensive risk assessment dossier for an onboarding enrollee."""
    enrollee_id: Optional[str]
    expected_annual_spend_ngn: float
    catastrophic_risk_prob: float
    risk_decile: int
    risk_tier: RiskTier
    underwriting: UnderwritingAction

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["risk_tier"] = self.risk_tier.value
        d["underwriting"]["risk_tier"] = self.underwriting.risk_tier.value
        return d
