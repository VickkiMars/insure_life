"""Unit tests for Nigerian HMO synthetic data generation suite."""

import os
import unittest
import sqlite3
import tempfile
from src.reference_data import generate_geography_and_icd10, generate_tariff_schedule, generate_drug_formulary
from src.entities import generate_brokers, generate_plans, generate_groups, generate_providers, generate_enrollees
from src.transactions import generate_premium_invoices, generate_capitation_payments, generate_claims_and_lines
from src.operations import generate_complaints_tickets, generate_audit_flags
from generate import run_generation

class TestNigerianHMOGenerator(unittest.TestCase):

    def test_reference_data_integrity(self):
        geo_rows, icd_rows = generate_geography_and_icd10()
        self.assertGreater(len(geo_rows), 30)
        self.assertGreater(len(icd_rows), 10)

        # Check malaria presence
        malaria = [i for i in icd_rows if i["icd10_code"] == "B50.9"]
        self.assertEqual(len(malaria), 1)
        self.assertEqual(malaria[0]["is_rainy_seasonal"], 1)

        # Check tariffs and inflation
        tariffs = generate_tariff_schedule()
        self.assertGreater(len(tariffs), 100)
        # Check 2025 prices are higher than 2023
        p_2023 = [t["price_ngn"] for t in tariffs if t["service_code"] == "CONS-GP-01" and t["facility_level"] == "Primary" and t["tariff_year"] == 2023][0]
        p_2025 = [t["price_ngn"] for t in tariffs if t["service_code"] == "CONS-GP-01" and t["facility_level"] == "Primary" and t["tariff_year"] == 2025][0]
        self.assertGreater(p_2025, p_2023)

    def test_household_structure(self):
        providers = generate_providers(20)
        plans = generate_plans()
        groups = generate_groups(10)
        enrollees = generate_enrollees(200, groups, plans, providers)

        principals = {e["enrollee_id"] for e in enrollees if e["principal_flag"] == 1}
        self.assertGreater(len(principals), 30)

        for e in enrollees:
            if e["principal_flag"] == 0:
                self.assertIn(e["relationship"], ("SPOUSE", "CHILD"))
                self.assertIn(e["principal_id"], principals)
            else:
                self.assertEqual(e["relationship"], "PRINCIPAL")
                self.assertIsNone(e["principal_id"])

    def test_claims_and_billing_sanity(self):
        providers = generate_providers(20)
        plans = generate_plans()
        groups = generate_groups(10)
        enrollees = generate_enrollees(100, groups, plans, providers)
        tariffs = generate_tariff_schedule()
        drugs = generate_drug_formulary()

        claims, claim_lines, preauths, referrals = generate_claims_and_lines(
            50, enrollees, providers, tariffs, drugs
        )

        self.assertEqual(len(claims), 50)
        self.assertGreater(len(claim_lines), 50)

        claim_map = {c["claim_id"]: c for c in claims}
        for cl in claim_lines:
            self.assertIn(cl["claim_id"], claim_map)
            self.assertLessEqual(cl["approved_amount"], cl["billed_amount"])

        for c in claims:
            self.assertLessEqual(c["total_approved"], c["total_billed"])
            self.assertGreaterEqual(c["total_billed"], 0.0)

    def test_end_to_end_test_scale_generation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            test_db = os.path.join(tmpdir, "test_hmo.db")
            test_csv_dir = os.path.join(tmpdir, "csv")

            total_records = run_generation(
                scale="test",
                seed=123,
                db_path=test_db,
                csv_dir=test_csv_dir,
                export_csv=True,
                export_sqlite=True
            )

            self.assertGreater(total_records, 50000)
            self.assertTrue(os.path.exists(test_db))
            self.assertTrue(os.path.exists(os.path.join(test_csv_dir, "enrollees.csv")))
            self.assertTrue(os.path.exists(os.path.join(test_csv_dir, "claims.csv")))
            self.assertTrue(os.path.exists(os.path.join(test_csv_dir, "claim_lines.csv")))

            conn = sqlite3.connect(test_db)
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) FROM enrollees;")
            enr_count = cursor.fetchone()[0]
            self.assertGreater(enr_count, 5000)
            conn.close()

if __name__ == "__main__":
    unittest.main()
