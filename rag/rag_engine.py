"""
PCN RAG Engine v4  — KEY FIX
==============================
Root cause of previous bug:
  GROQ_API_KEY was read at MODULE IMPORT TIME (module-level code).
  When api.py imported rag_engine, .env was not yet loaded,
  so GROQ_API_KEY was always empty string "".

Fix:
  - Key is read LAZILY inside init(), not at module level.
  - engine_status(key) accepts the key explicitly from caller.
  - get_engine() is a singleton that gets initialised once with the key.
"""

import os
import pickle
from typing import List, Tuple, Optional

# ── Optional packages (detected at import time, OK) ──────────────────────────
try:
    from groq import Groq
    _GROQ_PKG = True
except ImportError:
    _GROQ_PKG = False

try:
    from sentence_transformers import SentenceTransformer
    import faiss
    import numpy as np
    _FAISS_OK = True
except ImportError:
    _FAISS_OK = False

from rag.knowledge_base import PCN_KNOWLEDGE

_INDEX_PATH = os.path.join(os.path.dirname(__file__), "pcn_faiss.index")
_META_PATH  = os.path.join(os.path.dirname(__file__), "pcn_meta.pkl")

_GROQ_MODEL = "llama-3.1-8b-instant"
_TOP_K      = 4

_STOPWORDS = {
    "what","is","the","a","an","how","why","when","does","do","can","tell",
    "me","about","explain","are","my","i","for","in","of","to","and","or",
    "kya","hai","ka","ki","ko","se","mein","hota","hain","ky","wala","bata",
    "please","give","define","describe",
}

_SYSTEM_PROMPT = (
    "You are PCN-AI, a medical assistant specialising in Pancreatic Cancer (PC) "
    "and Neurodegenerative Disorders (ND). You are part of the PCN Early Detection "
    "System — Final Year Project by Aleem Amjad, Maham Faryad, Shafia Arooj at GCUF.\n\n"
    "RULES:\n"
    "• Answer ONLY from the CONTEXT below. Never hallucinate.\n"
    "• Be concise, warm, medically accurate. Max 220 words.\n"
    "• Use bullet points where helpful.\n"
    "• Always end with: '⚕ Please consult a licensed doctor for personal medical decisions.'\n\n"
    "CONTEXT:\n{context}"
)


# ─────────────────────────────────────────────────────────────────────────────
class SimpleRAG:
    """
    Keyword retrieval + Groq.
    Requires:  pip install groq python-dotenv
    Key is injected via init(key=...) — NEVER read at module level.
    """

    def __init__(self):
        self._client: Optional["Groq"] = None
        self.ready   = False
        self.error   = ""

    # ── Init receives the key explicitly ─────────────────────────────────────
    def init(self, key: str) -> Tuple[bool, str]:
        """
        Initialise with the given Groq API key.
        Safe to call multiple times — idempotent if already ready.
        """
        if self.ready:
            return True, "already initialised"

        if not _GROQ_PKG:
            self.error = "groq package not installed — pip install groq"
            return False, self.error

        if not key or key.startswith("gsk_your") or len(key) < 20:
            self.error = "GROQ_API_KEY is empty or placeholder — check .env file"
            return False, self.error

        try:
            self._client = Groq(api_key=key)
            # Quick connectivity ping
            self._client.chat.completions.create(
                model=_GROQ_MODEL,
                messages=[{"role": "user", "content": "hi"}],
                max_tokens=3,
            )
            self.ready = True
            return True, "OK"
        except Exception as exc:
            self.error = f"Groq init failed: {exc}"
            return False, self.error

    # ── Keyword retrieval ─────────────────────────────────────────────────────
    def _retrieve(self, query: str, k: int = _TOP_K) -> List[dict]:
        words = set(query.lower().split()) - _STOPWORDS
        scored = []
        for chunk in PCN_KNOWLEDGE:
            text  = (chunk["topic"] + " " + chunk["content"]).lower()
            score = sum(1 for w in words if w in text)
            if any(w in chunk["topic"].lower() for w in words):
                score += 3
            scored.append((score, chunk))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            {
                "id":      c["id"],
                "topic":   c["topic"],
                "content": c["content"].strip(),
                "score":   float(s),
            }
            for s, c in scored[:k]
        ]

    # ── Chat ──────────────────────────────────────────────────────────────────
    def chat(
        self,
        query:   str,
        history: Optional[List[dict]] = None,
    ) -> Tuple[str, List[dict]]:

        if not self.ready:
            return (
                f"⚠️ PCN-AI is offline: {self.error}\n\n"
                "Please set `GROQ_API_KEY` in your `.env` file and restart the server.",
                [],
            )

        chunks  = self._retrieve(query)
        context = "\n\n".join(
            f"[{c['topic']}]\n{c['content']}" for c in chunks
        )

        messages = [
            {
                "role":    "system",
                "content": _SYSTEM_PROMPT.format(context=context),
            }
        ]

        # Last 3 conversation turns for context (defensive access)
        for t in (history or [])[-3:]:
            if isinstance(t, dict) and "user" in t and "assistant" in t:
                messages.append({"role": "user",      "content": str(t["user"])})
                messages.append({"role": "assistant", "content": str(t["assistant"])})

        messages.append({"role": "user", "content": query})

        try:
            resp   = self._client.chat.completions.create(
                model=_GROQ_MODEL,
                messages=messages,
                temperature=0.25,
                max_tokens=450,
            )
            answer = resp.choices[0].message.content.strip()
        except Exception as exc:
            answer = f"⚠️ Groq API error: {exc}"

        return answer, chunks


