"""
PCN Early Detection — RAG Knowledge Base
Medical knowledge chunks about Pancreatic Cancer & Neurodegenerative Disorders
"""

PCN_KNOWLEDGE = [

    # ── PANCREATIC CANCER ─────────────────────────────────────────────────────
    {
        "id": "pc_001",
        "topic": "Pancreatic Cancer Overview",
        "content": """
        Pancreatic cancer is one of the most lethal malignancies with a 5-year survival rate of 
        only 11%. It is the 3rd leading cause of cancer-related deaths. Over 85% of cases are 
        diagnosed at an advanced stage (Stage III or IV) when curative surgery is no longer possible.
        The most common type is pancreatic ductal adenocarcinoma (PDAC), accounting for 90% of cases.
        Early detection is critical — Stage I survival rate is 80% vs 3% at Stage IV.
        """
    },
    {
        "id": "pc_002",
        "topic": "Pancreatic Cancer Risk Factors",
        "content": """
        Major risk factors for pancreatic cancer include:
        - Age above 60 years (risk doubles every decade after 50)
        - Type 2 Diabetes (3x increased risk, especially new-onset diabetes after age 50)
        - Obesity and high BMI (BMI > 30 increases risk by 20%)
        - Smoking (doubles the risk, responsible for 25% of cases)
        - Chronic pancreatitis (long-term inflammation)
        - Family history (5-10% of cases are hereditary)
        - BRCA1, BRCA2, PALB2 gene mutations
        - High LDL cholesterol and elevated liver enzymes (AST, ALT)
        - Heavy alcohol consumption
        - H. pylori infection
        """
    },
    {
        "id": "pc_003",
        "topic": "Pancreatic Cancer Symptoms",
        "content": """
        Pancreatic cancer symptoms often appear late and include:
        - Jaundice (yellowing of skin/eyes) — most common early sign
        - Abdominal pain radiating to the back
        - Unexplained significant weight loss (>10% body weight)
        - New-onset diabetes (especially after age 50)
        - Loss of appetite and fatigue
        - Dark urine and pale/greasy stools
        - Blood clots (deep vein thrombosis)
        - Nausea and vomiting
        The pancreas has no nerve endings for early pain, making early detection extremely difficult.
        """
    },
    {
        "id": "pc_004",
        "topic": "Pancreatic Cancer Biomarkers",
        "content": """
        Key biomarkers used for pancreatic cancer detection and monitoring:
        - CA 19-9: Primary tumor marker, elevated in 70-80% of pancreatic cancer patients
        - CEA (Carcinoembryonic antigen): Secondary marker
        - HbA1c: Chronic high blood sugar linked to pancreatic dysfunction
        - AST and ALT: Liver enzymes elevated when cancer spreads to liver
        - LDL Cholesterol: Elevated lipid levels associated with increased risk
        - Bilirubin: Elevated in bile duct obstruction from tumor
        - BMI: Obesity is a significant modifiable risk factor
        In our PCN model, we use: Age, BMI, HbA1c, LDL, AST, ALT, Vitamin B12,
        Memory Score, Sleep Hours, Depression Score, APOE-e4 gene, Family History.
        """
    },
    {
        "id": "pc_005",
        "topic": "Pancreatic Cancer Diagnosis",
        "content": """
        Diagnostic methods for pancreatic cancer:
        - CT Scan (computed tomography): Gold standard for staging
        - MRI/MRCP: Best for ductal evaluation
        - Endoscopic Ultrasound (EUS): Most sensitive for small tumors
        - ERCP (Endoscopic retrograde cholangiopancreatography)
        - PET Scan: Detects metastasis
        - Biopsy: Definitive diagnosis via fine needle aspiration
        - Blood tests: CA 19-9, CEA, liver function tests
        - Liquid biopsy: Circulating tumor DNA (emerging technology)
        Early diagnosis (Stage I-II) dramatically improves outcomes.
        """
    },
    {
        "id": "pc_006",
        "topic": "Pancreatic Cancer Treatment",
        "content": """
        Treatment options for pancreatic cancer:
        - Surgery: Whipple procedure (pancreaticoduodenectomy) for resectable tumors
        - Chemotherapy: FOLFIRINOX, Gemcitabine + nab-Paclitaxel are standard regimens
        - Radiation therapy: Often combined with chemotherapy
        - Targeted therapy: Erlotinib for EGFR-positive tumors; PARP inhibitors for BRCA mutations
        - Immunotherapy: Still under clinical trial evaluation
        - Palliative care: Pain management, stent placement for bile duct obstruction
        Only 15-20% of patients are eligible for curative surgery at diagnosis.
        Median survival without treatment: 3-6 months.
        """
    },

    # ── NEURODEGENERATIVE DISORDERS ───────────────────────────────────────────
    {
        "id": "nd_001",
        "topic": "Neurodegenerative Disorders Overview",
        "content": """
        Neurodegenerative disorders are progressive diseases characterized by the loss of 
        neurons in the brain and nervous system. Major types include:
        - Alzheimer's Disease (AD): Most common, 60-70% of dementia cases
        - Parkinson's Disease (PD): Movement disorder, 2nd most common
        - Amyotrophic Lateral Sclerosis (ALS): Motor neuron disease
        - Huntington's Disease: Genetic, autosomal dominant
        - Multiple Sclerosis (MS): Autoimmune demyelinating disease
        - Vascular Dementia: Post-stroke cognitive decline
        Globally, 50 million people live with dementia; this number doubles every 20 years.
        """
    },
    {
        "id": "nd_002",
        "topic": "Neurodegenerative Risk Factors and APOE-e4 Gene",
        "content": """
        Key risk factors for neurodegenerative disorders:
        - APOE-e4 gene: Strongest genetic risk factor for Alzheimer's disease.
          One copy increases risk 3x; two copies increase risk 8-12x.
        - Age: Risk doubles every 5 years after age 65
        - Family history: First-degree relatives have 2-3x higher risk
        - Low Vitamin B12: Deficiency linked to cognitive decline and dementia
        - Poor sleep quality: Less than 6 hours increases amyloid buildup
        - Depression: Increases dementia risk by 65%
        - Low memory scores: Early cognitive decline indicator
        - Cardiovascular risk factors: Hypertension, high LDL, diabetes
        - Head trauma history
        - Low education level and cognitive reserve
        In our PCN model: APOE-e4, Family History, Memory Score, Sleep Hours,
        Depression Score, Vitamin B12, and Age are key neuro features.
        """
    },
    {
        "id": "nd_003",
        "topic": "Alzheimer's Disease",
        "content": """
        Alzheimer's Disease (AD) is the most common neurodegenerative disorder:
        - Characterized by amyloid-beta plaques and tau tangles in the brain
        - Progressive memory loss, confusion, and personality changes
        - Diagnosis average delay: 2-4 years from symptom onset
        - Biomarkers: CSF amyloid/tau ratio, PET imaging, blood p-tau181
        - Risk genes: APOE-e4 (susceptibility), APP, PSEN1, PSEN2 mutations (early-onset)
        - 7 stages from normal aging to severe dementia
        - No cure; treatments (Donepezil, Memantine) slow progression
        - New FDA-approved: Lecanemab (Leqembi) — anti-amyloid antibody therapy
        Low memory scores and high depression scores in our PCN model flag Alzheimer's risk.
        """
    },
    {
        "id": "nd_004",
        "topic": "Parkinson's Disease",
        "content": """
        Parkinson's Disease is the 2nd most common neurodegenerative disorder:
        - Loss of dopamine-producing neurons in substantia nigra
        - Cardinal features: Tremor, rigidity, bradykinesia, postural instability
        - Non-motor symptoms: Depression, sleep disorders, cognitive impairment
        - Diagnosis: Clinical (no definitive biomarker test yet)
        - Risk factors: Age, pesticide exposure, head trauma, family history
        - LRRK2, PINK1, SNCA gene mutations in familial PD
        - Treatment: Levodopa, dopamine agonists, DBS (deep brain stimulation)
        - Average diagnosis delay: 1-3 years
        Sleep disturbance (REM sleep behavior disorder) is an early warning sign,
        detectable via sleep hours tracking — a feature in our PCN model.
        """
    },
    {
        "id": "nd_005",
        "topic": "Vitamin B12 and Neurological Health",
        "content": """
        Vitamin B12 (cobalamin) is critical for neurological function:
        - Normal range: 200-900 pg/mL
        - Deficiency (<200 pg/mL): Peripheral neuropathy, cognitive decline, dementia
        - Suboptimal levels (200-300 pg/mL): Associated with increased dementia risk
        - Optimal for neuroprotection: 400-900 pg/mL
        - B12 is essential for myelin sheath production and nerve conduction
        - Low B12 elevates homocysteine — a neurotoxic amino acid damaging brain cells
        - Sources: Meat, fish, dairy, eggs; vegans at high deficiency risk
        - Supplementation: Methylcobalamin preferred for neurological benefits
        In our PCN model, Vitamin B12 is used in Vascular/B12 Ratio feature:
        LDL / (Vitamin B12 + 1) — low B12 increases this ratio, flagging neuro risk.
        """
    },

    # ── PCN MODEL FEATURES ────────────────────────────────────────────────────
    {
        "id": "model_001",
        "topic": "PCN Model Engineered Features Explanation",
        "content": """
        Our PCN system uses 5 engineered biomarker features derived from raw inputs:

        1. Metabolic Index = (BMI × HbA1c) / 10
           - Captures combined metabolic burden; high values indicate diabetes+obesity risk
           - Threshold concern: values > 20 suggest elevated pancreatic stress

        2. Liver Stress Score = AST + ALT
           - Elevated liver enzymes indicate hepatic dysfunction or cancer spread
           - Normal AST: 10-40 U/L; Normal ALT: 7-56 U/L
           - Score > 80 is clinically significant

        3. Neuro-Genetic Risk = (Age × APOE-e4_flag) + (Family_History_flag × 10)
           - Combines age-gene interaction with family history
           - APOE-e4 presence (1) dramatically increases score with age

        4. Vascular/B12 Ratio = LDL / (Vitamin B12 + 1)
           - High LDL with low B12 = dual cardiovascular + neuro risk
           - Values > 0.5 suggest concerning vascular-neurological profile

        5. Mental Health Index = Memory Score − (Depression Score × 0.7)
           - Lower scores indicate cognitive decline risk
           - Negative values are serious warning indicators
        """
    },
    {
        "id": "model_002",
        "topic": "PCN Model Architecture and Performance",
        "content": """
        The PCN Early Detection System uses an Ensemble Machine Learning approach:

        Model Architecture:
        - Primary: XGBoost Classifier (Extreme Gradient Boosting)
        - Secondary: Logistic Regression
        - Combination: Soft-voting ensemble (probability averaging)

        Training Details:
        - Dataset: 5,000+ synthetic Electronic Health Records (EHR)
        - Train/Test Split: 80% training, 20% testing (stratified)
        - Class Balancing: SMOTE (Synthetic Minority Oversampling Technique)
        - Normalization: StandardScaler
        - Hyperparameter Tuning: GridSearchCV — 144 combinations, 5-fold CV (720 fits)

        Best XGBoost Parameters:
        - n_estimators: 800, learning_rate: 0.03, max_depth: 10
        - subsample: 0.7, colsample_bytree: 0.7, gamma: 0.1

        Performance Metrics:
        - Ensemble ROC-AUC: 89.36% (primary metric)
        - XGBoost ROC-AUC: 87.47%
        - Overall Accuracy: 81%
        - Weighted F1-Score: 82%
        - Risk Threshold: 40% probability = High Risk classification
        """
    },
    {
        "id": "model_003",
        "topic": "PCN Risk Interpretation Guide",
        "content": """
        How to interpret PCN Early Detection System results:

        Risk Levels:
        - 0-20%: Very Low Risk — Routine annual screening recommended
        - 20-40%: Low Risk — Monitor risk factors, lifestyle modifications
        - 40-60%: Moderate-High Risk — Specialist consultation recommended
        - 60-80%: High Risk — Urgent medical evaluation required
        - 80-100%: Very High Risk — Immediate specialist referral mandatory

        Risk Threshold: 40% probability cutoff for High Risk classification

        Key Red Flags (High-Risk Indicators):
        - Age > 60 + BMI > 30 + HbA1c > 7.0 → Strong pancreatic cancer risk
        - APOE-e4 present + Family History + Memory Score < 5 → Alzheimer's risk
        - AST + ALT > 80 → Liver stress / possible metastasis
        - Vitamin B12 < 200 pg/mL → Neurological deficiency alert
        - Depression Score > 7 + Sleep < 5 hours → Neuro-psychiatric risk

        IMPORTANT: This system is a decision-support tool only.
        All results MUST be reviewed by a licensed medical professional.
        """
    },
    {
        "id": "model_004",
        "topic": "Normal vs Abnormal Biomarker Ranges",
        "content": """
        Clinical reference ranges for PCN biomarkers:

        | Biomarker      | Normal Range        | Concern Level        |
        |----------------|---------------------|----------------------|
        | Age            | —                   | >60 elevated risk    |
        | BMI            | 18.5 – 24.9         | >30 obese            |
        | HbA1c          | <5.7%               | >6.5% = Diabetes     |
        | LDL            | <100 mg/dL optimal  | >160 mg/dL high      |
        | AST            | 10 – 40 U/L         | >40 elevated         |
        | ALT            | 7 – 56 U/L          | >56 elevated         |
        | Vitamin B12    | 200 – 900 pg/mL     | <200 deficient       |
        | Memory Score   | 7 – 10 (good)       | <5 concerning        |
        | Sleep Hours    | 7 – 9 hours         | <6 or >10 abnormal   |
        | Depression     | 0 – 2 (minimal)     | >6 severe            |

        Genetic Flags:
        - APOE-e4 gene presence: Significantly increases Alzheimer's risk
        - Family History of Neuro Disorders: 2-3x baseline risk increase
        """
    },

    # ── PREVENTION & LIFESTYLE ────────────────────────────────────────────────
    {
        "id": "prev_001",
        "topic": "Prevention and Lifestyle Modifications",
        "content": """
        Evidence-based strategies to reduce PCN risk:

        Pancreatic Cancer Prevention:
        - Maintain healthy BMI (18.5-24.9) — reduces risk by 20%
        - Quit smoking — single most impactful modifiable factor
        - Control diabetes — keep HbA1c < 7%
        - Limit alcohol — maximum 1-2 units/day
        - Mediterranean diet rich in vegetables, fruits, whole grains
        - Regular exercise (150 min moderate/week)
        - Control LDL cholesterol through diet and statins if needed

        Neurodegenerative Disease Prevention:
        - Cognitive activities: Reading, puzzles, learning new skills
        - Social engagement: Reduces dementia risk by 40%
        - Physical exercise: 30 min aerobic activity 5x/week
        - Sleep hygiene: 7-9 hours quality sleep
        - Mediterranean-MIND diet: Rich in leafy greens, berries, fish
        - Vitamin B12 supplementation for deficient individuals
        - Manage depression and anxiety proactively
        - Blood pressure and cholesterol control
        - Avoid head trauma (use helmets, fall prevention)
        """
    },
    {
        "id": "prev_002",
        "topic": "When to See a Doctor",
        "content": """
        Seek immediate medical attention if you experience:

        Pancreatic Cancer Warning Signs:
        - Sudden new-onset diabetes after age 50
        - Unexplained weight loss > 5kg in 3 months
        - Persistent abdominal/back pain
        - Jaundice (yellow skin or eyes)
        - Changes in stool (pale, greasy, floating)
        - Dark urine without obvious cause

        Neurological Warning Signs:
        - Progressive memory loss affecting daily activities
        - Difficulty finding words or following conversations
        - Getting lost in familiar places
        - Personality or mood changes
        - Tremors, stiffness, or balance problems
        - Significant sleep behavior changes (acting out dreams)

        Annual Screening Recommended For:
        - Age > 50 with diabetes + weight loss
        - Strong family history of pancreatic cancer
        - BRCA1/2 or PALB2 gene mutation carriers
        - APOE-e4 carriers over age 65
        - Chronic pancreatitis patients
        """
    },

    # ── ABOUT PCN SYSTEM ──────────────────────────────────────────────────────
    {
        "id": "sys_001",
        "topic": "About PCN Early Detection System",
        "content": """
        The PCN Early Detection System is a Final Year Project developed at
        Government College University Faisalabad (GCUF), Department of Information Technology.

        Team Members: Aleem Amjad, Maham Faryad, Shafia Arooj

        System Capabilities:
        - Simultaneous detection of Pancreatic Cancer AND Neurodegenerative Disorders
        - Input: 13 clinical biomarkers → Output: Unified PCN risk probability
        - Real-time prediction in under 20ms via FastAPI REST API
        - Interactive Streamlit web interface with Dark/Light themes
        - Session history tracking for multiple assessments
        - Professional clinical PDF report generation
        - AI-powered medical chatbot (RAG + Groq) for Q&A

        Technology Stack:
        - ML: XGBoost, Scikit-Learn, SMOTE, GridSearchCV
        - Backend: FastAPI (Python)
        - Frontend: Streamlit
        - RAG: FAISS + sentence-transformers + Groq (Llama3)
        - Data: Synthetic EHR (5,000 records, 18 features)

        DISCLAIMER: This system is for research and decision-support only.
        Results must be reviewed by licensed medical professionals.
        """
    },
]

def get_all_chunks():
    """Return all knowledge chunks as list of (id, topic, content) tuples"""
    return [(k["id"], k["topic"], k["content"]) for k in PCN_KNOWLEDGE]

def get_topics():
    """Return all available topics"""
    return [k["topic"] for k in PCN_KNOWLEDGE]

if __name__ == "__main__":
    print(f"Total knowledge chunks: {len(PCN_KNOWLEDGE)}")
    for k in PCN_KNOWLEDGE:
        print(f"  [{k['id']}] {k['topic']}")