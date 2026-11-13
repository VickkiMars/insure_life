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

class TestRiskEnginePhase2(unittest.TestCase):

    def test_glm_and_classifier_convergence(self):
        from src.risk_engine.models import ActuarialSpendGLM, CatastrophicRiskClassifier, RiskDecileCalibrator
        from src.risk_engine.evaluator import calculate_gini, calculate_roc_auc, compute_decile_lift

        np.random.seed(42)
        N, D = 100, 10
        X = np.random.randn(N, D)
        X[:, 0] = 1.0
        y_spend = np.random.exponential(5000, size=N)
        y_hr = (y_spend > 10000).astype(int)

        glm = ActuarialSpendGLM(l2_reg=1e-3)
        glm.fit(X, y_spend)
        preds = glm.predict(X)
        self.assertEqual(len(preds), N)
        self.assertTrue(np.all(preds > 0))

        clf = CatastrophicRiskClassifier(l2_reg=1e-3)
        clf.fit(X, y_hr)
        probs = clf.predict_proba(X)
        self.assertEqual(len(probs), N)
        self.assertTrue(np.all((probs >= 0.0) & (probs <= 1.0)))

        calibrator = RiskDecileCalibrator().fit(preds)
        decile = calibrator.predict_decile(float(preds[0]))
        self.assertTrue(1 <= decile <= 10)

        # Test metrics
        auc = calculate_roc_auc(y_hr, probs)
        self.assertTrue(0.0 <= auc <= 1.0)

        lift = compute_decile_lift(y_spend, preds)
        self.assertEqual(len(lift), 10)
        self.assertEqual(lift[-1]["decile"], 10)

class TestRiskEnginePhase3(unittest.TestCase):

    def test_underwriting_policy_rules(self):
        from src.risk_engine.policy_rules import UnderwritingPolicyEngine

        # Low risk corporate profile
        action_low = UnderwritingPolicyEngine.evaluate(
            expected_annual_spend_ngn=1500.0,
            catastrophic_risk_prob=0.03,
            decile=2,
            scheme_type="Formal Sector Private"
        )
        self.assertEqual(action_low.risk_tier, RiskTier.TIER_1_LOW)
        self.assertEqual(action_low.retail_premium_surcharge_pct, 0.0)
        self.assertFalse(action_low.proactive_care_management_required)

        # High risk retail profile
        action_high = UnderwritingPolicyEngine.evaluate(
            expected_annual_spend_ngn=18000.0,
            catastrophic_risk_prob=0.35,
            decile=10,
            scheme_type="Informal / Voluntary Retail"
        )
        self.assertEqual(action_high.risk_tier, RiskTier.TIER_4_CRITICAL)
        self.assertEqual(action_high.retail_premium_surcharge_pct, 35.0)
        self.assertEqual(action_high.recommended_waiting_period_days, 90)
        self.assertTrue(action_high.proactive_care_management_required)

    def test_end_to_end_predictor_pipeline(self):
        from src.risk_engine.pipeline import Day0RiskPredictor

        predictor = Day0RiskPredictor.load("models/risk_model_weights.json")
        intake = EnrolleeIntake(
            enrollee_id="ENR-TEST-999",
            age=45,
            sex="M",
            relationship="PRINCIPAL",
            state="Lagos",
            lga="Ikeja",
            scheme_type="Formal Sector Private",
            sector="Banking & Financial Services",
            plan_tier="Gold / Comprehensive",
            co_pay_pct=0.0,
            pcp_level="Secondary"
        )
        result = predictor.predict_enrollee(intake)
        self.assertEqual(result.enrollee_id, "ENR-TEST-999")
        self.assertGreater(result.expected_annual_spend_ngn, 0.0)
        self.assertTrue(0.0 <= result.catastrophic_risk_prob <= 1.0)
        self.assertTrue(1 <= result.risk_decile <= 10)
        self.assertIn(result.risk_tier, [RiskTier.TIER_1_LOW, RiskTier.TIER_2_MODERATE, RiskTier.TIER_3_HIGH, RiskTier.TIER_4_CRITICAL])

if __name__ == "__main__":
    unittest.main()
