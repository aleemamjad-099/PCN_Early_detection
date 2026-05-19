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

@app.get("/")
def read_root():
    return {"status": "online", "message": "PCN Early Detection API is running successfully!"}




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