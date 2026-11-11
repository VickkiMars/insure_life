"""Feature engineering and transformation pipeline for Day-0 Enrollee Intake."""

import random
from typing import List, Dict, Any, Union, Tuple
import numpy as np

from src.risk_engine.contracts import EnrolleeIntake

class FeaturePipeline:
    """
    Stateful feature extraction and encoding pipeline.
    Transforms raw dictionaries or EnrolleeIntake objects into pure NumPy arrays.
    """

    FEATURE_NAMES = [
        "intercept",
        "age_norm",
        "age_sq",
        "is_pediatric",
        "is_senior",
        "is_female",
        "is_maternal_age_female",
        "rel_principal",
        "rel_spouse",
        "rel_child",
        "geo_lagos",
        "geo_abuja",
        "geo_rivers",
        "geo_oyo",
        "geo_kano",
        "geo_other",
        "scheme_formal_private",
        "scheme_formal_public",
        "scheme_retail",
        "scheme_equity",
        "tier_bronze",
        "tier_silver",
        "tier_gold",
        "tier_platinum",
        "tier_equity",
        "co_pay_norm",
        "pcp_primary",
        "pcp_secondary",
        "pcp_tertiary",
        "sector_high_risk",
        "sector_retail"
    ]

    def __init__(self, age_mean: float = 29.5, age_std: float = 16.0):
        self.age_mean = age_mean
        self.age_std = age_std

    def transform_single(self, intake: Union[EnrolleeIntake, Dict[str, Any]]) -> np.ndarray:
        """Transforms a single enrollee intake record into a 1D NumPy feature array."""
        if isinstance(intake, EnrolleeIntake):
            data = intake.to_dict()
        else:
            data = intake

        age = float(data.get("age", 30))
        sex = data.get("sex", "M").upper()
        rel = data.get("relationship", "PRINCIPAL").upper()
        state = data.get("state", "Lagos")
        scheme = data.get("scheme_type", "Formal Sector Private")
        plan = data.get("plan_tier", "Silver / Standard")
        copay = float(data.get("co_pay_pct", 5.0))
        pcp = data.get("pcp_level", "Primary")
        sector = data.get("sector", "Retail / Individual")

        age_norm = (age - self.age_mean) / self.age_std
        age_sq = age_norm ** 2

        is_pediatric = 1.0 if age < 5 else 0.0
        is_senior = 1.0 if age >= 50 else 0.0
        is_female = 1.0 if sex == "F" else 0.0
        is_maternal = 1.0 if (sex == "F" and 18 <= age <= 45) else 0.0

        vec = [
            1.0,  # Intercept
            age_norm,
            age_sq,
            is_pediatric,
            is_senior,
            is_female,
            is_maternal,
            1.0 if rel == "PRINCIPAL" else 0.0,
            1.0 if rel == "SPOUSE" else 0.0,
            1.0 if rel == "CHILD" else 0.0,
            1.0 if state == "Lagos" else 0.0,
            1.0 if state in ("FCT Abuja", "Abuja") else 0.0,
            1.0 if state == "Rivers" else 0.0,
            1.0 if state == "Oyo" else 0.0,
            1.0 if state == "Kano" else 0.0,
            1.0 if state not in ("Lagos", "FCT Abuja", "Abuja", "Rivers", "Oyo", "Kano") else 0.0,
            1.0 if "Private" in scheme else 0.0,
            1.0 if "Public" in scheme else 0.0,
            1.0 if ("Retail" in scheme or "Informal" in scheme) else 0.0,
            1.0 if ("Equity" in scheme or "BHCPF" in scheme) else 0.0,
            1.0 if "Bronze" in plan else 0.0,
            1.0 if "Silver" in plan else 0.0,
            1.0 if "Gold" in plan else 0.0,
            1.0 if "Platinum" in plan else 0.0,
            1.0 if ("State Equity" in plan or "BHCPF" in plan) else 0.0,
            copay / 10.0,
            1.0 if pcp == "Primary" else 0.0,
            1.0 if pcp == "Secondary" else 0.0,
            1.0 if pcp == "Tertiary" else 0.0,
            1.0 if any(k in sector for k in ("Industry", "Oil & Gas", "Logistics")) else 0.0,
            1.0 if ("Retail" in sector or "Individual" in sector) else 0.0
        ]
        return np.array(vec, dtype=np.float64)

    def transform(self, records: List[Union[EnrolleeIntake, Dict[str, Any]]]) -> np.ndarray:
        """Transforms a batch of enrollee records into a 2D NumPy array (N, D)."""
        rows = [self.transform_single(r) for r in records]
        return np.vstack(rows)

    def extract_targets(self, records: List[Dict[str, Any]]) -> Tuple[np.ndarray, np.ndarray]:
        """Extracts continuous spend and binary high risk target vectors from raw DB records."""
        spend = np.array([float(r.get("year1_claims_cost", 0.0)) for r in records], dtype=np.float64)
        high_risk = np.array([int(r.get("year1_high_risk_flag", 0)) for r in records], dtype=np.int32)
        return spend, high_risk

    @staticmethod
    def split_dataset(records: List[Dict[str, Any]], train_ratio=0.70, val_ratio=0.15, seed=42):
        """Splits records reproducibly into train, validation, and test subsets."""
        rng = random.Random(seed)
        shuffled = list(records)
        rng.shuffle(shuffled)

        n = len(shuffled)
        n_train = int(n * train_ratio)
        n_val = int(n * val_ratio)

        train_data = shuffled[:n_train]
        val_data = shuffled[n_train:n_train + n_val]
        test_data = shuffled[n_train + n_val:]

        return train_data, val_data, test_data

    def to_dict(self) -> Dict[str, Any]:
        return {
            "age_mean": self.age_mean,
            "age_std": self.age_std,
            "feature_names": self.FEATURE_NAMES
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FeaturePipeline":
        return cls(age_mean=data.get("age_mean", 29.5), age_std=data.get("age_std", 16.0))
