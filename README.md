# 🧬 PCN Early Detection System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![XGBoost](https://img.shields.io/badge/XGBoost-1.7+-006400?style=for-the-badge)
![Groq](https://img.shields.io/badge/Groq_RAG-Llama3-F55036?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**AI-Powered Early Detection of Pancreatic Cancer & Neurodegenerative Disorders**

*Final Year Project — Government College University Faisalabad (GCUF)*  
*Department of Information Technology · 2024–2025*

---

**Team Members:** Aleem Amjad &nbsp;·&nbsp; Maham Faryad &nbsp;·&nbsp; Shafia Arooj

</div>

---

## 📋 Table of Contents

1. [Project Overview](#-project-overview)
2. [Key Features](#-key-features)
3. [Model Performance](#-model-performance)
4. [System Architecture](#-system-architecture)
5. [Dataset](#-dataset)
6. [Feature Engineering](#-feature-engineering)
7. [ML Pipeline](#-ml-pipeline)
8. [RAG Chatbot — PCN-AI](#-rag-chatbot--pcn-ai)
9. [Project Structure](#-project-structure)
10. [Installation & Setup](#-installation--setup)
11. [Running the Application](#-running-the-application)
12. [API Reference](#-api-reference)
13. [Configuration](#-configuration)
14. [Screenshots](#-screenshots)
15. [Clinical Disclaimer](#-clinical-disclaimer)

---

## 🎯 Project Overview

The **PCN Early Detection System** is a **2-in-1 AI-powered clinical decision support tool** that simultaneously screens patients for:

- 🦠 **Pancreatic Cancer (PC)** — the 3rd leading cause of cancer-related deaths, with only 11% 5-year survival rate when caught late
- 🧠 **Neurodegenerative Disorders (ND)** — including Alzheimer's and Parkinson's, where average diagnosis is delayed by 2–4 years

The system analyses **18 clinical biomarkers** from Electronic Health Records (EHR) and outputs a **unified PCN risk probability** with sub-20ms inference, a clinical PDF report, and an intelligent RAG-powered medical chatbot.

> **Why this matters:** Over 85% of pancreatic cancer cases are diagnosed at Stage III/IV when treatment is no longer curative. Early detection can increase 5-year survival from 3% → 80%.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🎯 **2-in-1 Detection** | Simultaneous pancreatic cancer + neurodegenerative disorder risk assessment |
| ⚡ **Real-time Inference** | Sub-20ms prediction via FastAPI REST API |
| 🧬 **18 Clinical Features** | 13 base biomarkers + 5 domain-engineered features |
| 🤖 **PCN-AI Chatbot** | RAG-powered medical Q&A using Groq Llama3 + FAISS |
| 📄 **PDF Reports** | Professional A4 clinical reports via ReportLab |
| 🌙 **Dark / Light Theme** | Toggle between professional UI themes |
| 📊 **Interactive Charts** | Plotly gauge, radar, bar, and donut charts |
| 🔐 **Secure API Key** | Groq key stored server-side in `.env` — never in frontend |
| 📱 **Session History** | Track multiple assessments per session |

---

## 📊 Model Performance

| Metric | Value |
|---|---|
| **Ensemble ROC-AUC** | **89.36%** |
| **XGBoost ROC-AUC** | **87.47%** |
| **Overall Accuracy** | **81%** |
| **Weighted F1-Score** | **82%** |
| **Macro F1-Score** | **78%** |
| **Risk Threshold** | **40%** probability |
| **GridSearchCV Fits** | 720 (144 combinations × 5-fold CV) |
| **Training Records** | 5,000 synthetic EHR samples |

### Classification Report (Test Set — n=1,000)

| Class | Precision | Recall | F1-Score | Support |
|---|---|---|---|---|
| 0 — Low Risk | 0.89 | 0.83 | 0.86 | 700 |
| 1 — High Risk | 0.66 | 0.76 | 0.71 | 300 |
| **Macro Avg** | **0.77** | **0.80** | **0.78** | 1000 |
| **Weighted Avg** | **0.82** | **0.81** | **0.81** | 1000 |

### Live Test Validation (5/5 ✅)

| Test Case | Expected | Result | Status |
|---|---|---|---|
| Age 28, Healthy Male, BMI 22 | Low Risk | **0.0%** | ✅ |
| Age 52, Borderline Male, BMI 28.5 | ~40-55% | **47.6%** | ✅ |
| Age 65, Healthy Senior, BMI 24 | Low Risk | **~5%** | ✅ |
| Age 72, Classic High Risk, BMI 34 | High Risk 80%+ | **99.84%** | ✅ |
| Age 80, Extreme Risk, BMI 38 | High Risk 90%+ | **99.33%** | ✅ |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    STREAMLIT FRONTEND (app.py)                   │
│  ┌──────────┐  ┌───────────┐  ┌──────────┐  ┌───────────────┐  │
│  │ Risk Form│  │ Charts &  │  │  Clinical│  │  PCN-AI RAG   │  │
│  │ (18 feat)│  │ Visualize │  │  PDF RPT │  │  Chatbot      │  │
│  └────┬─────┘  └─────┬─────┘  └────┬─────┘  └──────┬────────┘  │
└───────┼──────────────┼─────────────┼────────────────┼───────────┘
        │  POST /predict│             │         POST /chat
        ▼              ▼             ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FASTAPI BACKEND (api.py)                      │
│  ┌─────────────┐  ┌──────────────────────────────────────────┐  │
│  │ /predict    │  │ /chat  ← RAG Engine (singleton)          │  │
│  │ /health     │  │   ├── FAISS Vector Store (17 chunks)     │  │
│  └──────┬──────┘  │   ├── Keyword Retrieval (fallback)       │  │
│         │         │   └── Groq Llama3-8b (generation)        │  │
└─────────┼─────────┴──────────────────────────────────────────┘─┘
          │                           ▲
          ▼                           │ API Key from .env (secure)
┌─────────────────────┐     ┌─────────────────────────┐
│  ML ENSEMBLE MODEL  │     │    KNOWLEDGE BASE        │
│  ┌───────────────┐  │     │  • Pancreatic Cancer     │
│  │   XGBoost     │  │     │  • Neuro Disorders       │
│  │   +           │  │     │  • PCN ML Model          │
│  │  Logistic Reg │  │     │  • Biomarker Ranges      │
│  │  (soft-vote)  │  │     │  • Prevention            │
│  └───────────────┘  │     │  (17 chunks · 6 topics)  │
└─────────────────────┘     └─────────────────────────┘
          ▲
          │
┌─────────────────────┐
│  PREPROCESSING      │
│  StandardScaler     │
│  SMOTE Balancing    │
│  Feature Engineering│
└─────────────────────┘
```

---

## 🗃️ Dataset

### Generation (`data.ipynb`)

The dataset is **synthetically generated** to simulate realistic Electronic Health Records:

```python
generate_synthetic_ehr(
    num_samples  = 5000,
    positive_rate= 0.30,   # 30% High Risk, 70% Low Risk
    seed         = 42
)
```

### Features (13 Base)

| Feature | Type | Range | Clinical Significance |
|---|---|---|---|
| `age` | int | 40–90 | Risk doubles every decade after 50 |
| `sex` | str | M/F | Gender-based risk stratification |
| `bmi` | float | 16–55 | Obesity → metabolic + pancreatic risk |
| `hba1c` | float | 4.5–12 | Chronic hyperglycaemia → pancreatic stress |
| `ldl` | float | 40–260 | Vascular + lipid-neuro correlation |
| `ast` | float | 5–150 | Liver enzyme — hepatic stress marker |
| `alt` | float | 5–200 | Liver enzyme — hepatic inflammation |
| `apoe_e4` | int | 0/1 | Strongest genetic risk factor for Alzheimer's |
| `memory_score` | float | 1–10 | Cognitive function indicator |
| `sleep_hours` | float | 3–10 | <6hrs → amyloid buildup risk |
| `vitamin_b12` | float | 150–800 | Neuroprotective vitamin |
| `depression_score` | float | 0–10 | Neuro-psychiatric risk marker |
| `family_history_neuro` | int | 0/1 | 2-3x baseline risk multiplier |

### Risk Signal Calibration

The synthetic label is generated using a clinically-informed logit:

```python
risk_logit = (
    0.03 * (age - 60)
    + 0.04 * (hba1c - 6.0)
    + 0.02 * (bmi - 28.0)
    + 0.01 * (ldl - 130)
    + 0.015 * (ast - 25) + 0.015 * (alt - 25)
    + 0.40  * apoe_e4                         # Strong genetic signal
    + 0.03  * (7 - memory_score)
    + 0.02  * (7 - sleep_hours)
    + 0.015 * depression_score
    + 0.02  * family_history_neuro
    + noise (σ=0.4)
)
```

### Statistics

| Property | Value |
|---|---|
| Total Records | 5,000 |
| Positive Class (High Risk) | 1,500 (30%) |
| Negative Class (Low Risk) | 3,500 (70%) |
| Train Split | 4,000 (80%) |
| Test Split | 1,000 (20%) |
| After SMOTE (train) | Balanced |

---

## ⚗️ Feature Engineering

Five composite biomarker features are engineered from raw inputs:

| Engineered Feature | Formula | Clinical Rationale |
|---|---|---|
| **Metabolic Index** | `(BMI × HbA1c) / 10` | Combined metabolic burden — high values indicate diabetes+obesity co-risk |
| **Liver Stress Score** | `AST + ALT` | Hepatic dysfunction indicator — elevated in liver metastasis |
| **Neuro-Genetic Risk** | `(Age × APOE_flag) + (FamHx_flag × 10)` | Age-gene interaction — APOE-e4 risk amplifies with age |
| **Vascular / B12 Ratio** | `LDL / (Vitamin B12 + 1)` | High LDL + low B12 = dual cardiovascular-neurological risk |
| **Mental Health Index** | `Memory − (Depression × 0.7)` | Cognitive health composite — negative values are serious red flags |

---

## 🤖 ML Pipeline (`load_data.ipynb`)

### Step-by-Step

```
Raw EHR CSV
    │
    ├─ 1. Load & Encode        → sex: M=1, F=0
    ├─ 2. Feature Engineering  → 5 composite features added
    ├─ 3. Train/Test Split     → 80/20 stratified
    ├─ 4. StandardScaler       → zero-mean, unit-variance
    ├─ 5. SMOTE                → oversample minority class
    ├─ 6. GridSearchCV         → 144 combos × 5-fold CV = 720 fits
    ├─ 7. XGBoost Training     → best hyperparameters
    └─ 8. Ensemble Deploy      → XGBoost + LogisticRegression (soft-vote)
```

### Best Hyperparameters (GridSearchCV Result)

```python
{
    'n_estimators':     800,
    'learning_rate':    0.03,
    'max_depth':        10,
    'subsample':        0.7,
    'colsample_bytree': 0.7,
    'gamma':            0.1,
}
```

### Ensemble Architecture

```python
VotingClassifier(
    estimators=[
        ('xgb', XGBClassifier(**best_params)),   # Primary model
        ('lr',  LogisticRegression(              # Regularisation
                    max_iter=1000,
                    class_weight='balanced')),
    ],
    voting='soft'   # Probability averaging
)
```

### Output Files

```
final_medical_model.pkl   ← Trained VotingClassifier
final_scaler.pkl          ← Fitted StandardScaler
```

---

## 🤖 RAG Chatbot — PCN-AI

The system includes an intelligent medical chatbot powered by **Retrieval-Augmented Generation**:

```
User Query
    │
    ▼
Embed query (sentence-transformers: all-MiniLM-L6-v2)
    │
    ▼
FAISS similarity search → Top-4 relevant knowledge chunks
    │
    ▼
Build prompt: System + Context + History (last 3 turns) + Query
    │
    ▼
Groq API (llama3-8b-8192) → Medical answer
    │
    ▼
Answer + Source citations displayed in UI
```

### Knowledge Base (17 Chunks · 6 Topics)

| Topic | Chunks | Coverage |
|---|---|---|
| 🦠 Pancreatic Cancer | 6 | Overview, risk factors, symptoms, biomarkers, diagnosis, treatment |
| 🧠 Neurodegenerative Disorders | 5 | Overview, APOE-e4, Alzheimer's, Parkinson's, Vitamin B12 |
| ⚗️ PCN ML Model | 4 | Engineered features, architecture, performance, risk interpretation |
| 🥗 Prevention | 2 | Lifestyle modifications, when to see a doctor |
| 📋 Normal Ranges | 1 | All biomarker reference ranges |
| ℹ️ About PCN System | 1 | Project info, team, tech stack |

### Security

- ✅ API key stored **only** in `.env` — never in frontend
- ✅ Key passed explicitly to engine at startup — not read at module level
- ✅ No API key input field visible in UI

---

## 📁 Project Structure

```
LAST_PROJ_MEDI/
│
├── 📄 app.py                      # Streamlit frontend (Dark/Light theme)
├── 📄 api.py                      # FastAPI backend (predict + chat)
├── 📄 .env                        # API keys — DO NOT commit to Git
├── 📄 requirements.txt            # Python dependencies
├── 📄 synthetic_medical_ehr.csv   # Generated EHR dataset
├── 📄 final_medical_model.pkl     # Trained ensemble model
├── 📄 final_scaler.pkl            # Fitted StandardScaler
│
├── 📓 data.ipynb                  # Dataset generation notebook
├── 📓 load_data.ipynb             # Model training notebook
│
└── 📁 rag/
    ├── 📄 __init__.py             # Package init
    ├── 📄 knowledge_base.py       # 17 medical knowledge chunks
    └── 📄 rag_engine.py           # FAISS retrieval + Groq LLM
```

---

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.10+
- pip
- Virtual environment (recommended)

### Step 1 — Clone / Download

```bash
cd LAST_PROJ_MEDI
```

### Step 2 — Create Virtual Environment

```bash
python -m venv medvenv

# Windows
medvenv\Scripts\activate

# Linux / macOS
source medvenv/bin/activate
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Configure `.env`

Create a `.env` file in the project root:

```env
# Groq API Key — get free at https://console.groq.com
GROQ_API_KEY=gsk_your_actual_key_here

# Optional overrides
GROQ_MODEL=llama3-8b-8192
RAG_TOP_K=4
```

> **Get a free Groq API key:**
> 1. Go to [console.groq.com](https://console.groq.com)
> 2. Sign up (free)
> 3. Navigate to **API Keys** → **Create New Key**
> 4. Copy and paste into `.env`

### Step 5 — Generate Dataset (Optional)

If `synthetic_medical_ehr.csv` does not exist:

```bash
jupyter nbconvert --to script data.ipynb --stdout | python
# OR open data.ipynb and run all cells
```

### Step 6 — Train Model (Optional)

If `final_medical_model.pkl` and `final_scaler.pkl` do not exist:

```bash
# Open load_data.ipynb in Jupyter and run all cells
jupyter notebook load_data.ipynb
```

---

## 🚀 Running the Application

### Terminal 1 — Start FastAPI Backend

```bash
uvicorn api:app --reload --port 8000
```

Expected startup output:

```
[startup] .env loaded → True
[startup] GROQ_API_KEY found: YES (gsk_xxxx...)
[startup] RAG engine init → ready=True, msg=OK
[startup] ML model + scaler loaded ✓
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Terminal 2 — Start Streamlit Frontend

```bash
streamlit run app.py --server.port 8501
```

Open browser: [http://localhost:8501](http://localhost:8501)

### API Documentation (Swagger UI)

Open browser: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📡 API Reference

### `GET /health`

Check system status.

**Response:**
```json
{
  "status": "online",
  "model_loaded": "Ready",
  "scaler_loaded": "Ready",
  "rag_ready": "Ready",
  "rag_message": "OK"
}
```

---

### `POST /predict`

Run PCN risk assessment.

**Request Body:**
```json
{
  "age": 65,
  "gender": "Male",
  "bmi": 28.5,
  "hba1c": 6.2,
  "ldl": 145.0,
  "ast": 32.0,
  "alt": 28.0,
  "apoe_e4": "No",
  "memory_score": 7.0,
  "sleep_hours": 6.5,
  "vitamin_b12": 380.0,
  "depression_score": 3.0,
  "family_history_neuro": "No"
}
```

**Response:**
```json
{
  "status": "success",
  "risk_label": "Low Risk",
  "probability_raw": 0.127461,
  "probability_percentage": "12.75%",
  "confidence": "High Confidence",
  "processing_time_ms": 8.4,
  "engineered_features": {
    "metabolic_index": 17.67,
    "liver_stress_score": 60.0,
    "neuro_genetic_risk": 0.0,
    "vascular_b12_ratio": 0.38,
    "mental_health_index": 4.9
  }
}
```

---

### `POST /chat`

PCN-AI RAG chatbot query.

**Request Body:**
```json
{
  "message": "What are the symptoms of pancreatic cancer?",
  "history": []
}
```

**Response:**
```json
{
  "answer": "Pancreatic cancer symptoms often appear late...\n\n⚕ Please consult a licensed doctor...",
  "sources": [
    {"id": "pc_003", "topic": "Pancreatic Cancer Symptoms", "score": 0.847},
    {"id": "pc_002", "topic": "Pancreatic Cancer Risk Factors", "score": 0.621}
  ]
}
```

---

## ⚙️ Configuration

### `requirements.txt`

```
# Core ML
scikit-learn>=1.3.0
xgboost>=1.7.0
imbalanced-learn>=0.11.0
numpy>=1.24.0
pandas>=2.0.0
joblib>=1.3.0

# API Backend
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.0.0

# Frontend
streamlit>=1.28.0
plotly>=5.17.0

# PDF Generation
reportlab>=4.0.0

# RAG Chatbot
groq>=0.4.0
python-dotenv>=1.0.0

# Optional (better RAG retrieval)
faiss-cpu>=1.7.4
sentence-transformers>=2.2.2

# Utilities
requests>=2.31.0
```

### Risk Thresholds

| Probability | Risk Level | Action |
|---|---|---|
| 0–20% | Very Low Risk | Routine annual screening |
| 20–40% | Low Risk | Monitor risk factors |
| **40–60%** | **High Risk** | **Specialist consultation** |
| 60–80% | High Risk | Urgent medical evaluation |
| 80–100%+ | Very High Risk | Immediate specialist referral |

---

## 🖼️ Screenshots

| Feature | Description |
|---|---|
| **Main Dashboard** | Dark/Light theme, stat cards, API status |
| **Risk Assessment Form** | 18-feature clinical input form |
| **Result Overview** | Risk percentage, gauge chart, metric tiles |
| **Feature Analysis** | Radar chart + engineered features table |
| **Biomarker Charts** | Bar charts + risk distribution donut |
| **Clinical Report** | Downloadable PDF + Markdown report |
| **PCN-AI Chatbot** | RAG-powered medical Q&A interface |

---

## ⚠️ Clinical Disclaimer

> **IMPORTANT:** This system is a **research and decision-support tool only**, trained on **synthetic** Electronic Health Records. It is **NOT** a certified medical diagnostic device.
>
> - All results **MUST** be reviewed by a licensed oncologist or neurologist
> - Do **NOT** use this system as the sole basis for any clinical decision
> - This system does **NOT** replace professional medical advice, diagnosis, or treatment
> - The synthetic training data may not fully represent real-world clinical populations

---

## 🔒 Security Notes

- **Never commit `.env` to Git** — add it to `.gitignore`
- Groq API key is **never sent to or stored in the frontend**
- Key is loaded server-side via `python-dotenv` at startup

```bash
# Add to .gitignore
echo ".env" >> .gitignore
echo "*.pkl" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "rag/pcn_faiss.index" >> .gitignore
echo "rag/pcn_meta.pkl" >> .gitignore
```

---

## 👨‍💻 Technology Stack

| Layer | Technology |
|---|---|
| **ML Model** | XGBoost + Logistic Regression (Soft-Vote Ensemble) |
| **Preprocessing** | Scikit-Learn (StandardScaler, SMOTE) |
| **Hyperparameter Tuning** | GridSearchCV (5-fold Stratified CV) |
| **API Backend** | FastAPI + Uvicorn |
| **Frontend** | Streamlit + Plotly |
| **PDF Reports** | ReportLab |
| **RAG Retrieval** | FAISS + sentence-transformers |
| **LLM Generation** | Groq API (llama3-8b-8192) |
| **Environment** | python-dotenv |
| **Data** | NumPy + Pandas (Synthetic EHR) |

---

## 📚 References

1. Siegel, R.L. et al. (2023). *Cancer Statistics.* CA: A Cancer Journal for Clinicians.
2. World Health Organization. (2023). *Dementia Fact Sheet.*
3. Chen, T. & Guestrin, C. (2016). *XGBoost: A Scalable Tree Boosting System.* KDD.
4. Lewis, P. et al. (2020). *Retrieval-Augmented Generation for NLP.* NeurIPS.
5. Chawla, N.V. et al. (2002). *SMOTE: Synthetic Minority Over-sampling Technique.* JAIR.

---

<div align="center">

**PCN Early Detection System** · Final Year Project · GCUF · 2025

*Department of Information Technology · Government College University Faisalabad*

Made with ❤️ by **Aleem Amjad**, **Maham Faryad**, **Shafia Arooj**

</div>