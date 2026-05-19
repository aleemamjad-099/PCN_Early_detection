# """
# PCN Early Detection System — FastAPI Backend
# Final Year Project | NeuroScan AI
# """

# # ── Standard Library ──────────────────────────────────────────────────────────
# import os
# import time
# import logging
# import warnings

# # ── Third Party ───────────────────────────────────────────────────────────────
# import joblib
# import numpy as np
# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel, Field
# from typing import Literal

# # ---RAG imports---
# # RAGEngine ki jagah SimpleFallbackRAG use karein
# from rag.rag_engine import SimpleFallbackRAG as RAGEngine




# # ── Logging ───────────────────────────────────────────────────────────────────
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s [%(levelname)s] %(message)s"
# )
# logger = logging.getLogger(__name__)


# # ── App ───────────────────────────────────────────────────────────────────────
# app = FastAPI(
#     title="PCN Early Detection API",
#     description="""
# ## 🧠 Parkinson's Cognitive Neurology — Early Risk Detection

# Predicts neurological risk using **18 clinical + engineered features**.

# | Risk Label  | Threshold          |
# |-------------|--------------------|
# | Low Risk    | Probability < 40%  |
# | High Risk   | Probability >= 40% |

# > For clinical decision support only. Always verify with a licensed neurologist.
#     """,
#     version="2.0.0",
# )

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# # ── Model Loading ─────────────────────────────────────────────────────────────
# def _load_model_and_scaler():
#     """
#     Load model and scaler.
#     - Suppresses XGBoost pickle version warning at load time.
#     - Re-saves model in native XGBoost format (one-time) so future
#       restarts produce zero warnings.
#     """
#     with warnings.catch_warnings():
#         warnings.simplefilter("ignore")
#         mdl = joblib.load("final_medical_model.pkl")
#         scl = joblib.load("final_scaler.pkl")

#     native_path = "model_native.ubj"
#     if hasattr(mdl, "save_model") and not os.path.exists(native_path):
#         try:
#             mdl.save_model(native_path)
#             logger.info("XGBoost model saved in native format -> model_native.ubj")
#         except Exception as exc:
#             logger.warning(f"Could not save native model: {exc}")

#     return mdl, scl


# model = None
# scaler = None

# try:
#     model, scaler = _load_model_and_scaler()
#     logger.info("Model and scaler loaded successfully.")
# except FileNotFoundError as exc:
#     logger.error(f"File not found: {exc}")
# except Exception as exc:
#     logger.error(f"Unexpected error loading model: {exc}")


# # ── Request Schema ─────────────────────────────────────────────────────────────
# class PatientRequest(BaseModel):
#     """All clinical inputs for one patient assessment."""

#     age:                  int   = Field(..., ge=1,    le=120,    description="Age in years")
#     gender:               Literal["Male", "Female"]  = Field(..., description="Biological gender")
#     bmi:                  float = Field(..., ge=10.0, le=60.0,   description="Body Mass Index")
#     hba1c:                float = Field(..., ge=3.0,  le=15.0,   description="HbA1c level")
#     ldl:                  float = Field(..., ge=30.0, le=400.0,  description="LDL Cholesterol mg/dL")
#     ast:                  float = Field(..., ge=5.0,  le=500.0,  description="AST liver enzyme U/L")
#     alt:                  float = Field(..., ge=5.0,  le=500.0,  description="ALT liver enzyme U/L")
#     apoe_e4:              Literal["Yes", "No"]       = Field(..., description="APOE-e4 gene present")
#     memory_score:         float = Field(..., ge=1.0,  le=10.0,   description="Cognitive memory score 1-10")
#     sleep_hours:          float = Field(..., ge=1.0,  le=12.0,   description="Average nightly sleep hours")
#     vitamin_b12:          float = Field(..., ge=50.0, le=2000.0, description="Vitamin B12 pg/mL")
#     depression_score:     float = Field(..., ge=0.0,  le=10.0,   description="Depression severity 0-10")
#     family_history_neuro: Literal["Yes", "No"]       = Field(..., description="Family history of neuro disorders")

#     model_config = {
#         "json_schema_extra": {
#             "example": {
#                 "age": 65, "gender": "Male", "bmi": 28.5, "hba1c": 7.2,
#                 "ldl": 140.0, "ast": 25.0, "alt": 30.0, "apoe_e4": "No",
#                 "memory_score": 6.5, "sleep_hours": 7.0, "vitamin_b12": 400.0,
#                 "depression_score": 2.0, "family_history_neuro": "No",
#             }
#         }
#     }