# ─────────────────────────────────────────────────────────────────────────────
class FaissRAG(SimpleRAG):
    """
    Semantic retrieval via sentence-transformers + FAISS.
    Falls back silently to keyword retrieval if FAISS unavailable.
    Requires additionally:  pip install sentence-transformers faiss-cpu
    """

    def __init__(self):
        super().__init__()
        self._emb:   Optional["SentenceTransformer"] = None
        self._index: Optional["faiss.Index"]         = None
        self._meta:  List[dict]                      = []

    def init(self, key: str) -> Tuple[bool, str]:
        ok, msg = super().init(key)
        if not ok:
            return ok, msg
        try:
            self._emb = SentenceTransformer("all-MiniLM-L6-v2")
            if os.path.exists(_INDEX_PATH) and os.path.exists(_META_PATH):
                self._index = faiss.read_index(_INDEX_PATH)
                with open(_META_PATH, "rb") as f:
                    self._meta = pickle.load(f)
            else:
                self._build_index()
        except Exception:
            self._index = None   # fall back to keyword silently
        return True, "OK"

    def _build_index(self):
        texts, self._meta = [], []
        for c in PCN_KNOWLEDGE:
            texts.append(f"{c['topic']}. {c['content'].strip()}")
            self._meta.append({
                "id":      c["id"],
                "topic":   c["topic"],
                "content": c["content"].strip(),
            })
        embs = self._emb.encode(
            texts, normalize_embeddings=True, show_progress_bar=False
        ).astype("float32")
        self._index = faiss.IndexFlatIP(embs.shape[1])
        self._index.add(embs)
        faiss.write_index(self._index, _INDEX_PATH)
        with open(_META_PATH, "wb") as f:
            pickle.dump(self._meta, f)

    def _retrieve(self, query: str, k: int = _TOP_K) -> List[dict]:
        if self._index is None or self._emb is None:
            return super()._retrieve(query, k)   # keyword fallback
        q_emb = self._emb.encode(
            [query], normalize_embeddings=True
        ).astype("float32")
        scores, idxs = self._index.search(q_emb, k)
        return [
            {**self._meta[i], "score": float(s)}
            for s, i in zip(scores[0], idxs[0])
            if i >= 0
        ]


# ── Singleton ─────────────────────────────────────────────────────────────────
_engine_instance: Optional[SimpleRAG] = None


def get_engine() -> SimpleRAG:
    """Return (or lazily create) the singleton engine."""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = FaissRAG() if _FAISS_OK else SimpleRAG()
    return _engine_instance


def init_engine(key: str) -> Tuple[bool, str]:
    """
    Initialise the singleton engine with the given key.
    Call this ONCE from api.py startup, AFTER load_dotenv().
    Returns (is_ready, message).
    """
    return get_engine().init(key)