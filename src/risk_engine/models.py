"""Actuarial GLM spend model, catastrophic risk classifier, and decile calibrator."""

from typing import Dict, Any, Tuple
import numpy as np
from scipy.optimize import minimize

class ActuarialSpendGLM:
    """
    Log-Link Generalized Linear Model (Poisson/Gamma formulation) for health claims cost.
    Optimizes E[Y | X] = exp(X * beta) with L2 regularization via SciPy L-BFGS-B.
    Target is scaled by 1,000 NGN internally for numerical stability.
    """

    def __init__(self, l2_reg: float = 1e-3, target_scale: float = 1000.0):
        self.l2_reg = l2_reg
        self.target_scale = target_scale
        self.beta = None

    def fit(self, X: np.ndarray, y: np.ndarray, max_iter: int = 200) -> "ActuarialSpendGLM":
        N, D = X.shape
        y_scaled = np.maximum(y, 0.0) / self.target_scale

        def objective(b):
            xb = np.clip(X @ b, -10.0, 12.0)
            mu = np.exp(xb)
            loss = np.mean(mu - y_scaled * xb) + 0.5 * self.l2_reg * np.sum(b[1:] ** 2)
            grad = (X.T @ (mu - y_scaled)) / N
            grad[1:] += self.l2_reg * b[1:]
            return loss, grad

        init_beta = np.zeros(D, dtype=np.float64)
        init_beta[0] = np.log(max(np.mean(y_scaled), 1.0)) # Initialize intercept to mean

        res = minimize(
            objective,
            init_beta,
            jac=True,
            method="L-BFGS-B",
            options={"maxiter": max_iter, "disp": False}
        )
        self.beta = res.x
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        if self.beta is None:
            raise ValueError("Model is not fitted yet.")
        xb = np.clip(X @ self.beta, -10.0, 12.0)
        mu_scaled = np.exp(xb)
        return mu_scaled * self.target_scale

    def to_dict(self) -> Dict[str, Any]:
        return {
            "l2_reg": self.l2_reg,
            "target_scale": self.target_scale,
            "beta": self.beta.tolist() if self.beta is not None else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ActuarialSpendGLM":
        model = cls(l2_reg=data["l2_reg"], target_scale=data["target_scale"])
        if data.get("beta") is not None:
            model.beta = np.array(data["beta"], dtype=np.float64)
        return model

class CatastrophicRiskClassifier:
    """
    Regularized Logistic Regression classifier for high-cost catastrophic risk (spend >= 150,000 NGN).
    P(HighRisk = 1 | X) = 1 / (1 + exp(-X * theta)).
    """

    def __init__(self, l2_reg: float = 1e-3):
        self.l2_reg = l2_reg
        self.theta = None

    def fit(self, X: np.ndarray, y: np.ndarray, max_iter: int = 200) -> "CatastrophicRiskClassifier":
        N, D = X.shape
        y_binary = (y > 0).astype(np.float64)

        def objective(th):
            z = np.clip(X @ th, -15.0, 15.0)
            p = 1.0 / (1.0 + np.exp(-z))
            # Binary cross entropy with numerical stability
            loss = -np.mean(y_binary * np.log(p + 1e-12) + (1.0 - y_binary) * np.log(1.0 - p + 1e-12))
            loss += 0.5 * self.l2_reg * np.sum(th[1:] ** 2)

            grad = (X.T @ (p - y_binary)) / N
            grad[1:] += self.l2_reg * th[1:]
            return loss, grad

        init_theta = np.zeros(D, dtype=np.float64)
        pos_rate = np.mean(y_binary)
        if 0 < pos_rate < 1:
            init_theta[0] = np.log(pos_rate / (1.0 - pos_rate))

        res = minimize(
            objective,
            init_theta,
            jac=True,
            method="L-BFGS-B",
            options={"maxiter": max_iter, "disp": False}
        )
        self.theta = res.x
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if self.theta is None:
            raise ValueError("Classifier is not fitted yet.")
        z = np.clip(X @ self.theta, -15.0, 15.0)
        return 1.0 / (1.0 + np.exp(-z))

    def predict(self, X: np.ndarray, threshold: float = 0.15) -> np.ndarray:
        return (self.predict_proba(X) >= threshold).astype(int)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "l2_reg": self.l2_reg,
            "theta": self.theta.tolist() if self.theta is not None else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CatastrophicRiskClassifier":
        clf = cls(l2_reg=data["l2_reg"])
        if data.get("theta") is not None:
            clf.theta = np.array(data["theta"], dtype=np.float64)
        return clf

class RiskDecileCalibrator:
    """Calibrates model predictions into 10 actuarial risk deciles based on training quantiles."""

    def __init__(self, thresholds: list = None):
        self.thresholds = thresholds

    def fit(self, y_pred: np.ndarray) -> "RiskDecileCalibrator":
        # Calculate 9 quantile cut points for deciles 1 to 10
        percentiles = [10, 20, 30, 40, 50, 60, 70, 80, 90]
        self.thresholds = [float(np.percentile(y_pred, p)) for p in percentiles]
        return self

    def predict_decile(self, score: float) -> int:
        if self.thresholds is None:
            return 5
        for idx, cutoff in enumerate(self.thresholds, 1):
            if score <= cutoff:
                return idx
        return 10

    def to_dict(self) -> Dict[str, Any]:
        return {"thresholds": self.thresholds}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RiskDecileCalibrator":
        return cls(thresholds=data.get("thresholds"))
