"""Nigerian Health Insurance (HMO) configuration and demographic constants."""

import datetime

# Simulation timeframe
START_DATE = datetime.date(2023, 1, 1)
END_DATE = datetime.date(2025, 12, 31)

# Nigerian States, LGAs, Geopolitical Zones, and HMO Weightings
# Reflects economic concentration: Lagos, FCT Abuja, Rivers, Oyo, Kano dominate HMO penetration
STATES_DATA = [
    {
        "state": "Lagos", "zone": "South West", "weight": 0.42,
        "lgas": ["Ikeja", "Eti-Osa", "Alimosho", "Surulere", "Kosofe", "Ikorodu", "Lagos Island", "Oshodi-Isolo", "Apapa", "Shomolu", "Agege", "Mushin"]
    },
    {
        "state": "FCT Abuja", "zone": "North Central", "weight": 0.18,
        "lgas": ["AMAC", "Bwari", "Gwagwalada", "Kuje", "Abaji", "Kwali"]
    },
    {
        "state": "Rivers", "zone": "South South", "weight": 0.10,
        "lgas": ["Port Harcourt", "Obio-Akpor", "Eleme", "Ikwerre", "Oyigbo", "Bonny", "Okrika"]
    },
    {
        "state": "Oyo", "zone": "South West", "weight": 0.06,
        "lgas": ["Ibadan North", "Ibadan South-West", "Ibadan North-East", "Ogbomosho North", "Oyo East"]
    },
    {
        "state": "Kano", "zone": "North West", "weight": 0.05,
        "lgas": ["Kano Municipal", "Nassarawa", "Fagge", "Dala", "Gwale", "Tarauni"]
    },
    {
        "state": "Delta", "zone": "South South", "weight": 0.03,
        "lgas": ["Warri South", "Uvwie", "Oshimili South", "Sapele", "Ughelli North"]
    },
    {
        "state": "Edo", "zone": "South South", "weight": 0.03,
        "lgas": ["Oredo", "Ikpoba-Okha", "Egor", "Uhunmwonde"]
    },
    {
        "state": "Kaduna", "zone": "North West", "weight": 0.03,
        "lgas": ["Kaduna North", "Kaduna South", "Chikun", "Zaria", "Sabon Gari"]
    },
    {
        "state": "Anambra", "zone": "South East", "weight": 0.025,
        "lgas": ["Awka South", "Onitsha North", "Onitsha South", "Nnewi North", "Idemili North"]
    },
    {
        "state": "Enugu", "zone": "South East", "weight": 0.025,
        "lgas": ["Enugu North", "Enugu South", "Enugu East", "Nsukka", "Udi"]
    },
    {
        "state": "Ogun", "zone": "South West", "weight": 0.025,
        "lgas": ["Abeokuta South", "Abeokuta North", "Ado-Odo/Ota", "Sagamu", "Ijebu Ode"]
    },
    {
        "state": "Plateau", "zone": "North Central", "weight": 0.015,
        "lgas": ["Jos North", "Jos South", "Jos East", "Barkin Ladi"]
    },
    {
        "state": "Akwa Ibom", "zone": "South South", "weight": 0.015,
        "lgas": ["Uyo", "Ikot Ekpene", "Eket", "Oron"]
    },
    {
        "state": "Imo", "zone": "South East", "weight": 0.01,
        "lgas": ["Owerri Municipal", "Owerri North", "Owerri West", "Orlu"]
    }
]