# # ── Response Schema ────────────────────────────────────────────────────────────
# class PredictionResponse(BaseModel):
#     status:                 str
#     risk_label:             str
#     risk_level:             int
#     probability_percentage: str
#     probability_raw:        float
#     confidence:             str
#     engineered_features:    dict
#     input_summary:          dict
#     processing_time_ms:     float


# # ── Helpers ────────────────────────────────────────────────────────────────────
# def _to_binary(value: str, positives: list) -> int:
#     return 1 if value.lower() in [p.lower() for p in positives] else 0


# def _build_features(data: PatientRequest, gender_enc: int, apoe_enc: int, fam_enc: int):
#     metabolic_idx  = round((data.bmi * data.hba1c) / 10, 4)
#     liver_stress   = round(data.ast + data.alt, 4)
#     neuro_risk     = round((data.age * apoe_enc) + (fam_enc * 10), 4)
#     vascular_ratio = round(data.ldl / (data.vitamin_b12 + 1), 4)
#     mental_health  = round(data.memory_score - (data.depression_score * 0.7), 4)

#     features = [
#         data.age, gender_enc, data.bmi, data.hba1c, data.ldl,
#         data.ast, data.alt, apoe_enc, data.memory_score,
#         data.sleep_hours, data.vitamin_b12, data.depression_score,
#         fam_enc, metabolic_idx, liver_stress, neuro_risk,
#         vascular_ratio, mental_health,
#     ]

#     engineered = {
#         "metabolic_index":     metabolic_idx,
#         "liver_stress_score":  liver_stress,
#         "neuro_genetic_risk":  neuro_risk,
#         "vascular_b12_ratio":  vascular_ratio,
#         "mental_health_index": mental_health,
#     }

#     return features, engineered


# def _confidence_band(prob: float) -> str:
#     if prob < 0.15 or prob > 0.85:
#         return "High Confidence"
#     if prob < 0.30 or prob > 0.70:
#         return "Moderate Confidence"
#     return "Low Confidence (borderline — consult specialist)"



# # ── Routes ─────────────────────────────────────────────────────────────────────
# @app.get("/", tags=["Health"])
# def root():
#     return {
#         "status": "online",
#         "message": "PCN Early Detection API",
#         "version": "2.0.0",
#         "docs": "/docs",
#     }


# @app.get("/health", tags=["Health"])
# def health():
#     return {
#         "api":           "Online",
#         "model_loaded":  "Ready" if model  is not None else "Not Loaded",
#         "scaler_loaded": "Ready" if scaler is not None else "Not Loaded",
#     }


# @app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
# def predict(data: PatientRequest):
#     """Predict neurological risk for a single patient."""

#     if model is None or scaler is None:
#         raise HTTPException(status_code=503, detail="Model unavailable. Check server logs.")

#     t0 = time.perf_counter()

#     try:
#         gender_enc = _to_binary(data.gender,               ["male",  "m"])
#         apoe_enc   = _to_binary(data.apoe_e4,              ["yes",   "y", "1"])
#         fam_enc    = _to_binary(data.family_history_neuro, ["yes",   "y", "1"])

#         features, engineered = _build_features(data, gender_enc, apoe_enc, fam_enc)

#         scaled      = scaler.transform(np.array([features]))
#         probability = float(model.predict_proba(scaled)[0][1])
#         prediction  = 1 if probability >= 0.4 else 0
#         label       = "High Risk" if prediction == 1 else "Low Risk"
#         elapsed     = round((time.perf_counter() - t0) * 1000, 2)

#         logger.info(f"Prediction -> {label} | prob={probability:.4f} | age={data.age} | gender={data.gender}")

#         return PredictionResponse(
#             status="success",
#             risk_label=label,
#             risk_level=prediction,
#             probability_percentage=f"{round(probability * 100, 2)}%",
#             probability_raw=round(probability, 6),
#             confidence=_confidence_band(probability),
#             engineered_features=engineered,
#             input_summary={
#                 "age":            data.age,
#                 "gender":         "Male" if gender_enc == 1 else "Female",
#                 "apoe_e4":        bool(apoe_enc),
#                 "family_history": bool(fam_enc),
#             },
#             processing_time_ms=elapsed,
#         )

#     except Exception as exc:
#         logger.error(f"Prediction error: {exc}")
#         raise HTTPException(status_code=400, detail=str(exc))


