#!/usr/bin/env python3
"""
Production CLI inference script for scoring onboarding enrollees on Day 0.
Outputs expected annual claims spend (NGN), catastrophic risk probability, risk tier, and underwriting actions.
"""

import os
import sys
import json
import argparse

# Ensure root workspace is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.risk_engine.contracts import EnrolleeIntake
from src.risk_engine.pipeline import Day0RiskPredictor

def main():
    parser = argparse.ArgumentParser(description="Day-0 Enrollee Intake Risk Scoring CLI")
    parser.add_argument("--weights", default="models/risk_model_weights.json", help="Path to trained model weights JSON")
    
    # Enrollee Intake Attributes
    parser.add_argument("--enrollee-id", default="ENR-NEW-001", help="Enrollee ID")
    parser.add_argument("--age", type=int, default=32, help="Enrollee Age at onboarding")
    parser.add_argument("--sex", choices=["M", "F"], default="F", help="Sex (M or F)")
    parser.add_argument("--relationship", choices=["PRINCIPAL", "SPOUSE", "CHILD"], default="PRINCIPAL", help="Household role")
    parser.add_argument("--state", default="Lagos", help="Nigerian State of residence")
    parser.add_argument("--lga", default="Ikeja", help="Local Government Area (LGA)")
    parser.add_argument("--scheme", default="Formal Sector Private", help="Scheme type")
    parser.add_argument("--sector", default="Banking & Financial Services", help="Employer industry sector")
    parser.add_argument("--tier", default="Silver / Standard", help="HMO Plan Tier")
    parser.add_argument("--copay", type=float, default=5.0, help="Plan Co-pay percentage")
    parser.add_argument("--pcp-level", choices=["Primary", "Secondary", "Tertiary"], default="Primary", help="Gateway PCP facility level")
    
    # Output formatting
    parser.add_argument("--json", action="store_true", help="Output raw JSON format only")

    args = parser.parse_args()

    predictor = Day0RiskPredictor.load(weights_path=args.weights)

    intake = EnrolleeIntake(
        enrollee_id=args.enrollee_id,
        age=args.age,
        sex=args.sex,
        relationship=args.relationship,
        state=args.state,
        lga=args.lga,
        scheme_type=args.scheme,
        sector=args.sector,
        plan_tier=args.tier,
        co_pay_pct=args.copay,
        pcp_level=args.pcp_level
    )

    result = predictor.predict_enrollee(intake)
    result_dict = result.to_dict()

    if args.json:
        print(json.dumps(result_dict, indent=2))
        return

    print("=" * 68)
    print(f"DAY-0 INTAKE RISK ASSESSMENT DOSSIER: {result.enrollee_id}")
    print("=" * 68)
    print("  ONBOARDING PROFILE:")
    print(f"    - Age / Sex                  : {args.age} years | {args.sex}")
    print(f"    - Household Role             : {args.relationship}")
    print(f"    - Location                   : {args.state} State ({args.lga} LGA)")
    print(f"    - Scheme / Sector            : {args.scheme} | {args.sector}")
    print(f"    - Plan Tier / Co-pay         : {args.tier} (Co-pay: {args.copay}%)")
    print(f"    - Gateway PCP Level          : {args.pcp_level}")
    print("-" * 68)
    print("  PREDICTED ACTUARIAL METRICS:")
    print(f"    - Expected Year-1 Spend (NGN): ₦{result.expected_annual_spend_ngn:,.2f}")
    print(f"    - Catastrophic Risk (>=150k) : {result.catastrophic_risk_prob * 100.0:.2f}% probability")
    print(f"    - Portfolio Risk Decile      : Decile {result.risk_decile} / 10")
    print(f"    - Assigned Risk Tier         : [{result.risk_tier.value}]")
    print("-" * 68)
    print("  UNDERWRITING & CLINICAL ACTIONS:")
    print(f"    - Retail Premium Surcharge   : +{result.underwriting.retail_premium_surcharge_pct:.1f}%")
    print(f"    - Recommended Waiting Period : {result.underwriting.recommended_waiting_period_days} days")
    print(f"    - Proactive Care Management  : {'YES (Assigned Case Manager)' if result.underwriting.proactive_care_management_required else 'No (Standard Primary Pathway)'}")
    print(f"    - Recommended Gateway Clinic : {result.underwriting.recommended_pcp_gatekeeper_tier}")
    print(f"    - Underwriting Notes         : {result.underwriting.underwriting_notes}")
    print("=" * 68)

if __name__ == "__main__":
    main()