# Authentic Nigerian Names by Ethnolinguistic Background
ETHNIC_NAMES = {
    "Yoruba": {
        "first_male": ["Babatunde", "Olumide", "Adebayo", "Kehinde", "Oluwaseun", "Abiola", "Adeyemi", "Folarin", "Ayodele", "Gbenga", "Taiwo", "Damilola", "Segun", "Kunle", "Tunde", "Opeyemi", "Rotimi", "Adewale", "Kayode", "Tolani"],
        "first_female": ["Folashade", "Adesua", "Kehinde", "Oluwaseun", "Bolanle", "Titilayo", "Ronke", "Yetunde", "Abimbola", "Omotola", "Funmilayo", "Bisola", "Bukola", "Simisola", "Eniola", "Ayomide", "Morayo", "Mojisola", "Damilola", "Temitope"],
        "surnames": ["Balogun", "Ogundipe", "Adeleke", "Oyeneyin", "Akinwunmi", "Fashola", "Oshodi", "Tinubu", "Awolowo", "Akintola", "Adeniyi", "Babajide", "Sowande", "Alakija", "Bankole", "Dosunmu", "Ogunlesi", "Adewunmi", "Sanusi", "Oduwole"]
    },
    "Igbo": {
        "first_male": ["Chukwuma", "Chidiebere", "Nnamdi", "Emeka", "Chinonso", "Ifeanyi", "Obinna", "Kelechi", "Chibuike", "Uchenna", "Somtochukwu", "Chinedu", "Chika", "Tochukwu", "Echezona", "Ikenna", "Ebuka", "Nonso", "Chidi", "Onyekachi"],
        "first_female": ["Ngozi", "Chiamaka", "Chinwe", "Amaka", "Adanna", "Chioma", "Adaeze", "Ifunanya", "Nneka", "Uchechi", "Oluchi", "Chidinma", "Kamsiyochukwu", "Ijeoma", "Amarachi", "Somto", "Chisom", "Ogechi", "Uzoamaka", "Chinyere"],
        "surnames": ["Okonkwo", "Nwosu", "Eze", "Nwachukwu", "Okafor", "Okeke", "Anyanwu", "Ezeh", "Chukwu", "Iheanacho", "Obi", "Oguamanam", "Nnamani", "Maduka", "Onyema", "Umeh", "Mbah", "Ekwueme", "Anichebe", "Igbokwe"]
    },
    "Hausa_Fulani": {
        "first_male": ["Ibrahim", "Aminu", "Abubakar", "Usman", "Bello", "Danjuma", "Garba", "Aliyu", "Sanusi", "Shehu", "Kabiru", "Mustapha", "Bashir", "Nasiru", "Suleiman", "Faruk", "Sani", "Idris", "Yahaya", "Musa"],
        "first_female": ["Fatima", "Zainab", "Aisha", "Halima", "Maryam", "Hadiza", "Rabi", "Hauwa", "Asma'u", "Safiya", "Khadijah", "Nafisa", "Zubaida", "Bilkisu", "Jamila", "Ruqayya", "Salma", "Maimuna", "Sadiya", "Lubabatu"],
        "surnames": ["Dantata", "Yar'adua", "Balarabe", "Gwandu", "Katsina", "Gwarzo", "Daudawa", "Maiyaki", "Danfulani", "Zazzau", "Bayero", "Shekarau", "Ribadu", "Dangote", "Gwandu", "Makarfi", "Lamido", "Buhari", "Shagari", "Wamakko"]
    },
    "South_South": {
        "first_male": ["Victor", "Ebiere", "Osaro", "Efosa", "Edidiong", "Bassey", "Itoro", "Tari", "Godswill", "Etim", "Tamuno", "Baridua", "Ovie", "Oghenekaro", "Idongesit", "Ekemini", "Preye", "Tonye", "Akpan", "Efe"],
        "first_female": ["Ebiere", "Osas", "Edidiong", "Tari", "Enobong", "Aniekan", "Oghogho", "Isoken", "Utibe", "Iniabasi", "Ibifubara", "Oroma", "Oghenefejiro", "Toritseju", "Blessing", "Ese", "Ekaette", "Idara", "Mfon", "Peace"],
        "surnames": ["Henshaw", "Duke", "Briggs", "Amadi", "Ibori", "Igbinedion", "Udom", "Esuene", "Asuquo", "Etiebet", "Umoren", "Okilo", "Spiff", "Clark", "Uduaghan", "Dickson", "Wike", "Okiro", "Imoke", "Attah"]
    },
    "Middle_Belt": {
        "first_male": ["Terver", "Gyang", "Pam", "Bitrus", "Audu", "Lar", "Nanle", "Sunday", "Dung", "Yakubu", "Moses", "Chuwang", "Kefas", "Jerry", "Solomon", "Gowon", "Shima", "Iorwuese", "Davou", "Nuhu"],
        "first_female": ["Dooshima", "Simi", "Ngo", "Zungdet", "Kangyang", "Vongtau", "Ngizan", "Martha", "Ladi", "Murna", "Grace", "Rachael", "Keturah", "Tabitha", "Mwuese", "Wandoo", "Seember", "Hembadoon", "Lengkat", "Talatu"],
        "surnames": ["Gowon", "Tarka", "Lar", "Dariye", "Jang", "Plateau", "Akume", "Suswam", "Gemade", "Tyoden", "Bot", "Chollom", "Gyepgar", "Mwadkwon", "Dung", "Zang", "Tapgun", "Useni", "Shagaya", "Mantu"]
    }
}

