"""Reference data generator: ICD-10 subsets, geography, tariffs with inflation, and drug formulary."""

from src.config import STATES_DATA, ICD10_DATA, BASE_TARIFFS, DRUGS_DATA

def generate_geography_and_icd10():
    """Generates combined reference entries for Nigerian states, LGAs, and ICD-10 codes."""
    geo_rows = []
    for s_idx, state_info in enumerate(STATES_DATA, 1):
        state_name = state_info["state"]
        zone = state_info["zone"]
        weight = state_info["weight"]
        for lga in state_info["lgas"]:
            geo_rows.append({
                "ref_id": f"GEO-{s_idx:02d}-{len(geo_rows)+1:04d}",
                "state": state_name,
                "lga": lga,
                "geopolitical_zone": zone,
                "hmo_penetration_weight": weight
            })

    icd_rows = []
    for idx, item in enumerate(ICD10_DATA, 1):
        icd_rows.append({
            "icd10_code": item["code"],
            "description": item["description"],
            "category": item["category"],
            "base_weight": item["base_weight"],
            "sex_restriction": item.get("sex", "ANY"),
            "min_age": item.get("min_age", 0),
            "max_age": item.get("max_age", 120),
            "severity": item.get("severity", "Moderate"),
            "is_rainy_seasonal": int(item.get("is_rainy_seasonal", False))
        })

    return geo_rows, icd_rows

def generate_tariff_schedule():
    """
    Generates tariff schedule across Primary, Secondary, and Tertiary facility tiers.
    Simulates annual price inflation in Nigeria (e.g. 2023 base, 2024 +18%, 2025 +22%).
    """
    tariffs = []
    years = [
        (2023, 1.00, "2023-01-01"),
        (2024, 1.18, "2024-01-01"),
        (2025, 1.44, "2025-01-01")
    ]
    tiers = [
        ("Primary", 3),     # Index 3 in BASE_TARIFFS
        ("Secondary", 4),   # Index 4
        ("Tertiary", 5)     # Index 5
    ]

    tariff_id = 1
    for code, desc, service_type, p_price, s_price, t_price in BASE_TARIFFS:
        tier_prices = {
            "Primary": p_price,
            "Secondary": s_price,
            "Tertiary": t_price
        }
        for year, multiplier, eff_date in years:
            for tier_name, base_p in tier_prices.items():
                adjusted_price = round(base_p * multiplier, -2) # rounded to nearest 100 NGN
                tariffs.append({
                    "tariff_id": f"TAR-{tariff_id:06d}",
                    "service_code": code,
                    "service_type": service_type,
                    "description": desc,
                    "facility_level": tier_name,
                    "tariff_year": year,
                    "price_ngn": float(adjusted_price),
                    "effective_date": eff_date
                })
                tariff_id += 1

    return tariffs

def generate_drug_formulary():
    """Generates standard essential drug formulary entries with coverage flags."""
    formulary = []
    for idx, (brand_name, generic_name, form, base_price, covered) in enumerate(DRUGS_DATA, 1):
        formulary.append({
            "drug_id": f"DRG-{idx:04d}",
            "brand_or_label": brand_name,
            "generic_name": generic_name,
            "dosage_form": form,
            "unit_price_ngn": float(base_price),
            "is_covered": covered,
            "requires_preauth": 1 if base_price >= 4000 else 0
        })
    return formulary
