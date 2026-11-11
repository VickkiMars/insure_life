"""Core entity generators: brokers, plans, groups, providers, and enrollees."""

import random
import datetime
from src.config import (
    STATES_DATA, ETHNIC_NAMES, PLANS_DATA, SECTORS,
    PROVIDER_PREFIXES, SCHEME_TYPES, START_DATE, END_DATE
)

def generate_brokers(num_brokers: int = 120):
    """Generates licensed Nigerian insurance brokers."""
    broker_names = [
        "Hogg Robinson Nigeria", "FBN Insurance Brokers", "Boff & Company", "SCIB Insurance Brokers",
        "TCL Insurance Brokers", "Ark Insurance Brokers", "Glanvill Enthoven", "Standard Alliance",
        "Leadway Capital & Brokers", "First Anchor", "Cornerstone Partners", "Sterling Insurance Brokers",
        "Universal Insurance Brokers", "Consolidated Risk Brokers", "Equity Union", "Oakfield Brokers",
        "Trustville Risk Advisors", "Shieldcrest Insurance", "Pillar Risk Solutions", "Kano Allied Brokers",
        "Niger Delta Insurance Brokers", "Eko Risk Management", "Abuja Premier Brokers", "Apex Mutual"
    ]
    brokers = []
    for i in range(1, num_brokers + 1):
        base_name = random.choice(broker_names)
        suffix = f" {random.choice(['Consultants', 'Partners', 'Advisors', 'Nigeria Ltd', 'Group'])}"
        name = f"{base_name}{suffix} - #{i}"
        state = random.choices(["Lagos", "FCT Abuja", "Rivers", "Oyo", "Kano"], weights=[0.55, 0.25, 0.10, 0.05, 0.05])[0]
        brokers.append({
            "broker_id": f"BRK-{i:04d}",
            "name": name,
            "commission_rate": round(random.uniform(7.5, 12.5), 2),
            "license_number": f"NAICOM/RB/{2015 + (i % 9)}/{1000 + i}",
            "state": state
        })
    return brokers

def generate_plans():
    """Generates standard HMO plan tiers."""
    return PLANS_DATA

def generate_groups(num_groups: int = 500, broker_ids: list = None):
    """Generates corporate and public employer groups in Nigeria."""
    corporate_prefixes = [
        "Dangote", "Zenith", "Access", "United Bank for Africa", "Guaranty Trust", "FirstBank",
        "Nigerian Bottling Company", "Nestle Nigeria", "Flour Mills of Nigeria", "BUA Cement",
        "MTN Nigeria", "Airtel Africa", "Globacom", "TotalEnergies Nigeria", "Seplat Energy",
        "Nigeria LNG Limited", "Lagos State Civil Service", "Federal Ministry of Health",
        "Nigerian Ports Authority", "Federal Inland Revenue Service", "Central Bank of Nigeria",
        "Julius Berger Nigeria", "Lafarge Africa", "PwC Nigeria", "KPMG West Africa",
        "Andela Nigeria", "Flutterwave", "Paystack", "Interswitch", "Oando PLC"
    ]
    groups = []
    for i in range(1, num_groups + 1):
        base = random.choice(corporate_prefixes)
        sector = random.choice(SECTORS)
        name = f"{base} ({sector.split()[0]} Div - {i:03d})"
        headcount = int(random.lognormvariate(5.5, 1.2)) # realistic workforce size
        headcount = max(20, min(headcount, 12000))
        contract_start = START_DATE - datetime.timedelta(days=random.randint(30, 1000))
        contract_renewal = contract_start + datetime.timedelta(days=365)
        broker_id = random.choice(broker_ids) if broker_ids and random.random() < 0.75 else None
        negotiated_prem = round(random.uniform(55000, 280000), 2)

        groups.append({
            "group_id": f"GRP-{i:04d}",
            "name": name,
            "sector": sector,
            "headcount": headcount,
            "contract_start": contract_start.isoformat(),
            "contract_renewal": contract_renewal.isoformat(),
            "broker_id": broker_id,
            "negotiated_premium_head": negotiated_prem
        })
    return groups