# Scheme types in Nigerian Healthcare
SCHEME_TYPES = [
    ("Formal Sector Private", 0.58),
    ("Formal Sector Public", 0.22),
    ("Informal / Voluntary Retail", 0.12),
    ("State-Sponsored Equity", 0.05),
    ("BHCPF", 0.03)
]

# Plan Tiers
PLANS_DATA = [
    {
        "plan_id": "PLN-BRZ-01", "tier": "Bronze / Vital", "premium_per_head": 45000.0,
        "annual_limit": 750000.0, "co_pay_pct": 10.0, "waiting_periods": 60,
        "exclusions": "Cosmetic surgery, assisted reproduction, renal dialysis, advanced oncology",
        "referral_rules": "Strict PCP gatekeeping required for any secondary care"
    },
    {
        "plan_id": "PLN-SLV-02", "tier": "Silver / Standard", "premium_per_head": 85000.0,
        "annual_limit": 1800000.0, "co_pay_pct": 5.0, "waiting_periods": 30,
        "exclusions": "Cosmetic surgery, organ transplant, high-cost biologicals",
        "referral_rules": "PCP referral required except for direct OB/GYN and Pediatric visits"
    },
    {
        "plan_id": "PLN-GLD-03", "tier": "Gold / Comprehensive", "premium_per_head": 165000.0,
        "annual_limit": 4500000.0, "co_pay_pct": 0.0, "waiting_periods": 14,
        "exclusions": "Experimental therapy, aesthetic cosmetic procedures",
        "referral_rules": "Open access to network secondary hospitals; pre-auth for inpatient & surgery"
    },
    {
        "plan_id": "PLN-PLT-04", "tier": "Platinum / Executive", "premium_per_head": 320000.0,
        "annual_limit": 12000000.0, "co_pay_pct": 0.0, "waiting_periods": 0,
        "exclusions": "Self-inflicted injuries, non-medical wellness retreats",
        "referral_rules": "Direct specialist access across tertiary network, worldwide emergency coverage"
    },
    {
        "plan_id": "PLN-ST-EQ-05", "tier": "State Equity / BHCPF", "premium_per_head": 15000.0,
        "annual_limit": 300000.0, "co_pay_pct": 0.0, "waiting_periods": 0,
        "exclusions": "All non-primary services, specialist care without zonal approval",
        "referral_rules": "Public PHC mandatory gatekeeper; emergency tertiary stabilized only"
    }
]

# Corporate Sectors in Nigeria
SECTORS = [
    "Banking & Financial Services",
    "Oil & Gas / Energy",
    "Fast-Moving Consumer Goods (FMCG)",
    "Telecommunications & Tech",
    "Federal Civil Service / Parastatal",
    "State Government Ministry",
    "Manufacturing & Heavy Industry",
    "Professional Services & Consulting",
    "Logistics & Maritime",
    "Education & Healthcare Institutions"
]

# Nigerian Hospital Providers prefixes and suffixes
PROVIDER_PREFIXES = [
    "St. Nicholas", "Lagoon", "Reddington", "Cedarcrest", "Lily", "First Cardiology",
    "Gracefield", "Eko", "Mainland", "Crestview", "Faith City", "Garki", "Medway",
    "Prime", "Dantata", "Aminu Kano", "Al-Afiyah", "Heritage", "Shepherd", "Bethel",
    "Olive Branch", "Evercare", "Euracare", "Lifeline", "Springs", "Mercy & Grace"
]

