"""End-to-end prediction pipeline and model loader for Day-0 Enrollee Intake scoring."""

import os
import json
from typing import List, Union, Dict, Any

from src.risk_engine.contracts import EnrolleeIntake, RiskScoreResult
from src.risk_engine.features import FeaturePipeline
from src.risk_engine.models import ActuarialSpendGLM, CatastrophicRiskClassifier, RiskDecileCalibrator
from src.risk_engine.policy_rules import UnderwritingPolicyEngine

class Day0RiskPredictor:
    """Production serving pipeline for scoring enrollees at onboarding."""

    def __init__(
        self,
        pipeline: FeaturePipeline,
        glm: ActuarialSpendGLM,
        classifier: CatastrophicRiskClassifier,
        calibrator: RiskDecileCalibrator
    ):
        self.pipeline = pipeline
        self.glm = glm
        self.classifier = classifier
        self.calibrator = calibrator

    @classmethod
    def load(cls, weights_path: str = "models/risk_model_weights.json") -> "Day0RiskPredictor":
        """Loads trained weights and calibration artifacts from a JSON file."""
        if not os.path.exists(weights_path):
            raise FileNotFoundError(f"Weights file not found at '{weights_path}'. Please train the model first.")

        with open(weights_path, "r", encoding="utf-8") as f:
            artifact = json.load(f)

        pipe = FeaturePipeline.from_dict(artifact["pipeline"])
        glm = ActuarialSpendGLM.from_dict(artifact["glm_spend_model"])
        clf = CatastrophicRiskClassifier.from_dict(artifact["catastrophic_classifier"])
        calibrator = RiskDecileCalibrator.from_dict(artifact["calibrator"])

        return cls(pipeline=pipe, glm=glm, classifier=clf, calibrator=calibrator)

    def predict_enrollee(self, intake: Union[EnrolleeIntake, Dict[str, Any]]) -> RiskScoreResult:
        """Scores a single enrollee at onboarding and returns full risk dossier."""
        if isinstance(intake, dict):
            intake_obj = EnrolleeIntake(**intake)
        else:
            intake_obj = intake

        vec = self.pipeline.transform_single(intake_obj).reshape(1, -1)

        expected_spend = float(self.glm.predict(vec)[0])
        cat_prob = float(self.classifier.predict_proba(vec)[0])
        decile = self.calibrator.predict_decile(expected_spend)

        underwriting = UnderwritingPolicyEngine.evaluate(
            expected_annual_spend_ngn=expected_spend,
            catastrophic_risk_prob=cat_prob,
            decile=decile,
            scheme_type=intake_obj.scheme_type
        )

        return RiskScoreResult(
            enrollee_id=intake_obj.enrollee_id,
            expected_annual_spend_ngn=round(expected_spend, 2),
            catastrophic_risk_prob=round(cat_prob, 4),
            risk_decile=decile,
            risk_tier=underwriting.risk_tier,
            underwriting=underwriting
        )

    def predict_batch(self, intakes: List[Union[EnrolleeIntake, Dict[str, Any]]]) -> List[RiskScoreResult]:
        """Scores a batch of enrollees."""
        return [self.predict_enrollee(i) for i in intakes]