def generate_providers(num_providers: int = 1500):
    """Generates primary, secondary, and tertiary healthcare providers across Nigeria."""
    levels = [
        ("Primary", 0.60, ["General Practice", "Family Medicine", "Basic Maternity", "Pharmacy", "Basic Lab"]),
        ("Secondary", 0.32, ["Internal Medicine", "General Surgery", "OBGYN", "Pediatrics", "Radiology", "Orthopedics"]),
        ("Tertiary", 0.08, ["Cardiothoracic", "Neurosurgery", "Oncology", "Nephrology", "ICU", "Specialist Pediatrics"])
    ]
    level_names = [l[0] for l in levels]
    level_weights = [l[1] for l in levels]
    specialty_map = {l[0]: l[2] for l in levels}

    ownership_types = [("Private", 0.65), ("Public", 0.25), ("Faith-based", 0.10)]
    own_names = [o[0] for o in ownership_types]
    own_weights = [o[1] for o in ownership_types]

    state_names = [s["state"] for s in STATES_DATA]
    state_weights = [s["weight"] for s in STATES_DATA]
    state_lga_map = {s["state"]: s["lgas"] for s in STATES_DATA}

    providers = []
    for i in range(1, num_providers + 1):
        level = random.choices(level_names, weights=level_weights)[0]
        ownership = random.choices(own_names, weights=own_weights)[0]
        state = random.choices(state_names, weights=state_weights)[0]
        lga = random.choice(state_lga_map[state])

        prefix = random.choice(PROVIDER_PREFIXES)
        if level == "Primary":
            name = f"{prefix} Primary Health Centre & Clinic ({lga})"
            contract_type = "Capitation"
        elif level == "Secondary":
            name = f"{prefix} Specialist Hospital ({state})"
            contract_type = "Capitation & Fee-For-Service"
        else:
            name = f"Federal / University Teaching Hospital & {prefix} Annex ({state})"
            contract_type = "Fee-For-Service"

        specialties = ", ".join(specialty_map[level])
        accreditation = random.choices(["Accredited - Grade A", "Accredited - Grade B", "Provisional"], weights=[0.5, 0.4, 0.1])[0]

        providers.append({
            "provider_id": f"PRV-{i:05d}",
            "name": name,
            "level": level,
            "ownership": ownership,
            "state": state,
            "lga": lga,
            "specialties": specialties,
            "accreditation_status": accreditation,
            "contract_type": contract_type
        })
    return providers

