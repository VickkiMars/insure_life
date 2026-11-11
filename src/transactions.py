"""Transaction generators: invoices, capitation, preauthorizations, claims, claim_lines, and referrals."""

import random
import datetime
from src.config import START_DATE, END_DATE, ICD10_DATA

def generate_premium_invoices(groups: list):
    """Generates monthly billing cycles and payment records for corporate groups."""
    invoices = []
    inv_counter = 1
    channels = ["NIBSS Instant Payment (NIP)", "Remita e-Payment", "Direct Bank Debit", "Corporate Bank Transfer", "Bank Draft / Cheque"]
    channel_weights = [0.45, 0.30, 0.15, 0.08, 0.02]

    # Generate invoices for each month from 2023 to 2025 (36 months)
    for g in groups:
        g_id = g["group_id"]
        headcount = g["headcount"]
        prem_per_head = g["negotiated_premium_head"]
        monthly_billed = round((headcount * prem_per_head) / 12.0, 2)

        curr_year = START_DATE.year
        curr_month = START_DATE.month

        while (curr_year < END_DATE.year) or (curr_year == END_DATE.year and curr_month <= END_DATE.month):
            period = f"{curr_year}-{curr_month:02d}"
            inv_date = datetime.date(curr_year, curr_month, 5)

            # Collection behavior: 85% paid on time, 10% partial/late, 5% arrears
            roll = random.random()
            if roll < 0.85:
                paid = monthly_billed
                arrears = 0.0
                pay_date = (inv_date + datetime.timedelta(days=random.randint(5, 25))).isoformat()
                status = "Fully Paid"
            elif roll < 0.95:
                paid = round(monthly_billed * random.uniform(0.4, 0.85), 2)
                arrears = round(monthly_billed - paid, 2)
                pay_date = (inv_date + datetime.timedelta(days=random.randint(30, 60))).isoformat()
                status = "Partially Paid"
            else:
                paid = 0.0
                arrears = monthly_billed
                pay_date = None
                status = "Overdue / Arrears"

            channel = random.choices(channels, weights=channel_weights)[0]

            invoices.append({
                "invoice_id": f"INV-{inv_counter:07d}",
                "group_id": g_id,
                "period": period,
                "amount_billed": monthly_billed,
                "amount_paid": paid,
                "payment_date": pay_date,
                "arrears": arrears,
                "payment_channel": channel,
                "status": status
            })
            inv_counter += 1

            if curr_month == 12:
                curr_month = 1
                curr_year += 1
            else:
                curr_month += 1

    return invoices

def generate_capitation_payments(providers: list, enrollees: list):
    """
    Generates monthly capitation payments for Primary and Secondary providers
    based on the number of enrollees registered to them as PCP.
    """
    # Count enrollees per provider
    pcp_counts = {}
    for e in enrollees:
        if e["status"] == "Active":
            p_id = e["primary_care_provider_id"]
            pcp_counts[p_id] = pcp_counts.get(p_id, 0) + 1

    capitations = []
    cap_counter = 1
    # Monthly capitation rate in NGN (typically 900 - 1800 NGN per enrollee per month in Nigeria)
    base_rate_per_head = 1250.0

    curr_year = START_DATE.year
    curr_month = START_DATE.month

    eligible_providers = [p for p in providers if "Capitation" in p["contract_type"]]

    while (curr_year < END_DATE.year) or (curr_year == END_DATE.year and curr_month <= END_DATE.month):
        period = f"{curr_year}-{curr_month:02d}"
        pay_date = datetime.date(curr_year, curr_month, 2) # Paid in advance at start of month
        # Annual inflation adjustment on capitation rate
        inflation = 1.0 if curr_year == 2023 else (1.15 if curr_year == 2024 else 1.30)
        rate = round(base_rate_per_head * inflation, 2)

        for p in eligible_providers:
            p_id = p["provider_id"]
            assigned = pcp_counts.get(p_id, 0)
            if assigned == 0:
                continue

            total = round(assigned * rate, 2)
            capitations.append({
                "capitation_id": f"CAP-{cap_counter:07d}",
                "provider_id": p_id,
                "month": period,
                "enrollees_assigned": assigned,
                "rate_per_head": rate,
                "total_amount": total,
                "payment_date": pay_date.isoformat(),
                "status": "Disbursed"
            })
            cap_counter += 1

        if curr_month == 12:
            curr_month = 1
            curr_year += 1
        else:
            curr_month += 1

    return capitations