# Top ICD-10 conditions in Nigeria with realistic epidemiologic weights, seasonality, and sex constraints
ICD10_DATA = [
    {
        "code": "B50.9", "description": "Plasmodium falciparum malaria, unspecified",
        "category": "Infectious", "base_weight": 0.35, "is_rainy_seasonal": True, "sex": "ANY",
        "severity": "Low-Moderate", "pediatric_skew": 1.4
    },
    {
        "code": "J06.9", "description": "Acute upper respiratory infection, unspecified",
        "category": "Respiratory", "base_weight": 0.14, "is_harmattan_seasonal": True, "sex": "ANY",
        "severity": "Low", "pediatric_skew": 1.6
    },
    {
        "code": "A01.0", "description": "Typhoid fever, unspecified",
        "category": "Infectious", "base_weight": 0.11, "is_rainy_seasonal": True, "sex": "ANY",
        "severity": "Moderate", "pediatric_skew": 1.0
    },
    {
        "code": "I10", "description": "Essential (primary) hypertension",
        "category": "Cardiovascular", "base_weight": 0.09, "is_seasonal": False, "sex": "ANY",
        "severity": "Moderate", "min_age": 28, "pediatric_skew": 0.0
    },
    {
        "code": "A09", "description": "Infectious gastroenteritis and colitis, unspecified",
        "category": "Gastrointestinal", "base_weight": 0.08, "is_rainy_seasonal": True, "sex": "ANY",
        "severity": "Low-Moderate", "pediatric_skew": 1.8
    },
    {
        "code": "O80", "description": "Single spontaneous delivery (Normal Delivery)",
        "category": "Maternal", "base_weight": 0.04, "is_seasonal": False, "sex": "F",
        "min_age": 16, "max_age": 48, "severity": "Moderate"
    },
    {
        "code": "O82", "description": "Single delivery by caesarean section",
        "category": "Maternal", "base_weight": 0.025, "is_seasonal": False, "sex": "F",
        "min_age": 16, "max_age": 48, "severity": "High"
    },
    {
        "code": "Z34.9", "description": "Antenatal screening, unspecified trimester",
        "category": "Maternal", "base_weight": 0.035, "is_seasonal": False, "sex": "F",
        "min_age": 16, "max_age": 48, "severity": "Low"
    },
    {
        "code": "E11.9", "description": "Type 2 diabetes mellitus without complications",
        "category": "Endocrine", "base_weight": 0.04, "is_seasonal": False, "sex": "ANY",
        "min_age": 30, "severity": "Moderate"
    },
    {
        "code": "D57.0", "description": "Hb-SS disease with crisis (Sickle Cell Crisis)",
        "category": "Hematology", "base_weight": 0.025, "is_seasonal": False, "sex": "ANY",
        "severity": "High", "pediatric_skew": 1.5
    },
    {
        "code": "V89.2", "description": "Person injured in road traffic accident, unspecified",
        "category": "Trauma", "base_weight": 0.025, "is_seasonal": False, "sex": "ANY",
        "severity": "High"
    },
    {
        "code": "B20", "description": "Human immunodeficiency virus [HIV] disease",
        "category": "Infectious", "base_weight": 0.015, "is_seasonal": False, "sex": "ANY",
        "min_age": 15, "severity": "High"
    },
    {
        "code": "K27.9", "description": "Peptic ulcer, unspecified as acute or chronic",
        "category": "Gastrointestinal", "base_weight": 0.015, "is_seasonal": False, "sex": "ANY",
        "min_age": 20, "severity": "Moderate"
    },
    {
        "code": "N39.0", "description": "Urinary tract infection, site not specified",
        "category": "Urology", "base_weight": 0.015, "is_seasonal": False, "sex": "ANY",
        "severity": "Low-Moderate"
    },
    {
        "code": "H25.9", "description": "Senile cataract, unspecified",
        "category": "Ophthalmology", "base_weight": 0.01, "is_seasonal": False, "sex": "ANY",
        "min_age": 50, "severity": "Moderate"
    },
    {
        "code": "N40", "description": "Benign prostatic hyperplasia",
        "category": "Urology", "base_weight": 0.01, "is_seasonal": False, "sex": "M",
        "min_age": 48, "severity": "Moderate"
    }
]

