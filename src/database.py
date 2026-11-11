"""Database schema definition and high-speed SQLite batch persistence."""

import os
import sqlite3
import csv

DDL_STATEMENTS = [
    # 1. Brokers
    """
    CREATE TABLE IF NOT EXISTS brokers (
        broker_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        commission_rate REAL NOT NULL,
        license_number TEXT NOT NULL,
        state TEXT NOT NULL
    );
    """,

    # 2. Plans
    """
    CREATE TABLE IF NOT EXISTS plans (
        plan_id TEXT PRIMARY KEY,
        tier TEXT NOT NULL,
        premium_per_head REAL NOT NULL,
        annual_limit REAL NOT NULL,
        co_pay_pct REAL NOT NULL,
        waiting_periods INTEGER NOT NULL,
        exclusions TEXT NOT NULL,
        referral_rules TEXT NOT NULL
    );
    """,

    # 3. Groups (Corporate & Government Clients)
    """
    CREATE TABLE IF NOT EXISTS groups (
        group_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        sector TEXT NOT NULL,
        headcount INTEGER NOT NULL,
        contract_start TEXT NOT NULL,
        contract_renewal TEXT NOT NULL,
        broker_id TEXT,
        negotiated_premium_head REAL NOT NULL,
        FOREIGN KEY (broker_id) REFERENCES brokers (broker_id)
    );
    """,

    # 4. Providers (Healthcare facilities)
    """
    CREATE TABLE IF NOT EXISTS providers (
        provider_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        level TEXT NOT NULL,
        ownership TEXT NOT NULL,
        state TEXT NOT NULL,
        lga TEXT NOT NULL,
        specialties TEXT NOT NULL,
        accreditation_status TEXT NOT NULL,
        contract_type TEXT NOT NULL
    );
    """,

    # 5. Enrollees
    """
    CREATE TABLE IF NOT EXISTS enrollees (
        enrollee_id TEXT PRIMARY KEY,
        principal_flag INTEGER NOT NULL,
        principal_id TEXT,
        relationship TEXT NOT NULL,
        dob TEXT NOT NULL,
        sex TEXT NOT NULL,
        state TEXT NOT NULL,
        lga TEXT NOT NULL,
        scheme_type TEXT NOT NULL,
        group_id TEXT,
        plan_id TEXT NOT NULL,
        primary_care_provider_id TEXT NOT NULL,
        enrolment_date TEXT NOT NULL,
        status TEXT NOT NULL,
        nin TEXT,
        phone_number TEXT,
        FOREIGN KEY (principal_id) REFERENCES enrollees (enrollee_id),
        FOREIGN KEY (group_id) REFERENCES groups (group_id),
        FOREIGN KEY (plan_id) REFERENCES plans (plan_id),
        FOREIGN KEY (primary_care_provider_id) REFERENCES providers (provider_id)
    );
    """,

    # 6. Tariff Schedule
    """
    CREATE TABLE IF NOT EXISTS tariff_schedule (
        tariff_id TEXT PRIMARY KEY,
        service_code TEXT NOT NULL,
        service_type TEXT NOT NULL,
        description TEXT NOT NULL,
        facility_level TEXT NOT NULL,
        tariff_year INTEGER NOT NULL,
        price_ngn REAL NOT NULL,
        effective_date TEXT NOT NULL
    );
    """,

    # 7. Drug Formulary
    """
    CREATE TABLE IF NOT EXISTS drug_formulary (
        drug_id TEXT PRIMARY KEY,
        brand_or_label TEXT NOT NULL,
        generic_name TEXT NOT NULL,
        dosage_form TEXT NOT NULL,
        unit_price_ngn REAL NOT NULL,
        is_covered INTEGER NOT NULL,
        requires_preauth INTEGER NOT NULL
    );
    """,

    # 8. ICD-10 Reference
    """
    CREATE TABLE IF NOT EXISTS icd10_subset (
        icd10_code TEXT PRIMARY KEY,
        description TEXT NOT NULL,
        category TEXT NOT NULL,
        base_weight REAL NOT NULL,
        sex_restriction TEXT NOT NULL,
        min_age INTEGER NOT NULL,
        max_age INTEGER NOT NULL,
        severity TEXT NOT NULL,
        is_rainy_seasonal INTEGER NOT NULL
    );
    """,

    # 9. Premium Invoices and Payments
    """
    CREATE TABLE IF NOT EXISTS premium_invoices (
        invoice_id TEXT PRIMARY KEY,
        group_id TEXT NOT NULL,
        period TEXT NOT NULL,
        amount_billed REAL NOT NULL,
        amount_paid REAL NOT NULL,
        payment_date TEXT,
        arrears REAL NOT NULL,
        payment_channel TEXT NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (group_id) REFERENCES groups (group_id)
    );
    """,

    # 10. Capitation Payments
    """
    CREATE TABLE IF NOT EXISTS capitation_payments (
        capitation_id TEXT PRIMARY KEY,
        provider_id TEXT NOT NULL,
        month TEXT NOT NULL,
        enrollees_assigned INTEGER NOT NULL,
        rate_per_head REAL NOT NULL,
        total_amount REAL NOT NULL,
        payment_date TEXT NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (provider_id) REFERENCES providers (provider_id)
    );
    """,

    # 11. Preauthorizations
    """
    CREATE TABLE IF NOT EXISTS preauthorizations (
        auth_id TEXT PRIMARY KEY,
        enrollee_id TEXT NOT NULL,
        provider_id TEXT NOT NULL,
        requested_service TEXT NOT NULL,
        icd10_code TEXT NOT NULL,
        requested_amount REAL NOT NULL,
        approved_amount REAL NOT NULL,
        status TEXT NOT NULL,
        turnaround_hours INTEGER NOT NULL,
        denial_reason TEXT,
        request_date TEXT NOT NULL,
        decision_date TEXT NOT NULL,
        FOREIGN KEY (enrollee_id) REFERENCES enrollees (enrollee_id),
        FOREIGN KEY (provider_id) REFERENCES providers (provider_id),
        FOREIGN KEY (icd10_code) REFERENCES icd10_subset (icd10_code)
    );
    """,

    # 12. Claims (Header)
    """
    CREATE TABLE IF NOT EXISTS claims (
        claim_id TEXT PRIMARY KEY,
        enrollee_id TEXT NOT NULL,
        provider_id TEXT NOT NULL,
        encounter_type TEXT NOT NULL,
        admission_date TEXT NOT NULL,
        discharge_date TEXT NOT NULL,
        primary_icd10 TEXT NOT NULL,
        secondary_icd10 TEXT,
        submission_date TEXT NOT NULL,
        batch_id TEXT NOT NULL,
        total_billed REAL NOT NULL,
        total_approved REAL NOT NULL,
        total_paid REAL NOT NULL,
        status TEXT NOT NULL,
        rejection_reason TEXT,
        adjudication_date TEXT NOT NULL,
        payment_date TEXT,
        FOREIGN KEY (enrollee_id) REFERENCES enrollees (enrollee_id),
        FOREIGN KEY (provider_id) REFERENCES providers (provider_id),
        FOREIGN KEY (primary_icd10) REFERENCES icd10_subset (icd10_code)
    );
    """,

    # 13. Claim Lines (Itemized)
    """
    CREATE TABLE IF NOT EXISTS claim_lines (
        line_id TEXT PRIMARY KEY,
        claim_id TEXT NOT NULL,
        line_type TEXT NOT NULL,
        service_code TEXT NOT NULL,
        description TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        billed_amount REAL NOT NULL,
        approved_amount REAL NOT NULL,
        FOREIGN KEY (claim_id) REFERENCES claims (claim_id)
    );
    """,

    # 14. Referrals
    """
    CREATE TABLE IF NOT EXISTS referrals (
        referral_id TEXT PRIMARY KEY,
        enrollee_id TEXT NOT NULL,
        from_provider_id TEXT NOT NULL,
        to_provider_id TEXT NOT NULL,
        reason TEXT NOT NULL,
        referral_date TEXT NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (enrollee_id) REFERENCES enrollees (enrollee_id),
        FOREIGN KEY (from_provider_id) REFERENCES providers (provider_id),
        FOREIGN KEY (to_provider_id) REFERENCES providers (provider_id)
    );
    """,

    # 15. Complaints / Service Tickets
    """
    CREATE TABLE IF NOT EXISTS complaints_tickets (
        ticket_id TEXT PRIMARY KEY,
        enrollee_id TEXT NOT NULL,
        provider_id TEXT,
        category TEXT NOT NULL,
        status TEXT NOT NULL,
        priority TEXT NOT NULL,
        opened_date TEXT NOT NULL,
        resolved_date TEXT,
        resolution_notes TEXT,
        FOREIGN KEY (enrollee_id) REFERENCES enrollees (enrollee_id),
        FOREIGN KEY (provider_id) REFERENCES providers (provider_id)
    );
    """,

    # 16. Audit Flags (SIU Fraud, Waste & Abuse)
    """
    CREATE TABLE IF NOT EXISTS audit_flags (
        flag_id TEXT PRIMARY KEY,
        claim_id TEXT NOT NULL,
        flag_type TEXT NOT NULL,
        severity TEXT NOT NULL,
        detection_rule TEXT NOT NULL,
        amount_at_risk REAL NOT NULL,
        investigation_outcome TEXT NOT NULL,
        flagged_date TEXT NOT NULL,
        FOREIGN KEY (claim_id) REFERENCES claims (claim_id)
    );
    """
]

