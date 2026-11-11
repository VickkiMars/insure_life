# Nigerian Health Insurance (HMO) Synthetic Dataset Suite

A realistic, high-fidelity synthetic data generator modeling the operational, clinical, and financial ecosystem of a Nigerian Health Maintenance Organisation (HMO).

Built for data engineering, actuarial modeling, healthcare analytics, fraud detection (Special Investigation Unit), and data warehouse benchmarking.

---

## Architecture & Schema Overview

The dataset models 16 relational tables with complete primary key and foreign key integrity.

```
                          [GROUPS] (Corporate / Public)
                             │
            ┌────────────────┴────────────────┐
            ▼                                 ▼
   [PREMIUM_INVOICES]                    [ENROLLEES]
   (Monthly billing/arrears)            (Principals & Dependants)
                                              │
              ┌───────────────────────────────┼───────────────────────────────┐
              ▼                               ▼                               ▼
       [COMPLAINTS]                    [CAPITATION]                    [PREAUTHORIZATION]
    (Service tickets)              (Monthly PCP stipends)              (Secondary approvals)
                                              │
                                              ▼
                                         [REFERRALS]
                                 (PCP to Secondary/Tertiary)
                                              │
                                              ▼
                                          [CLAIMS]
                                  (Encounters & Diagnosis)
                                              │
                             ┌────────────────┴────────────────┐
                             ▼                                 ▼
                       [CLAIM_LINES]                     [AUDIT_FLAGS]
                 (Itemized tariffs & drugs)          (SIU fraud & abuse)
```

---

## 16 Relational Tables

### Core Entities
1. **`enrollees`**: Principal and dependant enrollees with NIN, Nigerian telephone numbers, dates of birth following Nigeria's demographic pyramid, relationships (`PRINCIPAL`, `SPOUSE`, `CHILD`), geopolitical zone, state, LGA, scheme type (`Formal Sector Private`, `Formal Sector Public`, `Informal / Voluntary Retail`, `State-Sponsored Equity`, `BHCPF`), plan ID, and assigned Primary Care Provider (PCP).
2. **`groups`**: Corporate clients and public sector employers (e.g., FMCG, Banking, Oil & Gas, State Civil Service, Federal Ministries) with headcounts, negotiated annual premiums per head, and contract dates.
3. **`plans`**: HMO benefit tiers (`Bronze / Vital`, `Silver / Standard`, `Gold / Comprehensive`, `Platinum / Executive`, `State Equity / BHCPF`) with annual limits, co-pay percentages, waiting periods, exclusions, and referral rules.
4. **`providers`**: Primary Healthcare Centres (PHCs), private clinics, secondary specialist hospitals, and tertiary teaching hospitals/Federal Medical Centres with accreditation ratings, state, LGA, and contract type (`Capitation`, `Fee-For-Service`).
5. **`brokers`**: NAICOM-licensed insurance brokers placing group policies with negotiated commission rates.

### Reference Tables
6. **`tariff_schedule`**: Medical service codes (`consultation`, `lab`, `imaging`, `bed-day`, `procedure`) tiered by facility level (Primary, Secondary, Tertiary) with multi-year inflation adjustments (2023–2025).
7. **`drug_formulary`**: Essential medicines catalogue covering antimalarials (Artemether-Lumefantrine, Artesunate IV), antibiotics (Amoxicillin-Clavulanic acid, Ciprofloxacin, Ceftriaxone), antihypertensives, oral hypoglycemics, and analgesics.
8. **`icd10_subset`**: Clinical ICD-10 diagnostic reference with Nigerian epidemiological prevalence weights, clinical severity, sex constraints, and seasonal flags.

### Transactions
9. **`premium_invoices`**: Monthly billing cycles for corporate groups detailing amounts billed, amounts paid, payment channels (NIBSS Instant Payment, Remita, Direct Debit), arrears, and payment statuses.
10. **`capitation_payments`**: Monthly prospective capitation payments disbursed to primary healthcare providers based on active enrollee panels.
11. **`preauthorizations`**: Prior-authorization requests for secondary referrals, surgical interventions, high-cost imaging (CT/MRI), and inpatient admissions with turnaround hours and denial reasons.
12. **`claims`**: Clinical encounter headers tracking admission/discharge dates, primary/secondary ICD-10 diagnoses, monthly batch submission IDs, billed/approved/paid amounts, rejection reasons, adjudication dates, and payment settlement lags.
13. **`claim_lines`**: Itemized service lines linked to tariff schedule codes and formulary medications with quantities, unit prices, billed amounts, and approved amounts.
14. **`referrals`**: Formal referral transfers from primary care gatekeeper facilities to secondary/tertiary specialist centers.

### Operations & Risk
15. **`complaints_tickets`**: Customer care tickets submitted by enrollees (out-of-pocket charges, delayed card, drug stockouts, delay in pre-auth) with resolution turnaround times.
16. **`audit_flags`**: Special Investigation Unit (SIU) fraud, waste, and abuse alerts (impossible gender diagnosis, upcoding, duplicate billing, post-discharge claims, ghost enrollees).

---

## Nigerian Demographic & Domain Realism

- **Demographics**: Authentic Nigerian given names and surnames sampled across Yoruba, Igbo, Hausa/Fulani, South-South, and Middle-Belt ethnolinguistic groups.
- **Geography**: Realistic geographic distribution concentrated across Nigerian commercial centers (Lagos ~42%, FCT Abuja ~18%, Rivers ~10%, Oyo ~6%, Kano ~5%, Delta/Edo ~6%, others ~13%) mapped to actual LGAs.
- **Disease Seasonality**: Plasmodium falciparum malaria surges during the West African rainy season (May through October), while Acute Upper Respiratory Infections peak during Harmattan (December through February).
- **Financial Dynamics**: Amounts denominated in Nigerian Naira (NGN). Claims follow a heavy-tailed distribution where routine outpatient care costs ₦4,500 – ₦25,000, while catastrophic inpatient and surgical care reaches ₦350,000 – ₦2,000,000+. Medical tariffs drift upward over 2023–2025 reflecting local inflation.
- **Process Friction**: Hospital claims batched monthly with 15–45 day post-discharge lags, 30–90 day payment adjudication cycles, steady 8–10% claim rejections, and injected forensic anomalies for SIU audit testing.

---

## CLI Usage

### Generate Full Dataset (&ge; 1,000,000 rows)
```bash
python3 generate.py --scale full --seed 42 --db-path nigerian_hmo.db --csv-dir data
```

### Generate Fast Sample Dataset (~100,000 rows)
```bash
python3 generate.py --scale sample --seed 42 --db-path sample_hmo.db --csv-dir sample_data
```

### Verify Dataset Integrity & Realism
```bash
python3 verify_data.py --db-path nigerian_hmo.db
```

### Run Unit Tests
```bash
python3 -m unittest discover -s tests -v
```