# @app.post("/batch-predict", tags=["Prediction"])
# def batch_predict(patients: list[PatientRequest]):
#     """Bulk risk screening — up to 50 patients per request."""

#     if len(patients) > 50:
#         raise HTTPException(status_code=400, detail="Batch limit is 50 patients per request.")

#     results = []
#     for i, patient in enumerate(patients):
#         try:
#             result = predict(patient)
#             results.append({"patient_index": i, **result.model_dump()})
#         except HTTPException as exc:
#             results.append({"patient_index": i, "status": "error", "detail": exc.detail})

#     return {"total": len(patients), "results": results}








"""
PCN Early Detection — FastAPI Backend v3
=========================================
Startup order (critical):
  1. load_dotenv()          → reads .env into os.environ
  2. read GROQ_API_KEY      → from os.environ (now populated)
  3. import rag_engine      → safe: key is NOT read at module level
  4. init_engine(key)       → pass key explicitly → Groq ping → ready
  5. FastAPI routes active

Endpoints:
    GET  /health   — model + scaler + RAG status
    POST /predict  — PCN risk prediction
    POST /chat     — RAG chatbot (PCN-AI)
"""

import os
import sys
import time

# ══════════════════════════════════════════════════════════════════════════════
# STEP 1 — Load .env BEFORE anything else
# ══════════════════════════════════════════════════════════════════════════════
try:
    from dotenv import load_dotenv
    _env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    loaded = load_dotenv(_env_path, override=True)   # override=True forces reload
    print(f"[startup] .env loaded from {_env_path} → {loaded}")
except ImportError:
    # Manual fallback
    _env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(_env_path):
        with open(_env_path) as _f:
            for _line in _f:
                _line = _line.strip()
                if _line and not _line.startswith("#") and "=" in _line:
                    _k, _v = _line.split("=", 1)
                    os.environ[_k.strip()] = _v.strip()
        print("[startup] .env loaded manually (python-dotenv not installed)")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 2 — Read key NOW (env is loaded)
# ══════════════════════════════════════════════════════════════════════════════
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "").strip()
print(f"[startup] GROQ_API_KEY found: {'YES (' + GROQ_API_KEY[:8] + '...)' if GROQ_API_KEY else 'NO — check .env'}")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 3 — Import RAG (safe: key is NOT read at module level in rag_engine.py)
# ══════════════════════════════════════════════════════════════════════════════
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from rag.rag_engine import get_engine, init_engine
    _rag_importable = True
except Exception as _ie:
    _rag_importable = False
    print(f"[startup] RAG import failed: {_ie}")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 4 — Init engine with the key explicitly
# ══════════════════════════════════════════════════════════════════════════════
_rag_ready = False
_rag_msg   = "Not initialised"

if _rag_importable:
    _rag_ready, _rag_msg = init_engine(GROQ_API_KEY)
    print(f"[startup] RAG engine init → ready={_rag_ready}, msg={_rag_msg}")
else:
    _rag_msg = "RAG module could not be imported"

# ══════════════════════════════════════════════════════════════════════════════
# STEP 5 — FastAPI app + ML model
# ══════════════════════════════════════════════════════════════════════════════
import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="PCN Early Detection API",
    description="Pancreatic Cancer & Neurodegenerative Disorder Detection · RAG Chatbot",
    version="3.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── ML model & scaler ─────────────────────────────────────────────────────────
_BASE       = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH  = os.path.join(_BASE, "final_medical_model.pkl")
SCALER_PATH = os.path.join(_BASE, "final_scaler.pkl")

try:
    _model  = joblib.load(MODEL_PATH)
    _scaler = joblib.load(SCALER_PATH)
    _model_ready = True
    print("[startup] ML model + scaler loaded ✓")
except Exception as _me:
    _model = _scaler = None
    _model_ready = False
    print(f"[startup] ML model load failed: {_me}")


# ── Pydantic schemas ──────────────────────────────────────────────────────────
class PatientData(BaseModel):
    age:                  int   = Field(..., ge=1,   le=120)
    gender:               str
    bmi:                  float = Field(..., ge=10.0, le=60.0)
    hba1c:                float = Field(..., ge=3.0,  le=15.0)
    ldl:                  float = Field(..., ge=30.0, le=400.0)
    ast:                  float = Field(..., ge=5.0,  le=500.0)
    alt:                  float = Field(..., ge=5.0,  le=500.0)
    apoe_e4:              str
    memory_score:         float = Field(..., ge=1.0,  le=10.0)
    sleep_hours:          float = Field(..., ge=1.0,  le=12.0)
    vitamin_b12:          float = Field(..., ge=50.0, le=2000.0)
    depression_score:     float = Field(..., ge=0.0,  le=10.0)
    family_history_neuro: str


