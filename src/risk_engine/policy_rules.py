"""Underwriting policy rule engine for Day-0 risk tiering and decisioning."""

from src.risk_engine.contracts import RiskTier, UnderwritingAction

class UnderwritingPolicyEngine:
    """
    Applies HMO actuarial underwriting rules to predicted claims spend and catastrophic probability.
    Determines risk tiers, retail surcharge loadings, waiting periods, and care routing.
    """

    @staticmethod
    def evaluate(
        expected_annual_spend_ngn: float,
        catastrophic_risk_prob: float,
        decile: int,
        scheme_type: str = "Formal Sector Private"
    ) -> UnderwritingAction:
        is_retail = "Retail" in scheme_type or "Informal" in scheme_type or "Individual" in scheme_type

        # Risk Tier Classification Logic
        if expected_annual_spend_ngn < 2500.0 and catastrophic_risk_prob < 0.08 and decile <= 3:
            tier = RiskTier.TIER_1_LOW
            surcharge = 0.0
            waiting_days = 0 if not is_retail else 14
            proactive_care = False
            gatekeeper = "Primary Care Clinic / PHC"
            notes = "Standard healthy profile. Preferred risk band. Eligible for immediate elective benefits."

        elif expected_annual_spend_ngn < 4500.0 and catastrophic_risk_prob < 0.18 and decile <= 7:
            tier = RiskTier.TIER_2_MODERATE
            surcharge = 5.0 if is_retail else 0.0
            waiting_days = 30
            proactive_care = False
            gatekeeper = "Standard Primary Care Center"
            notes = "Standard actuarial risk. Normal utilization expected under primary gatekeeper model."

        elif expected_annual_spend_ngn < 8000.0 or catastrophic_risk_prob < 0.30 or decile <= 9:
            tier = RiskTier.TIER_3_HIGH
            surcharge = 20.0 if is_retail else 0.0
            waiting_days = 60
            proactive_care = True
            gatekeeper = "Secondary Specialist Hospital Annex"
            notes = "Elevated risk profile. Enforce 60-day surgical waiting period and assign proactive wellness case manager."

        else:
            tier = RiskTier.TIER_4_CRITICAL
            surcharge = 35.0 if is_retail else 0.0
            waiting_days = 90
            proactive_care = True
            gatekeeper = "Specialist Tertiary / Multi-specialist Center"
            notes = "High-risk adverse exposure. Mandatory 90-day surgical waiting period and specialized chronic care protocol."

        return UnderwritingAction(
            risk_tier=tier,
            retail_premium_surcharge_pct=surcharge,
            recommended_waiting_period_days=waiting_days,
            proactive_care_management_required=proactive_care,
            recommended_pcp_gatekeeper_tier=gatekeeper,
            underwriting_notes=notes
        )
