"""Operational and risk data generators: complaints tickets and SIU audit flags."""

import random
import datetime

def generate_complaints_tickets(target_count: int, enrollees: list, providers: list):
    """Generates enrollee grievance and customer care service tickets."""
    categories = [
        ("Provider Demanded Out-of-Pocket Payment", 0.30),
        ("Provider Refusal to Dispense Prescribed Drugs", 0.25),
        ("Delay in Secondary Pre-Authorization Approval", 0.18),
        ("Delay in Physical HMO Card Delivery", 0.12),
        ("Wrong Primary Care Provider Assigned", 0.08),
        ("Hospital Staff Unprofessional Conduct", 0.07)
    ]
    cat_names = [c[0] for c in categories]
    cat_weights = [c[1] for c in categories]

    priorities = ["Medium", "High", "Critical", "Low"]
    priority_weights = [0.55, 0.25, 0.12, 0.08]

    provider_ids = [p["provider_id"] for p in providers]

    tickets = []
    for i in range(1, target_count + 1):
        enrollee = random.choice(enrollees)
        e_id = enrollee["enrollee_id"]
        category = random.choices(cat_names, weights=cat_weights)[0]
        priority = random.choices(priorities, weights=priority_weights)[0]
        p_id = enrollee["primary_care_provider_id"] if random.random() < 0.85 else random.choice(provider_ids)

        opened_dt = datetime.date(2023, 1, 1) + datetime.timedelta(days=random.randint(0, 1000))
        # 88% resolved, 12% in progress
        is_resolved = random.random() < 0.88
        if is_resolved:
            res_days = random.randint(1, 14)
            resolved_dt = (opened_dt + datetime.timedelta(days=res_days)).isoformat()
            status = "Resolved"
            notes = f"Investigated with hospital admin. {category.split()[0]} resolved and enrollee notified."
        else:
            resolved_dt = None
            status = random.choice(["In Progress", "Escalated to Medical Director", "Awaiting Provider Response"])
            notes = "Case actively being reviewed by HMO Quality Assurance team."

        tickets.append({
            "ticket_id": f"TCK-{i:07d}",
            "enrollee_id": e_id,
            "provider_id": p_id,
            "category": category,
            "status": status,
            "priority": priority,
            "opened_date": opened_dt.isoformat(),
            "resolved_date": resolved_dt,
            "resolution_notes": notes
        })

    return tickets

def generate_audit_flags(target_count: int, claims: list):
    """
    Generates Special Investigation Unit (SIU) fraud, waste, and abuse audit flags.
    Targets a realistic subset of claims with forensic patterns:
    - Impossible diagnosis for sex
    - Upcoding
    - Duplicate billing
    - Service billing after discharge
    - Ghost enrollee billing
    """
    flag_rules = [
        ("Impossible Sex-Diagnosis", "Critical", "Rule-101: Diagnosis code sex restriction contradicts enrollee registered sex", 0.15),
        ("Upcoding and Level Inflation", "High", "Rule-204: Routine primary malaria billed at complex tertiary tariff schedule", 0.35),
        ("Duplicate Claim Submission", "Medium", "Rule-305: Identical service code and enrollee billed within 48 hours", 0.25),
        ("Unbundled Lab Panels", "Medium", "Rule-402: Component lab tests billed separately instead of standard composite panel", 0.15),
        ("Post-Discharge Encounter Date", "High", "Rule-501: Claim itemized line date exceeds documented patient discharge", 0.10)
    ]
    rule_names = [r[0] for r in flag_rules]
    rule_weights = [r[3] for r in flag_rules]
    rule_meta = {r[0]: (r[1], r[2]) for r in flag_rules}

    outcomes = [
        ("Amount Fully Recovered / Deducted", 0.50),
        ("Provider Sanctioned & Warning Issued", 0.20),
        ("Justified Clinical Exception (False Positive)", 0.20),
        ("Under Active Investigation", 0.10)
    ]
    out_names = [o[0] for o in outcomes]
    out_weights = [o[1] for o in outcomes]

    # Sample claims to flag
    sample_claims = random.sample(claims, min(target_count, len(claims)))

    flags = []
    for i, claim in enumerate(sample_claims, 1):
        rule_choice = random.choices(rule_names, weights=rule_weights)[0]
        severity, detection_rule = rule_meta[rule_choice]
        outcome = random.choices(out_names, weights=out_weights)[0]

        billed = claim["total_billed"]
        at_risk = round(billed * random.uniform(0.35, 1.0), 2)
        flag_dt = datetime.date.fromisoformat(claim["submission_date"]) + datetime.timedelta(days=random.randint(2, 20))

        flags.append({
            "flag_id": f"FLG-{i:07d}",
            "claim_id": claim["claim_id"],
            "flag_type": rule_choice,
            "severity": severity,
            "detection_rule": detection_rule,
            "amount_at_risk": at_risk,
            "investigation_outcome": outcome,
            "flagged_date": flag_dt.isoformat()
        })

    return flags