class ChatRequest(BaseModel):
    message: str  = Field(..., min_length=1, max_length=1000)
    history: list = Field(default_factory=list)


# ── Helpers ───────────────────────────────────────────────────────────────────
def _engineer(d: PatientData) -> dict:
    apoe = 1 if d.apoe_e4.lower()              == "yes" else 0
    fam  = 1 if d.family_history_neuro.lower() == "yes" else 0
    return {
        "metabolic_index":    round((d.bmi * d.hba1c) / 10, 4),
        "liver_stress_score": round(d.ast + d.alt, 4),
        "neuro_genetic_risk": round((d.age * apoe) + (fam * 10), 4),
        "vascular_b12_ratio": round(d.ldl / (d.vitamin_b12 + 1), 6),
        "mental_health_index":round(d.memory_score - (d.depression_score * 0.7), 4),
    }


# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {
        "status":        "online",
        "model_loaded":  "Ready" if _model_ready else "Error",
        "scaler_loaded": "Ready" if _model_ready else "Error",
        "rag_ready":     "Ready" if _rag_ready   else "Error",
        "rag_message":   _rag_msg,
    }


@app.post("/predict")
def predict(data: PatientData):
    if not _model_ready:
        raise HTTPException(503, "ML model not loaded. Check model files.")

    t0   = time.time()
    eng  = _engineer(data)
    apoe = 1 if data.apoe_e4.lower()              == "yes" else 0
    fam  = 1 if data.family_history_neuro.lower() == "yes" else 0
    gend = 1 if data.gender.lower()               == "male" else 0

    feats = np.array([[
        data.age, gend, data.bmi, data.hba1c, data.ldl,
        data.ast, data.alt, apoe,
        data.memory_score, data.sleep_hours, data.vitamin_b12,
        data.depression_score, fam,
        eng["metabolic_index"], eng["liver_stress_score"],
        eng["neuro_genetic_risk"], eng["vascular_b12_ratio"],
        eng["mental_health_index"],
    ]])

    try:
        scaled   = _scaler.transform(feats)
        prob_raw = float(_model.predict_proba(scaled)[0][1])
    except Exception as e:
        raise HTTPException(500, f"Prediction error: {e}")

    elapsed  = round((time.time() - t0) * 1000, 1)
    pct      = prob_raw * 100
    risk     = "High Risk" if prob_raw >= 0.40 else "Low Risk"
    conf     = (
        "Very High Confidence" if prob_raw >= 0.75 else
        "High Confidence"      if prob_raw >= 0.55 else
        "Moderate Confidence"  if prob_raw >= 0.35 else
        "High Confidence"
    )

    return {
        "status":                 "success",
        "risk_label":             risk,
        "probability_raw":        round(prob_raw, 6),
        "probability_percentage": f"{pct:.2f}%",
        "confidence":             conf,
        "processing_time_ms":     elapsed,
        "engineered_features":    eng,
    }


@app.post("/chat")
def chat(req: ChatRequest):
    """PCN-AI RAG chatbot — key is stored server-side only."""
    if not _rag_importable:
        raise HTTPException(503, "RAG module not available. Check rag/ folder.")

    if not _rag_ready:
        raise HTTPException(
            503,
            detail=(
                f"PCN-AI is offline: {_rag_msg}. "
                "Set GROQ_API_KEY in .env and restart the server."
            ),
        )

    engine = get_engine()
    try:
        # Validate & sanitize history — must be list of {user, assistant} dicts
        clean_history = []
        for item in (req.history or []):
            if (
                isinstance(item, dict)
                and "user" in item
                and "assistant" in item
                and isinstance(item["user"], str)
                and isinstance(item["assistant"], str)
            ):
                clean_history.append({
                    "user":      item["user"],
                    "assistant": item["assistant"],
                })

        answer, sources = engine.chat(
            query=req.message,
            history=clean_history,
        )
    except Exception as e:
        raise HTTPException(500, f"Chat error: {e}")

    return {
        "answer":  answer,
        "sources": [
            {
                "id":    s["id"],
                "topic": s["topic"],
                "score": round(s.get("score", 0.0), 3),
            }
            for s in sources
        ],
    }