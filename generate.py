#!/usr/bin/env python3
"""
Main CLI data generation script for synthetic Nigerian HMO health insurance datasets.
Produces >= 1,000,000 interconnected records across 16 tables.
"""

import os
import sys
import time
import random
import argparse

# Ensure src package is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database import init_db, insert_batch, export_table_to_csv
from src.reference_data import generate_geography_and_icd10, generate_tariff_schedule, generate_drug_formulary
from src.entities import generate_brokers, generate_plans, generate_groups, generate_providers, generate_enrollees
from src.transactions import generate_premium_invoices, generate_capitation_payments, generate_claims_and_lines
from src.operations import generate_complaints_tickets, generate_audit_flags

def run_generation(scale="full", seed=42, db_path="nigerian_hmo.db", csv_dir="data", export_csv=True, export_sqlite=True):
    start_time = time.time()
    if seed is not None:
        random.seed(seed)

    # Scaling profiles
    if scale == "full":
        num_brokers = 120
        num_groups = 500
        num_providers = 1500
        num_enrollees = 100000
        num_claims = 260000
        num_complaints = 18000
        num_audit_flags = 22000
    elif scale == "test" or scale == "sample":
        num_brokers = 20
        num_groups = 50
        num_providers = 150
        num_enrollees = 8000
        num_claims = 18000
        num_complaints = 1200
        num_audit_flags = 1500
    else:
        raise ValueError(f"Unknown scale profile: {scale}")

    print(f"===========================================================")
    print(f"Starting Nigerian HMO Synthetic Data Generation")
    print(f"Scale: {scale.upper()} | Random Seed: {seed}")
    print(f"Target Enrollees: {num_enrollees:,} | Target Claims: {num_claims:,}")
    print(f"===========================================================")

    conn = init_db(db_path) if export_sqlite else None

    # Step 1: Reference Data
    print("Generating reference data (ICD-10, Geography, Tariffs, Formulary)...")
    _, icd_rows = generate_geography_and_icd10()
    tariffs = generate_tariff_schedule()
    drugs = generate_drug_formulary()

    # Step 2: Core Entities
    print("Generating core entities (Brokers, Plans, Groups, Providers)...")
    brokers = generate_brokers(num_brokers)
    broker_ids = [b["broker_id"] for b in brokers]
    plans = generate_plans()
    groups = generate_groups(num_groups, broker_ids)
    providers = generate_providers(num_providers)

    print(f"Generating {num_enrollees:,} Nigerian enrollees with household structures...")
    t0_enr = time.time()
    enrollees = generate_enrollees(num_enrollees, groups, plans, providers)
    print(f"  Enrollees generated in {time.time() - t0_enr:.2f}s (Total: {len(enrollees):,})")

    # Step 3: Transactions
    print("Generating premium invoices and capitation disbursements...")
    invoices = generate_premium_invoices(groups)
    capitations = generate_capitation_payments(providers, enrollees)

    print(f"Generating {num_claims:,} claims and itemized claim lines...")
    t0_claims = time.time()
    claims, claim_lines, preauths, referrals = generate_claims_and_lines(
        num_claims, enrollees, providers, tariffs, drugs
    )
    print(f"  Claims & lines generated in {time.time() - t0_claims:.2f}s (Claims: {len(claims):,}, Lines: {len(claim_lines):,})")

    # Step 4: Operations & Risk
    print("Generating complaints and SIU audit flags...")
    complaints = generate_complaints_tickets(num_complaints, enrollees, providers)
    audit_flags = generate_audit_flags(num_audit_flags, claims)

    # Master table inventory
    tables_data = [
        ("brokers", brokers),
        ("plans", plans),
        ("groups", groups),
        ("providers", providers),
        ("tariff_schedule", tariffs),
        ("drug_formulary", drugs),
        ("icd10_subset", icd_rows),
        ("enrollees", enrollees),
        ("premium_invoices", invoices),
        ("capitation_payments", capitations),
        ("preauthorizations", preauths),
        ("claims", claims),
        ("claim_lines", claim_lines),
        ("referrals", referrals),
        ("complaints_tickets", complaints),
        ("audit_flags", audit_flags)
    ]

    total_rows = sum(len(records) for _, records in tables_data)

    # Step 5: Database Persistence
    if export_sqlite and conn:
        print("\nPersisting records to SQLite database...")
        t0_db = time.time()
        for tbl_name, records in tables_data:
            insert_batch(conn, tbl_name, records)
        print(f"  SQLite batch inserts committed in {time.time() - t0_db:.2f}s")

    # Step 6: CSV Export
    if export_csv and conn:
        print(f"\nExporting all 16 tables to CSV in '{csv_dir}/'...")
        t0_csv = time.time()
        os.makedirs(csv_dir, exist_ok=True)
        for tbl_name, _ in tables_data:
            csv_path = os.path.join(csv_dir, f"{tbl_name}.csv")
            export_table_to_csv(conn, tbl_name, csv_path)
        print(f"  CSV export completed in {time.time() - t0_csv:.2f}s")

    if conn:
        conn.close()

    elapsed = time.time() - start_time
    print("\n" + "=" * 60)
    print(f"GENERATION COMPLETE - SUMMARY REPORT")
    print("=" * 60)
    for tbl_name, records in tables_data:
        print(f"  - {tbl_name:<24}: {len(records):>10,} rows")
    print("-" * 60)
    print(f"  TOTAL RECORDS GENERATED    : {total_rows:>10,} rows")
    print(f"  ELAPSED TIME               : {elapsed:>10.2f} seconds")
    print(f"  THROUGHPUT                 : {total_rows / elapsed:>10,.0f} rows/second")
    print("=" * 60)

    return total_rows

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic Nigerian HMO health insurance datasets")
    parser.add_argument("--scale", choices=["full", "sample", "test"], default="full", help="Data generation scale")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--db-path", default="nigerian_hmo.db", help="SQLite database output path")
    parser.add_argument("--csv-dir", default="data", help="Directory for CSV exports")
    parser.add_argument("--no-csv", action="store_true", help="Skip CSV export")
    parser.add_argument("--no-sqlite", action="store_true", help="Skip SQLite database creation")

    args = parser.parse_args()

    run_generation(
        scale=args.scale,
        seed=args.seed,
        db_path=args.db_path,
        csv_dir=args.csv_dir,
        export_csv=not args.no_csv,
        export_sqlite=not args.no_sqlite
    )
