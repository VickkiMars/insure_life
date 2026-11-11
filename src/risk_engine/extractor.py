"""Extracts Day-0 intake snapshots joined with ground-truth Year-1 claims from SQLite."""

import sqlite3
from typing import List, Dict, Any, Tuple

DAY0_QUERY = """
SELECT 
    e.enrollee_id,
    CAST((strftime('%Y', e.enrolment_date) - strftime('%Y', e.dob)) AS INTEGER) AS age,
    e.sex,
    e.relationship,
    e.state,
    e.lga,
    e.scheme_type,
    COALESCE(g.sector, 'Retail / Individual') AS sector,
    p.tier AS plan_tier,
    p.co_pay_pct,
    prv.level AS pcp_level,
    e.enrolment_date,
    COALESCE(SUM(c.total_billed), 0.0) AS year1_claims_cost,
    COUNT(c.claim_id) AS year1_claim_count,
    COALESCE(MAX(CASE WHEN c.encounter_type = 'Inpatient' THEN 1 ELSE 0 END), 0) AS year1_had_inpatient,
    CASE WHEN COALESCE(SUM(c.total_billed), 0.0) >= 150000.0 THEN 1 ELSE 0 END AS year1_high_risk_flag
FROM enrollees e
LEFT JOIN groups g ON e.group_id = g.group_id
JOIN plans p ON e.plan_id = p.plan_id
JOIN providers prv ON e.primary_care_provider_id = prv.provider_id
LEFT JOIN claims c ON e.enrollee_id = c.enrollee_id 
    AND julianday(c.admission_date) >= julianday(e.enrolment_date)
    AND julianday(c.admission_date) < julianday(e.enrolment_date, '+365 days')
GROUP BY e.enrollee_id
ORDER BY e.enrolment_date ASC;
"""

def extract_day0_dataset(db_path: str = "nigerian_hmo.db", limit: int = None) -> List[Dict[str, Any]]:
    """
    Queries the database and returns a list of dictionaries containing
    Day-0 onboarding features along with Year-1 downstream targets.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    query = DAY0_QUERY if limit is None else DAY0_QUERY.replace(";", f" LIMIT {limit};")
    cursor.execute(query)

    columns = [
        "enrollee_id", "age", "sex", "relationship", "state", "lga",
        "scheme_type", "sector", "plan_tier", "co_pay_pct", "pcp_level",
        "enrolment_date", "year1_claims_cost", "year1_claim_count",
        "year1_had_inpatient", "year1_high_risk_flag"
    ]

    records = []
    for row in cursor.fetchall():
        records.append(dict(zip(columns, row)))

    conn.close()
    return records
