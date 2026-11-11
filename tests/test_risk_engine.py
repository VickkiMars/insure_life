"""Unit tests for Phase 1 & 2 of the Day-0 Risk Engine."""

import unittest
import numpy as np
from src.risk_engine.contracts import EnrolleeIntake, RiskTier, UnderwritingAction, RiskScoreResult
from src.risk_engine.extractor import extract_day0_dataset
from src.risk_engine.features import FeaturePipeline

class TestRiskEnginePhase1(unittest.TestCase):

    def test_enrollee_intake_contract(self):
        intake = EnrolleeIntake(
            age=34,
            sex="F",
            relationship="PRINCIPAL",
            state="Lagos",
            lga="Ikeja",
            scheme_type="Formal Sector Private",
            sector="Banking & Financial Services",
            plan_tier="Gold / Comprehensive",
            co_pay_pct=0.0,
            pcp_level="Secondary"
        )
        d = intake.to_dict()
        self.assertEqual(d["age"], 34)
        self.assertEqual(d["sex"], "F")
        self.assertEqual(d["state"], "Lagos")

    def test_feature_transformation(self):
        pipe = FeaturePipeline()
        intake = EnrolleeIntake(
            age=3,
            sex="M",
            relationship="CHILD",
            state="Lagos",
            lga="Alimosho",
            scheme_type="Formal Sector Private",
            sector="FMCG",
            plan_tier="Silver / Standard",
            co_pay_pct=5.0,
            pcp_level="Primary"
        )
        vec = pipe.transform_single(intake)
        self.assertEqual(len(vec), len(FeaturePipeline.FEATURE_NAMES))
        # Pediatric flag check (index 3)
        self.assertEqual(vec[3], 1.0)
        # Child flag check (index 9)
        self.assertEqual(vec[9], 1.0)
        # Female flag check (index 5)
        self.assertEqual(vec[5], 0.0)

    def test_database_extraction(self):
        records = extract_day0_dataset(limit=25)
        self.assertEqual(len(records), 25)
        first = records[0]
        self.assertIn("age", first)
        self.assertIn("year1_claims_cost", first)
        self.assertIn("year1_high_risk_flag", first)

if __name__ == "__main__":
    unittest.main()