INDEX_STATEMENTS = [
    "CREATE INDEX IF NOT EXISTS idx_enrollees_group ON enrollees (group_id);",
    "CREATE INDEX IF NOT EXISTS idx_enrollees_pcp ON enrollees (primary_care_provider_id);",
    "CREATE INDEX IF NOT EXISTS idx_claims_enrollee ON claims (enrollee_id);",
    "CREATE INDEX IF NOT EXISTS idx_claims_provider ON claims (provider_id);",
    "CREATE INDEX IF NOT EXISTS idx_claims_date ON claims (admission_date);",
    "CREATE INDEX IF NOT EXISTS idx_claim_lines_claim ON claim_lines (claim_id);",
    "CREATE INDEX IF NOT EXISTS idx_audit_flags_claim ON audit_flags (claim_id);"
]

def init_db(db_path: str) -> sqlite3.Connection:
    """Initializes SQLite database with schema and high-performance write settings."""
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA synchronous = OFF;")
    conn.execute("PRAGMA journal_mode = MEMORY;")
    conn.execute("PRAGMA temp_store = MEMORY;")
    conn.execute("PRAGMA cache_size = -128000;")  # 128MB cache

    for stmt in DDL_STATEMENTS:
        conn.execute(stmt)

    for stmt in INDEX_STATEMENTS:
        conn.execute(stmt)

    conn.commit()
    return conn

def insert_batch(conn: sqlite3.Connection, table_name: str, records: list):
    """Executes fast batch insert for a list of dictionaries into a table."""
    if not records:
        return
    keys = list(records[0].keys())
    placeholders = ",".join(["?"] * len(keys))
    sql = f"INSERT INTO {table_name} ({','.join(keys)}) VALUES ({placeholders})"
    values = [[rec[k] for k in keys] for rec in records]
    conn.executemany(sql, values)
    conn.commit()

def export_table_to_csv(conn: sqlite3.Connection, table_name: str, csv_path: str):
    """Exports SQLite table contents to a CSV file."""
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    col_names = [desc[0] for desc in cursor.description]

    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(col_names)
        while True:
            rows = cursor.fetchmany(10000)
            if not rows:
                break
            writer.writerows(rows)