def _get_disease_weights(month: int):
    """
    Applies Nigerian epidemiological seasonality:
    - Rainy season (May - October) surges Malaria, Typhoid, Gastroenteritis.
    - Harmattan season (Dec - Feb) surges URTI.
    """
    weights = []
    for item in ICD10_DATA:
        w = item["base_weight"]
        if item.get("is_rainy_seasonal") and (5 <= month <= 10):
            # Peak rain in July and September
            multiplier = 2.1 if month in (6, 7, 9) else 1.6
            w *= multiplier
        elif item.get("is_harmattan_seasonal") and (month in (12, 1, 2)):
            w *= 1.8
        weights.append(w)
    return weights

def generate_claims_and_lines(
    target_claim_count: int,
    enrollees: list,
    providers: list,
    tariffs: list,
    drugs: list
):
    """
    Generates realistic clinical encounters (claims header) and itemized claim lines.
    Reflects log-normal cost distribution, monthly batching, and payment lags.
    """
    claims = []
    claim_lines = []
    preauths = []
    referrals = []

    # Map tariffs by service code and facility level and year
    tariff_lookup = {}
    for t in tariffs:
        tariff_lookup[(t["service_code"], t["facility_level"], t["tariff_year"])] = t["price_ngn"]

    # Map providers by ID
    provider_map = {p["provider_id"]: p for p in providers}

    # Pre-filter secondary and tertiary providers for referrals
    specialist_providers = [p["provider_id"] for p in providers if p["level"] in ("Secondary", "Tertiary")]

    # Sample claimant pool: heavy-tailed (Pareto principle: ~20% of enrollees drive 80% of claims)
    active_enrollees = [e for e in enrollees if e["status"] != "Terminated"]
    high_utilizers = random.sample(active_enrollees, max(1, int(len(active_enrollees) * 0.15)))

    claim_id_seq = 1
    line_id_seq = 1
    auth_id_seq = 1
    ref_id_seq = 1

    days_in_sim = (END_DATE - START_DATE).days

    while claim_id_seq <= target_claim_count:
        # 70% of claims come from high utilizers, 30% from general pool
        enrollee = random.choice(high_utilizers) if random.random() < 0.70 else random.choice(active_enrollees)
        e_sex = enrollee["sex"]
        e_dob = datetime.date.fromisoformat(enrollee["dob"])

        # Encounter date
        offset_days = random.randint(0, days_in_sim)
        encounter_date = START_DATE + datetime.timedelta(days=offset_days)
        e_age = encounter_date.year - e_dob.year

        # Select ICD-10 condition with seasonality and sex/age constraints
        monthly_weights = _get_disease_weights(encounter_date.month)
        
        # Filter valid conditions for this enrollee
        valid_indices = []
        valid_weights = []
        for idx, item in enumerate(ICD10_DATA):
            if item.get("sex") != "ANY" and item.get("sex") != e_sex:
                continue
            if e_age < item.get("min_age", 0) or e_age > item.get("max_age", 120):
                continue
            valid_indices.append(idx)
            valid_weights.append(monthly_weights[idx])

        if not valid_indices:
            cond_idx = 0
        else:
            cond_idx = random.choices(valid_indices, weights=valid_weights)[0]

        primary_cond = ICD10_DATA[cond_idx]
        primary_icd = primary_cond["code"]

        # Secondary ICD-10 in 15% of cases (comorbidity: e.g. Malaria + Typhoid, or HTN + Diabetes)
        secondary_icd = None
        if random.random() < 0.15:
            sec_idx = random.choice(valid_indices)
            if sec_idx != cond_idx:
                secondary_icd = ICD10_DATA[sec_idx]["code"]

        # Encounter type and facility
        if primary_cond["category"] == "Maternal":
            encounter_type = "Maternity" if primary_icd in ("O80", "O82") else "Outpatient"
        elif primary_cond["category"] == "Trauma":
            encounter_type = "Emergency"
        elif primary_cond.get("severity") == "High" and random.random() < 0.45:
            encounter_type = "Inpatient"
        else:
            encounter_type = "Outpatient"

        # Provider assignment: 65% PCP, 35% specialist / tertiary referral
        if encounter_type in ("Inpatient", "Maternity") or random.random() < 0.35:
            provider_id = random.choice(specialist_providers)
            is_referral = True
        else:
            provider_id = enrollee["primary_care_provider_id"]
            is_referral = False

        provider = provider_map.get(provider_id, providers[0])
        fac_level = provider["level"]
        tariff_year = encounter_date.year

        # Admission & Discharge
        admission_date = encounter_date
        if encounter_type == "Inpatient":
            stay_days = random.randint(2, 7)
            discharge_date = admission_date + datetime.timedelta(days=stay_days)
        elif encounter_type == "Maternity":
            stay_days = 2 if primary_icd == "O80" else 4
            discharge_date = admission_date + datetime.timedelta(days=stay_days)
        else:
            discharge_date = admission_date

        # Generate Referral Record if referred
        if is_referral and random.random() < 0.60:
            referrals.append({
                "referral_id": f"REF-{ref_id_seq:07d}",
                "enrollee_id": enrollee["enrollee_id"],
                "from_provider_id": enrollee["primary_care_provider_id"],
                "to_provider_id": provider_id,
                "reason": f"Secondary care referral for {primary_cond['description']}",
                "referral_date": (admission_date - datetime.timedelta(days=random.randint(1, 7))).isoformat(),
                "status": "Completed"
            })
            ref_id_seq += 1

        # Preauthorization for surgical / high-cost inpatient procedures
        preauth_id = None
        needs_preauth = (primary_icd in ("O82", "PROC-APP-03") or encounter_type == "Inpatient" or fac_level == "Tertiary")
        if needs_preauth:
            req_amt = round(random.uniform(75000, 450000), 2)
            auth_status = random.choices(["Approved", "Denied", "Modified"], weights=[0.82, 0.10, 0.08])[0]
            app_amt = req_amt if auth_status == "Approved" else (round(req_amt * 0.75, 2) if auth_status == "Modified" else 0.0)
            denial = "Non-covered indication under plan tier" if auth_status == "Denied" else None
            req_date = admission_date - datetime.timedelta(days=random.randint(1, 5))
            dec_date = req_date + datetime.timedelta(hours=random.randint(2, 24))

            preauths.append({
                "auth_id": f"ATH-{auth_id_seq:07d}",
                "enrollee_id": enrollee["enrollee_id"],
                "provider_id": provider_id,
                "requested_service": f"Inpatient / Procedure Authorization ({primary_icd})",
                "icd10_code": primary_icd,
                "requested_amount": req_amt,
                "approved_amount": app_amt,
                "status": auth_status,
                "turnaround_hours": random.randint(1, 18),
                "denial_reason": denial,
                "request_date": req_date.isoformat(),
                "decision_date": dec_date.isoformat()
            })
            preauth_id = f"ATH-{auth_id_seq:07d}"
            auth_id_seq += 1

        # Claim Header & Lines Generation
        current_claim_id = f"CLM-{claim_id_seq:08d}"
        claim_id_seq += 1

        # Generate itemized lines for this encounter
        lines_for_claim = []

        # 1. Consultation line
        cons_code = "CONS-SP-02" if fac_level in ("Secondary", "Tertiary") else "CONS-GP-01"
        cons_price = tariff_lookup.get((cons_code, fac_level, tariff_year), 4500.0)
        lines_for_claim.append({
            "line_type": "consultation",
            "service_code": cons_code,
            "description": "General or Specialist Clinical Consultation",
            "quantity": 1,
            "unit_price": cons_price
        })

        # 2. Lab investigation line
        if primary_icd.startswith("B50"):
            lines_for_claim.append({
                "line_type": "lab", "service_code": "LAB-MP-01",
                "description": "Malaria Parasite Microscopic Examination / RDT",
                "quantity": 1, "unit_price": tariff_lookup.get(("LAB-MP-01", fac_level, tariff_year), 2500.0)
            })
        elif primary_icd.startswith("A01"):
            lines_for_claim.append({
                "line_type": "lab", "service_code": "LAB-WID-03",
                "description": "Typhoid Widal Slide Agglutination Test",
                "quantity": 1, "unit_price": tariff_lookup.get(("LAB-WID-03", fac_level, tariff_year), 3500.0)
            })
        elif primary_icd.startswith("E11"):
            lines_for_claim.append({
                "line_type": "lab", "service_code": "LAB-FBS-05",
                "description": "Fasting Blood Sugar / Lipid Profile",
                "quantity": 1, "unit_price": tariff_lookup.get(("LAB-FBS-05", fac_level, tariff_year), 4500.0)
            })

        # 3. Imaging lines
        if primary_icd.startswith("V89") or primary_cond.get("category") == "Trauma":
            ct_price = tariff_lookup.get(("IMG-CT-03", fac_level, tariff_year), 75000.0)
            lines_for_claim.append({
                "line_type": "imaging", "service_code": "IMG-CT-03",
                "description": "Computed Tomography (CT) Brain / Trauma Scan",
                "quantity": 1, "unit_price": ct_price
            })
            wnd_price = tariff_lookup.get(("PROC-WND-06", fac_level, tariff_year), 15000.0)
            lines_for_claim.append({
                "line_type": "procedure", "service_code": "PROC-WND-06",
                "description": "Minor / Major Surgical Wound Debridement & Suturing",
                "quantity": 1, "unit_price": wnd_price
            })
        elif primary_icd.startswith("Z34") or primary_cond.get("category") == "Maternal":
            uss_price = tariff_lookup.get(("IMG-USS-02", fac_level, tariff_year), 8000.0)
            lines_for_claim.append({
                "line_type": "imaging", "service_code": "IMG-USS-02",
                "description": "Obstetric / Abdominopelvic Ultrasound Scan",
                "quantity": 1, "unit_price": uss_price
            })

        # 4. Procedure / Bed line if inpatient or maternity
        if primary_icd == "O80":
            lines_for_claim.append({
                "line_type": "procedure", "service_code": "PROC-NVD-01",
                "description": "Normal Spontaneous Vaginal Delivery Package",
                "quantity": 1, "unit_price": tariff_lookup.get(("PROC-NVD-01", fac_level, tariff_year), 65000.0)
            })
        elif primary_icd == "O82":
            lines_for_claim.append({
                "line_type": "procedure", "service_code": "PROC-CS-02",
                "description": "Caesarean Section Surgical Delivery",
                "quantity": 1, "unit_price": tariff_lookup.get(("PROC-CS-02", fac_level, tariff_year), 260000.0)
            })
        elif primary_icd == "H25.9":
            lines_for_claim.append({
                "line_type": "procedure", "service_code": "PROC-CAT-05",
                "description": "Cataract Extraction with Intraocular Lens",
                "quantity": 1, "unit_price": tariff_lookup.get(("PROC-CAT-05", fac_level, tariff_year), 140000.0)
            })
        elif encounter_type == "Inpatient" and random.random() < 0.20:
            proc_code = "PROC-APP-03" if random.random() < 0.5 else "PROC-HER-04"
            proc_name = "Emergency / Elective Appendectomy" if proc_code == "PROC-APP-03" else "Inguinal Herniorrhaphy Repair"
            lines_for_claim.append({
                "line_type": "procedure", "service_code": proc_code,
                "description": proc_name,
                "quantity": 1, "unit_price": tariff_lookup.get((proc_code, fac_level, tariff_year), 220000.0)
            })

        if encounter_type in ("Inpatient", "Maternity"):
            days = (discharge_date - admission_date).days
            days = max(1, days)
            # 10% of high-severity tertiary admissions require ICU
            is_icu = (fac_level == "Tertiary" and random.random() < 0.12)
            bed_code = "BED-ICU-03" if is_icu else ("BED-GEN-01" if fac_level == "Primary" else "BED-PVT-02")
            bed_desc = "Intensive Care Unit (ICU) Critical Bed Accommodation" if is_icu else f"Hospital Ward Inpatient Bed Accommodation ({days} days)"
            bed_price = tariff_lookup.get((bed_code, fac_level, tariff_year), 25000.0)
            lines_for_claim.append({
                "line_type": "bed-day", "service_code": bed_code,
                "description": bed_desc,
                "quantity": days, "unit_price": bed_price
            })

        # 4. Medication lines (1 to 3 relevant drugs)
        drug_sample = random.sample(drugs, random.randint(1, 3))
        for d in drug_sample:
            lines_for_claim.append({
                "line_type": "drug", "service_code": d["drug_id"],
                "description": f"{d['brand_or_label']} ({d['generic_name']})",
                "quantity": random.randint(1, 2), "unit_price": d["unit_price_ngn"]
            })

        # Calculate billed amounts
        total_billed = 0.0
        for l in lines_for_claim:
            l_billed = round(l["quantity"] * l["unit_price"], 2)
            l["billed_amount"] = l_billed
            total_billed += l_billed

        # Adjudication Status (Process Friction)
        # 84% fully approved, 8% partially approved, 8% rejected
        roll = random.random()
        if roll < 0.84:
            c_status = "Approved"
            rej_reason = None
            total_approved = total_billed
        elif roll < 0.92:
            c_status = "Partially Approved"
            rej_reason = random.choice(["Tariff code billed above agreed rate", "Non-formulary drug disallowed", "Excess quantity deducted"])
            total_approved = round(total_billed * random.uniform(0.70, 0.90), 2)
        else:
            c_status = "Rejected"
            rej_reason = random.choice([
                "Service requires prior authorization but none found",
                "Benefit limit exceeded for plan tier",
                "Service excluded under plan terms",
                "Enrollee policy inactive on encounter date",
                "Duplicate claim submission"
            ])
            total_approved = 0.0

        # Submissions batched monthly with 15-45 day lag
        submission_date = discharge_date + datetime.timedelta(days=random.randint(15, 45))
        batch_id = f"BAT-{provider_id}-{submission_date.year}{submission_date.month:02d}"

        # Adjudication lag: 14-30 days post-submission
        adjudication_date = submission_date + datetime.timedelta(days=random.randint(14, 30))

        # Payment lag: 30-90 days post-submission
        if c_status in ("Approved", "Partially Approved"):
            payment_date = (submission_date + datetime.timedelta(days=random.randint(30, 90))).isoformat()
            total_paid = total_approved
        else:
            payment_date = None
            total_paid = 0.0

        claims.append({
            "claim_id": current_claim_id,
            "enrollee_id": enrollee["enrollee_id"],
            "provider_id": provider_id,
            "encounter_type": encounter_type,
            "admission_date": admission_date.isoformat(),
            "discharge_date": discharge_date.isoformat(),
            "primary_icd10": primary_icd,
            "secondary_icd10": secondary_icd,
            "submission_date": submission_date.isoformat(),
            "batch_id": batch_id,
            "total_billed": round(total_billed, 2),
            "total_approved": round(total_approved, 2),
            "total_paid": round(total_paid, 2),
            "status": c_status,
            "rejection_reason": rej_reason,
            "adjudication_date": adjudication_date.isoformat(),
            "payment_date": payment_date
        })

        # Build claim_lines records
        for l in lines_for_claim:
            l_billed = l["billed_amount"]
            if c_status == "Approved":
                l_app = l_billed
            elif c_status == "Partially Approved":
                l_app = round(l_billed * (total_approved / total_billed), 2)
            else:
                l_app = 0.0

            claim_lines.append({
                "line_id": f"LIN-{line_id_seq:09d}",
                "claim_id": current_claim_id,
                "line_type": l["line_type"],
                "service_code": l["service_code"],
                "description": l["description"],
                "quantity": l["quantity"],
                "unit_price": l["unit_price"],
                "billed_amount": l_billed,
                "approved_amount": l_app
            })
            line_id_seq += 1

    return claims, claim_lines, preauths, referrals
