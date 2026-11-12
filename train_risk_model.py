#!/usr/bin/env python3
"""
CLI model training and evaluation script for the Day-0 Enrollee Risk Engine.
Trains on historical enrollees in SQLite, validates on holdout, and serializes model weights.
"""

import os
import sys
import json
import time
import argparse
import numpy as np

# Ensure root workspace is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.risk_engine.extractor import extract_day0_dataset
from src.risk_engine.features import FeaturePipeline
from src.risk_engine.models import ActuarialSpendGLM, CatastrophicRiskClassifier, RiskDecileCalibrator
from src.risk_engine.evaluator import evaluate_models

def train_and_evaluate(
    db_path: str = "nigerian_hmo.db",
    out_weights: str = "models/risk_model_weights.json",
    sample_size: int = None
):
    print("=" * 65)
    print("DAY-0 ENROLLEE RISK ENGINE: MODEL TRAINING & EVALUATION")
    print("=" * 65)

    # 1. Extraction
    print(f"Loading Day-0 onboarding records from '{db_path}'...")
    t0 = time.time()
    records = extract_day0_dataset(db_path=db_path, limit=sample_size)
    print(f"  Loaded {len(records):,} records in {time.time() - t0:.2f}s")

    # 2. Splitting
    print("Splitting dataset into Train (70%), Validation (15%), Test (15%)...")
    train_recs, val_recs, test_recs = FeaturePipeline.split_dataset(records, train_ratio=0.70, val_ratio=0.15, seed=42)
    print(f"  Train: {len(train_recs):,} | Validation: {len(val_recs):,} | Test: {len(test_recs):,}")

    # 3. Feature Transformation
    print("Transforming Day-0 intake features...")
    pipeline = FeaturePipeline()
    X_train = pipeline.transform(train_recs)
    y_spend_train, y_hr_train = pipeline.extract_targets(train_recs)

    X_val = pipeline.transform(val_recs)
    y_spend_val, y_hr_val = pipeline.extract_targets(val_recs)

    X_test = pipeline.transform(test_recs)
    y_spend_test, y_hr_test = pipeline.extract_targets(test_recs)

    # 4. Training
    print("Training Actuarial Log-Link GLM (Claims Spend)...")
    t0_glm = time.time()
    glm = ActuarialSpendGLM(l2_reg=1e-3, target_scale=1000.0)
    glm.fit(X_train, y_spend_train)
    print(f"  GLM converged in {time.time() - t0_glm:.2f}s")

    print("Training Catastrophic Risk Classifier (High-Cost >= 150k NGN)...")
    t0_clf = time.time()
    clf = CatastrophicRiskClassifier(l2_reg=1e-3)
    clf.fit(X_train, y_hr_train)
    print(f"  Classifier converged in {time.time() - t0_clf:.2f}s")

    print("Calibrating Risk Deciles...")
    calibrator = RiskDecileCalibrator()
    train_pred_spend = glm.predict(X_train)
    calibrator.fit(train_pred_spend)

    # 5. Evaluation on Test Set
    print("\nEvaluating on Independent Holdout Test Set...")
    test_pred_spend = glm.predict(X_test)
    test_pred_hr_prob = clf.predict_proba(X_test)
    metrics = evaluate_models(y_spend_test, test_pred_spend, y_hr_test, test_pred_hr_prob)

    print("\n" + "=" * 65)
    print("ACTUARIAL PERFORMANCE REPORT (TEST SET)")
    print("=" * 65)
    print(f"  Gini Coefficient               : {metrics['gini_coefficient']:.4f}")
    print(f"  Catastrophic ROC-AUC (>=150k)   : {metrics['catastrophic_roc_auc']:.4f}")
    print(f"  Mean Absolute Error (MAE)      : ₦{metrics['mae_ngn']:,.2f}")
    print(f"  Top Decile Spend Capture Rate  : {metrics['top_decile_spend_capture_pct']:.1f}%")
    print(f"  Top Decile Lift Factor         : {metrics['top_decile_lift_factor']:.2f}x")
    print("-" * 65)
    print("  DECILE LIFT TABLE (Low Risk Decile 1 -> High Risk Decile 10):")
    print(f"  {'Decile':<8} {'Pred Mean':<14} {'Actual Mean':<14} {'Spend %':<10} {'Cumul %':<10} {'Lift':<8}")
    for row in metrics["decile_table"]:
        print(f"  {row['decile']:<8} ₦{row['pred_mean_spend_ngn']:<13,.0f} ₦{row['actual_mean_spend_ngn']:<13,.0f} {row['spend_share_pct']:<9.1f}% {row['cumulative_share_pct']:<9.1f}% {row['lift_vs_portfolio']:<6.2f}x")
    print("=" * 65)

    # 6. Save Artifacts
    os.makedirs(os.path.dirname(out_weights), exist_ok=True)
    artifact = {
        "pipeline": pipeline.to_dict(),
        "glm_spend_model": glm.to_dict(),
        "catastrophic_classifier": clf.to_dict(),
        "calibrator": calibrator.to_dict(),
        "evaluation_metrics": metrics
    }
    with open(out_weights, "w", encoding="utf-8") as f:
        json.dump(artifact, f, indent=2)

    print(f"\nModel artifacts successfully saved to '{out_weights}'.")
    return artifact

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Day-0 Enrollee Risk Engine")
    parser.add_argument("--db-path", default="nigerian_hmo.db", help="Path to SQLite database")
    parser.add_argument("--out-weights", default="models/risk_model_weights.json", help="Path to save weights")
    parser.add_argument("--sample-size", type=int, default=None, help="Optional limit for fast debugging")

    args = parser.parse_args()
    train_and_evaluate(db_path=args.db_path, out_weights=args.out_weights, sample_size=args.sample_size)
