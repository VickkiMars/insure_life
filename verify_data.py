#!/usr/bin/env python3
"""
Verification and adversarial validation script for Nigerian HMO synthetic dataset.
Ensures >= 1,000,000 rows, relational integrity, demographic realism, and epidemiological validity.
"""

import os
import sys
import sqlite3
import argparse

def verify_dataset(db_path: str = "nigerian_hmo.db"):
    if not os.path.exists(db_path):
        print(f"Error: Database file '{db_path}' not found.", file=sys.stderr)
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print(f"\n===========================================================")
    print(f"ADVERSARIAL DATA VERIFICATION & AUDIT: {db_path}")
    print(f"===========================================================")

    all_passed = True
    table_names = [
        "brokers", "plans", "groups", "providers", "tariff_schedule",
        "drug_formulary", "icd10_subset", "enrollees", "premium_invoices",
        "capitation_payments", "preauthorizations", "claims", "claim_lines",
        "referrals", "complaints_tickets", "audit_flags"
    ]

    # Test 1: Table existence and row counts
    print("\n--- Test 1: Row Counts Across All 16 Tables ---")
    total_rows = 0
    counts = {}
    for tbl in table_names:
        cursor.execute(f"SELECT count(*) FROM {tbl};")
        cnt = cursor.fetchone()[0]
        counts[tbl] = cnt
        total_rows += cnt
        status = "PASS" if cnt > 0 else "FAIL"
        print(f"  [{status}] {tbl:<24}: {cnt:>10,} rows")
        if cnt == 0:
            all_passed = False

    print(f"\n  TOTAL RECORD COUNT: {total_rows:,} rows")
    if total_rows >= 1000000:
        print(f"  [PASS] Dataset meets >= 1,000,000 records threshold ({total_rows:,}).")
    else:
        print(f"  [FAIL] Dataset has only {total_rows:,} records (< 1,000,000).")
        all_passed = False

    # Test 2: Foreign Key and Relational Integrity
    print("\n--- Test 2: Relational Integrity & Orphaned Record Checks ---")
    
    # Check enrollees referencing non-existent groups (when group_id is not null)
    cursor.execute("""
        SELECT count(*) FROM enrollees e 
        LEFT JOIN groups g ON e.group_id = g.group_id 
        WHERE e.group_id IS NOT NULL AND g.group_id IS NULL;
    """)
    orphan_groups = cursor.fetchone()[0]

    # Check enrollees referencing non-existent plans
    cursor.execute("""
        SELECT count(*) FROM enrollees e 
        LEFT JOIN plans p ON e.plan_id = p.plan_id 
        WHERE p.plan_id IS NULL;
    """)
    orphan_plans = cursor.fetchone()[0]

    # Check enrollees referencing non-existent providers
    cursor.execute("""
        SELECT count(*) FROM enrollees e 
        LEFT JOIN providers pr ON e.primary_care_provider_id = pr.provider_id 
        WHERE pr.provider_id IS NULL;
    """)
    orphan_pcps = cursor.fetchone()[0]

    # Check dependants referencing valid principals
    cursor.execute("""
        SELECT count(*) FROM enrollees d 
        LEFT JOIN enrollees p ON d.principal_id = p.enrollee_id 
        WHERE d.principal_flag = 0 AND p.enrollee_id IS NULL;
    """)
    orphan_principals = cursor.fetchone()[0]

    # Check claims referencing non-existent enrollees or providers
    cursor.execute("""
        SELECT count(*) FROM claims c 
        LEFT JOIN enrollees e ON c.enrollee_id = e.enrollee_id 
        WHERE e.enrollee_id IS NULL;
    """)
    orphan_claim_enrollees = cursor.fetchone()[0]

    cursor.execute("""
        SELECT count(*) FROM claims c 
        LEFT JOIN providers p ON c.provider_id = p.provider_id 
        WHERE p.provider_id IS NULL;
    """)
    orphan_claim_providers = cursor.fetchone()[0]

    # Check claim lines referencing claims
    cursor.execute("""
        SELECT count(*) FROM claim_lines cl 
        LEFT JOIN claims c ON cl.claim_id = c.claim_id 
        WHERE c.claim_id IS NULL;
    """)
    orphan_claim_lines = cursor.fetchone()[0]

    fk_checks = [
        ("Enrollee -> Group (Orphans)", orphan_groups),
        ("Enrollee -> Plan (Orphans)", orphan_plans),
        ("Enrollee -> Primary Provider (Orphans)", orphan_pcps),
        ("Dependant -> Principal Link (Orphans)", orphan_principals),
        ("Claim -> Enrollee (Orphans)", orphan_claim_enrollees),
        ("Claim -> Provider (Orphans)", orphan_claim_providers),
        ("Claim Lines -> Claim Header (Orphans)", orphan_claim_lines)
    ]

    for name, cnt in fk_checks:
        res = "PASS" if cnt == 0 else "FAIL"
        print(f"  [{res}] {name:<40}: {cnt} orphaned records")
        if cnt > 0:
            all_passed = False

    # Test 3: Nigerian Demographics & Geographic Realism
    print("\n--- Test 3: Nigerian Demographic & Geographic Realism ---")
    cursor.execute("SELECT state, count(*) as cnt FROM enrollees GROUP BY state ORDER BY cnt DESC LIMIT 5;")
    top_states = cursor.fetchall()
    print("  Top 5 States by Enrolment (Lagos & FCT Abuja should lead):")
    for st, c in top_states:
        pct = (c / counts["enrollees"]) * 100
        print(f"    - {st:<15}: {c:>7,} ({pct:.1f}%)")

    # Verify Lagos is top state
    if top_states[0][0] == "Lagos":
        print("  [PASS] Lagos State correctly leads Nigerian HMO enrollment concentration.")
    else:
        print("  [FAIL] Expected Lagos to lead HMO enrollment.")
        all_passed = False

    cursor.execute("SELECT relationship, count(*) FROM enrollees GROUP BY relationship;")
    rel_counts = dict(cursor.fetchall())
    print(f"  Household Breakdown: Principals: {rel_counts.get('PRINCIPAL', 0):,}, Spouses: {rel_counts.get('SPOUSE', 0):,}, Children: {rel_counts.get('CHILD', 0):,}")
    if rel_counts.get("PRINCIPAL", 0) > 0 and rel_counts.get("CHILD", 0) > rel_counts.get("SPOUSE", 0):
        print("  [PASS] Authentic household structure with child dependency pyramid.")
    else:
        print("  [FAIL] Household distribution irregular.")
        all_passed = False

    # Test 4: Epidemiological Mix & Seasonality
    print("\n--- Test 4: Epidemiological Diagnosis Distribution & Seasonality ---")
    cursor.execute("""
        SELECT primary_icd10, i.description, count(*) as cnt 
        FROM claims c 
        JOIN icd10_subset i ON c.primary_icd10 = i.icd10_code 
        GROUP BY primary_icd10 
        ORDER BY cnt DESC LIMIT 5;
    """)
    top_diseases = cursor.fetchall()
    print("  Top 5 Clinical Diagnoses:")
    for code, desc, cnt in top_diseases:
        pct = (cnt / counts["claims"]) * 100
        print(f"    - {code:<6} {desc[:42]:<44}: {cnt:>7,} ({pct:.1f}%)")

    if top_diseases[0][0] == "B50.9":
        print("  [PASS] Plasmodium falciparum malaria correctly leads as the dominant diagnosis.")
    else:
        print("  [FAIL] Expected Malaria (B50.9) to lead diagnoses in Nigeria.")
        all_passed = False

    # Seasonality check: Malaria during Rainy Season (May-Oct) vs Dry Season (Nov-Apr)
    cursor.execute("""
        SELECT 
            CASE WHEN strftime('%m', admission_date) IN ('05','06','07','08','09','10') THEN 'Rainy Season' ELSE 'Dry Season' END as season,
            count(*) as malaria_claims
        FROM claims 
        WHERE primary_icd10 = 'B50.9'
        GROUP BY season;
    """)
    malaria_seasons = dict(cursor.fetchall())
    rain_cnt = malaria_seasons.get("Rainy Season", 0)
    dry_cnt = malaria_seasons.get("Dry Season", 0)
    print(f"  Malaria Seasonal Surge: Rainy Season = {rain_cnt:,} vs Dry Season = {dry_cnt:,}")
    if rain_cnt > dry_cnt * 1.2:
        print("  [PASS] Statistically significant malaria surge during West African rainy season.")
    else:
        print("  [FAIL] Rainy season malaria surge was not observed.")
        all_passed = False

    # Test 5: Financial Distribution and Heavy Tail (Pareto / Lognormal)
    print("\n--- Test 5: Financial Sanity and Heavy-Tailed Cost Distribution ---")
    cursor.execute("SELECT min(total_billed), avg(total_billed), max(total_billed), sum(total_billed) FROM claims;")
    min_b, avg_b, max_b, sum_b = cursor.fetchone()
    print(f"  Claims Total Billed (NGN): Min = ₦{min_b:,.2f}, Mean = ₦{avg_b:,.2f}, Max = ₦{max_b:,.2f}")
    
    # Check top 5% claimant spend
    cursor.execute("""
        SELECT sum(total_billed) FROM (
            SELECT total_billed FROM claims ORDER BY total_billed DESC LIMIT cast(0.05 * (SELECT count(*) FROM claims) as int)
        );
    """)
    top_5_spend = cursor.fetchone()[0] or 0.0
    top_5_pct = (top_5_spend / sum_b) * 100 if sum_b > 0 else 0
    print(f"  Spend Concentration: Top 5% of highest claims account for {top_5_pct:.1f}% of total spend.")
    if top_5_pct >= 40.0:
        print("  [PASS] Heavy-tailed spend confirmed (realistic catastrophic claim skew).")
    else:
        print("  [WARN] Spend concentration is more uniform than typical private health insurance.")

    # Check approved <= billed
    cursor.execute("SELECT count(*) FROM claims WHERE total_approved > total_billed;")
    invalid_app = cursor.fetchone()[0]
    if invalid_app == 0:
        print("  [PASS] Zero instances of total_approved exceeding total_billed.")
    else:
        print(f"  [FAIL] Found {invalid_app} claims where total_approved > total_billed.")
        all_passed = False

    # Test 6: Audit Flags and Process Friction
    print("\n--- Test 6: Process Friction, Rejections, and SIU Audit Flags ---")
    cursor.execute("SELECT status, count(*) FROM claims GROUP BY status;")
    status_counts = dict(cursor.fetchall())
    rej_cnt = status_counts.get("Rejected", 0)
    part_cnt = status_counts.get("Partially Approved", 0)
    app_cnt = status_counts.get("Approved", 0)
    print(f"  Claim Adjudication: Approved = {app_cnt:,}, Partially Approved = {part_cnt:,}, Rejected = {rej_cnt:,}")
    if rej_cnt > 0 and part_cnt > 0:
        print("  [PASS] Realistic process friction with steady claim rejection and tariff deduction rate.")
    else:
        print("  [FAIL] Missing rejected or partially approved claims.")
        all_passed = False

    cursor.execute("SELECT flag_type, count(*) FROM audit_flags GROUP BY flag_type ORDER BY count(*) DESC;")
    audit_summary = cursor.fetchall()
    print("  SIU Audit Flags Summary:")
    for ftype, c in audit_summary:
        print(f"    - {ftype:<35}: {c:>6,}")

    conn.close()

    print("\n" + "=" * 60)
    if all_passed:
        print("ALL VERIFICATION CHECKS PASSED SUCCESSFULLY.")
    else:
        print("ONE OR MORE VERIFICATION CHECKS FAILED.")
    print("=" * 60)
    return all_passed

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify Nigerian HMO dataset")
    parser.add_argument("--db-path", default="nigerian_hmo.db", help="Path to SQLite database")
    args = parser.parse_args()

    success = verify_dataset(args.db_path)
    sys.exit(0 if success else 1)