def generate_enrollees(target_count: int, groups: list, plans: list, providers: list):
    """
    Generates realistic Nigerian enrollee population with household structures:
    Principals, Spouses, and Children with authentic Nigerian names, DOBs, and primary care providers.
    """
    state_names = [s["state"] for s in STATES_DATA]
    state_weights = [s["weight"] for s in STATES_DATA]
    state_lga_map = {s["state"]: s["lgas"] for s in STATES_DATA}

    # Group providers by state for primary care assignment
    state_pcp_map = {}
    for p in providers:
        if p["level"] in ("Primary", "Secondary"):
            state_pcp_map.setdefault(p["state"], []).append(p["provider_id"])
    
    # Fallback if any state has empty list
    all_provider_ids = [p["provider_id"] for p in providers]

    group_ids = [g["group_id"] for g in groups]
    plan_ids = [p["plan_id"] for p in plans]
    plan_weights = [0.25, 0.40, 0.25, 0.07, 0.03] # Bronze, Silver, Gold, Platinum, State Equity

    enrollees = []
    enrollee_counter = 1

    ethnic_groups = list(ETHNIC_NAMES.keys())
    ethnic_weights = [0.35, 0.25, 0.20, 0.12, 0.08] # Yoruba, Igbo, Hausa/Fulani, South-South, Middle-Belt

    while enrollee_counter <= target_count:
        # Generate Household: Principal + 0-1 Spouse + 0-4 Children
        ethnic = random.choices(ethnic_groups, weights=ethnic_weights)[0]
        names_dict = ETHNIC_NAMES[ethnic]
        surname = random.choice(names_dict["surnames"])

        # Inconsistent name spelling noise (realistic messiness)
        if random.random() < 0.03 and len(surname) > 4:
            surname_disp = surname.replace("u", "o", 1) if "u" in surname else surname + "h"
        else:
            surname_disp = surname

        state = random.choices(state_names, weights=state_weights)[0]
        lga = random.choice(state_lga_map[state])
        pcp_options = state_pcp_map.get(state, all_provider_ids)
        pcp_id = random.choice(pcp_options)

        # Corporate group vs retail
        is_corporate = random.random() < 0.88
        grp_id = random.choice(group_ids) if is_corporate else None
        if is_corporate:
            sch_type = random.choice(["Formal Sector Private", "Formal Sector Public"])
            p_id = random.choices(plan_ids, weights=plan_weights)[0]
        else:
            sch_type = random.choice(["Informal / Voluntary Retail", "State-Sponsored Equity", "BHCPF"])
            p_id = "PLN-BRZ-01" if sch_type == "Informal / Voluntary Retail" else "PLN-ST-EQ-05"

        principal_id = f"ENR-{enrollee_counter:07d}"
        enrollee_counter += 1

        p_sex = random.choice(["M", "F"])
        first_name = random.choice(names_dict["first_male"] if p_sex == "M" else names_dict["first_female"])
        # Age between 23 and 60
        p_age_years = random.randint(23, 60)
        p_dob = datetime.date(2023 - p_age_years, random.randint(1, 12), random.randint(1, 28))
        enrol_date = START_DATE - datetime.timedelta(days=random.randint(60, 1200))
        status = random.choices(["Active", "Suspended", "Terminated"], weights=[0.92, 0.05, 0.03])[0]

        has_nin = random.random() > 0.05
        nin = f"{random.randint(10000000000, 99999999999)}" if has_nin else None
        phone = f"+234-{random.choice(['803', '802', '814', '703', '905', '805'])}-{random.randint(1000000, 9999999)}" if random.random() > 0.04 else None

        enrollees.append({
            "enrollee_id": principal_id,
            "principal_flag": 1,
            "principal_id": None,
            "relationship": "PRINCIPAL",
            "dob": p_dob.isoformat(),
            "sex": p_sex,
            "state": state,
            "lga": lga,
            "scheme_type": sch_type,
            "group_id": grp_id,
            "plan_id": p_id,
            "primary_care_provider_id": pcp_id,
            "enrolment_date": enrol_date.isoformat(),
            "status": status,
            "nin": nin,
            "phone_number": phone
        })

        # Add Spouse (70% probability for married principal)
        if random.random() < 0.70 and enrollee_counter <= target_count:
            spouse_id = f"ENR-{enrollee_counter:07d}"
            enrollee_counter += 1
            s_sex = "F" if p_sex == "M" else "M"
            s_first = random.choice(names_dict["first_female"] if s_sex == "F" else names_dict["first_male"])
            s_age = max(18, p_age_years + random.randint(-6, 4))
            s_dob = datetime.date(2023 - s_age, random.randint(1, 12), random.randint(1, 28))

            enrollees.append({
                "enrollee_id": spouse_id,
                "principal_flag": 0,
                "principal_id": principal_id,
                "relationship": "SPOUSE",
                "dob": s_dob.isoformat(),
                "sex": s_sex,
                "state": state,
                "lga": lga,
                "scheme_type": sch_type,
                "group_id": grp_id,
                "plan_id": p_id,
                "primary_care_provider_id": pcp_id,
                "enrolment_date": enrol_date.isoformat(),
                "status": status,
                "nin": f"{random.randint(10000000000, 99999999999)}" if random.random() > 0.1 else None,
                "phone_number": phone
            })

        # Add Children (0 to 4 children, capping at 4 dependants per HMO rules)
        num_children = random.choices([0, 1, 2, 3, 4], weights=[0.15, 0.25, 0.35, 0.18, 0.07])[0]
        for c_idx in range(num_children):
            if enrollee_counter > target_count:
                break
            child_id = f"ENR-{enrollee_counter:07d}"
            enrollee_counter += 1
            c_sex = random.choice(["M", "F"])
            c_first = random.choice(names_dict["first_male"] if c_sex == "M" else names_dict["first_female"])
            c_age = max(0, min(p_age_years - 20, random.randint(0, 18)))
            c_dob = datetime.date(2023 - c_age, random.randint(1, 12), random.randint(1, 28))

            enrollees.append({
                "enrollee_id": child_id,
                "principal_flag": 0,
                "principal_id": principal_id,
                "relationship": "CHILD",
                "dob": c_dob.isoformat(),
                "sex": c_sex,
                "state": state,
                "lga": lga,
                "scheme_type": sch_type,
                "group_id": grp_id,
                "plan_id": p_id,
                "primary_care_provider_id": pcp_id,
                "enrolment_date": enrol_date.isoformat(),
                "status": status,
                "nin": None,
                "phone_number": phone
            })

    return enrollees