# Standard Medical Tariff services in NGN across facility tiers
BASE_TARIFFS = [
    ("CONS-GP-01", "General Outpatient Consultation", "consultation", 2500, 4500, 8000),
    ("CONS-SP-02", "Specialist Consultation (Cardiology/OBGYN/Pediatrics)", "consultation", 6000, 12000, 22000),
    ("LAB-MP-01", "Malaria Parasite Microscopic Examination / RDT", "lab", 1200, 2500, 4500),
    ("LAB-FBC-02", "Full Blood Count (FBC / CBC) with Differential", "lab", 2500, 5000, 8500),
    ("LAB-WID-03", "Typhoid Widal Slide Agglutination / Typhidot", "lab", 1800, 3500, 6000),
    ("LAB-EUC-04", "Electrolytes, Urea, and Creatinine (E/U/Cr)", "lab", 4000, 8500, 15000),
    ("LAB-FBS-05", "Fasting Blood Sugar / Lipid Profile", "lab", 2000, 4500, 8000),
    ("LAB-URIN-06", "Urinalysis and Urine Microscopy / C&S", "lab", 1500, 3500, 6500),
    ("IMG-XR-01", "Chest X-Ray (PA View)", "imaging", 4000, 9000, 16000),
    ("IMG-USS-02", "Abdominopelvic / Obstetric Ultrasound Scan", "imaging", 3500, 8000, 15000),
    ("IMG-CT-03", "Computed Tomography (CT) Brain / Abdomen", "imaging", 35000, 75000, 140000),
    ("IMG-MRI-04", "Magnetic Resonance Imaging (MRI)", "imaging", 60000, 130000, 240000),
    ("BED-GEN-01", "General Inpatient Bed Ward (Per Day)", "bed-day", 5000, 12000, 25000),
    ("BED-PVT-02", "Private Room Inpatient Bed (Per Day)", "bed-day", 12000, 30000, 65000),
    ("BED-ICU-03", "Intensive Care Unit (ICU) Bed (Per Day)", "bed-day", 35000, 95000, 190000),
    ("PROC-NVD-01", "Normal Spontaneous Vaginal Delivery (SVD) Package", "procedure", 25000, 65000, 130000),
    ("PROC-CS-02", "Emergency / Elective Caesarean Section (CS)", "procedure", 95000, 260000, 550000),
    ("PROC-APP-03", "Appendectomy (Open / Laparoscopic)", "procedure", 80000, 220000, 480000),
    ("PROC-HER-04", "Herniorrhaphy (Inguinal Hernia Repair)", "procedure", 65000, 175000, 380000),
    ("PROC-CAT-05", "Cataract Extraction with Intraocular Lens", "procedure", 50000, 140000, 300000),
    ("PROC-WND-06", "Minor Surgical Wound Debridement & Suturing", "procedure", 6000, 15000, 32000)
]

# Essential Drug Formulary across Nigerian clinical practice
DRUGS_DATA = [
    ("Artemether-Lumefantrine 80/480mg", "Artemether + Lumefantrine", "Tablet", 2200, 1),
    ("Dihydroartemisinin-Piperaquine 40/320mg", "Dihydroartemisinin + Piperaquine", "Tablet", 3100, 1),
    ("Injectable Artesunate 60mg/120mg", "Artesunate", "Injection", 4800, 1),
    ("Amoxicillin-Clavulanic Acid 625mg/1g", "Amoxicillin + Clavulanate", "Tablet", 4500, 1),
    ("Ciprofloxacin 500mg", "Ciprofloxacin", "Tablet", 1800, 1),
    ("Azithromycin 500mg", "Azithromycin", "Tablet", 3200, 1),
    ("Ceftriaxone 1g IV", "Ceftriaxone", "Injection", 3500, 1),
    ("Paracetamol 500mg / IV Infusion", "Paracetamol", "Tablet/Infusion", 600, 1),
    ("Ibuprofen 400mg", "Ibuprofen", "Tablet", 750, 1),
    ("Diclofenac Potassium 50mg / 75mg Inj", "Diclofenac", "Tablet/Inj", 1200, 1),
    ("Tramadol 50mg Inj/Cap", "Tramadol", "Capsule/Inj", 1800, 1),
    ("Amlodipine 5mg / 10mg", "Amlodipine", "Tablet", 1600, 1),
    ("Lisinopril 5mg / 10mg", "Lisinopril", "Tablet", 2100, 1),
    ("Hydrochlorothiazide 25mg", "Hydrochlorothiazide", "Tablet", 900, 1),
    ("Metformin 500mg / 850mg", "Metformin", "Tablet", 1800, 1),
    ("Glibenclamide 5mg", "Glibenclamide", "Tablet", 1100, 1),
    ("Omeprazole 20mg / 40mg", "Omeprazole", "Capsule", 1500, 1),
    ("Oral Rehydration Salts + Zinc Sulfate", "ORS + Zinc", "Sachet/Tab", 850, 1),
    ("Metronidazole 400mg / IV Infusion", "Metronidazole", "Tablet/Infusion", 1100, 1),
    ("Folic Acid 5mg + Ferrous Sulfate", "Iron + Folic Acid", "Tablet", 700, 1),
    ("Hydroxyurea 500mg", "Hydroxyurea", "Capsule", 6500, 1),
    ("Salbutamol Inhaler 100mcg", "Salbutamol", "Inhaler", 3800, 1),
    ("Dextrose 5% / Normal Saline 0.9% IV 500ml", "IV Fluid", "Infusion", 1400, 1)
]
