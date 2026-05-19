

"""
PCN Early Detection System — Professional Frontend v4.1
Pancreatic Cancer & Neurodegenerative Disorder Detection
Final Year Project | Medical AI | GCUF
"""



# 🌐 Cloud Secrets se URL check karne ke liye safe bypass
import os

# Agar Streamlit Secrets me API_URL mojud hai (Cloud par), to wo use karein
if "API_URL" in os.environ:
    API_URL = os.environ["API_URL"]
else:
    # Agar aap local computer par chala rahe hain, to purana localhost chalega
    API_URL = "http://127.0.0.1:8000"

# ⚠️ Sirf local par uvicorn chalane ke liye check (Cloud crash se bachne ke liye)
if "API_URL" not in os.environ:
    # ⬇️ JO AAPKA PURANA SUBPROCESS WALA CODE THA, WOH IS IF KE ANDAR RAKHEIN ⬇️
    # Jaise aapne uvicorn start kiya hua tha:
    try:
        import subprocess
        # Agar pehle se chal raha ho to theek, warna start karein
        # os.system("uvicorn api:app --reload &") ya jo bhi aapka pehle wala startup line tha
        pass
    except Exception:
        pass



import time, io, datetime, re, requests
import streamlit as st
import plotly.graph_objects as go

# ── RAG status loaded once at startup from backend /health ────────────────────
API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="PCN Early Detection",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Session State ─────────────────────────────────────────────────────────────
if "dark_mode"        not in st.session_state: st.session_state.dark_mode        = False
if "assessment_count" not in st.session_state: st.session_state.assessment_count = 0
if "history"          not in st.session_state: st.session_state.history          = []
if "chat_messages"    not in st.session_state: st.session_state.chat_messages    = []
# pending_msg: holds a question submitted via st.chat_input, processed on next run
if "pending_msg"      not in st.session_state: st.session_state.pending_msg      = None

D = st.session_state.dark_mode

# ── Theme ─────────────────────────────────────────────────────────────────────
if D:
    BG="#111827";CARD="#1a2236";CARD2="#1f2b42";BORDER="#263352";BORDER2="#2e3d5e"
    TXT="#e2e8f0";TXT_S="#94a3b8";TXT_M="#5a7095";INP="#141e30"
    BLUE="#4f8ef7";BLUE_LT="rgba(79,142,247,0.12)";BLUE_MD="rgba(79,142,247,0.22)"
    TEAL="#2dd4bf";TEAL_LT="rgba(45,212,191,0.10)"
    RED="#f87171";RED_LT="rgba(248,113,113,0.10)";RED_MD="rgba(248,113,113,0.22)"
    GREEN="#4ade80";GREEN_LT="rgba(74,222,128,0.10)";GREEN_MD="rgba(74,222,128,0.22)"
    AMBER="#fbbf24";AMBER_LT="rgba(251,191,36,0.10)"
    DISC_TXT="#fbbf24";DISC_BORD="rgba(251,191,36,0.30)"
    NAV="#151f33";SHADOW="0 4px 20px rgba(0,0,0,0.40)"
    PLY_BG="#1a2236";PLY_PAPER="#1a2236";GRID="#263352";TICK="#5a7095";GAUGE_BG="#1a2236"
    BTN_SHADOW="0 4px 18px rgba(79,142,247,0.45)";PURPLE="#a78bfa"
else:
    BG="#f4f7fe";CARD="#ffffff";CARD2="#f8faff";BORDER="#dce6f7";BORDER2="#bdd0f0"
    TXT="#0d1b3e";TXT_S="#2d4a80";TXT_M="#7a96c2";INP="#f0f5ff"
    BLUE="#1d4ed8";BLUE_LT="#eef2ff";BLUE_MD="#bfdbfe"
    TEAL="#0f766e";TEAL_LT="#f0fdfa"
    RED="#b91c1c";RED_LT="#fef2f2";RED_MD="#fecaca"
    GREEN="#15803d";GREEN_LT="#f0fdf4";GREEN_MD="#bbf7d0"
    AMBER="#b45309";AMBER_LT="#fffbeb"
    DISC_TXT="#92400e";DISC_BORD="#fde68a"
    NAV="#ffffff";SHADOW="0 2px 16px rgba(29,78,216,0.08)"
    PLY_BG="#ffffff";PLY_PAPER="#ffffff";GRID="#e8efff";TICK="#7a96c2";GAUGE_BG="white"
    BTN_SHADOW="0 4px 18px rgba(29,78,216,0.30)";PURPLE="#7c3aed"

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&family=Playfair+Display:wght@700;900&display=swap');
*,*::before,*::after{{box-sizing:border-box;}}
html,body,.stApp{{background:{BG}!important;font-family:'IBM Plex Sans',sans-serif!important;color:{TXT}!important;}}
.main .block-container{{padding:0 2rem 6rem;max-width:1340px;margin:0 auto;}}
#MainMenu,footer,header{{visibility:hidden;}}
section[data-testid="stSidebar"]{{display:none!important;}}
.pcn-nav{{background:{NAV};border-bottom:1.5px solid {BORDER};padding:0.85rem 0 0.75rem;margin-bottom:2rem;display:flex;align-items:center;justify-content:space-between;gap:1rem;}}
.pcn-nl{{display:flex;align-items:center;gap:1.1rem;}}
.pcn-logo{{width:44px;height:44px;background:linear-gradient(140deg,{BLUE} 0%,#6366f1 100%);border-radius:12px;display:flex;align-items:center;justify-content:center;font-family:'IBM Plex Mono',monospace;font-weight:600;font-size:0.82rem;color:#fff;box-shadow:0 4px 14px rgba(29,78,216,0.35);flex-shrink:0;letter-spacing:-0.03em;}}
.pcn-title{{font-weight:700;font-size:1.05rem;color:{TXT};line-height:1.2;}}
.pcn-sub{{font-size:0.72rem;color:{TXT_M};font-weight:400;margin-top:2px;}}
.pcn-tags{{display:flex;align-items:center;gap:0.55rem;flex-wrap:wrap;}}
.ptag{{font-size:0.66rem;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;padding:0.25rem 0.75rem;border-radius:100px;border:1px solid;}}
.ptag-b{{color:{BLUE};background:{BLUE_LT};border-color:{BLUE_MD};}}.ptag-t{{color:{TEAL};background:{TEAL_LT};border-color:{TEAL}44;}}.ptag-m{{color:{TXT_M};background:transparent;border-color:{BORDER2};}}
.stat-row{{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-bottom:2rem;}}
.scard{{background:{CARD};border:1px solid {BORDER};border-radius:16px;padding:1.3rem 1.5rem;box-shadow:{SHADOW};position:relative;overflow:hidden;transition:transform .2s,box-shadow .2s;}}
.scard:hover{{transform:translateY(-3px);box-shadow:0 8px 28px rgba(29,78,216,0.13);}}
.scard::before{{content:'';position:absolute;top:0;left:0;right:0;height:3.5px;background:linear-gradient(90deg,var(--ca),var(--cb));}}
.scard.bl{{--ca:{BLUE};--cb:#818cf8;}}.scard.te{{--ca:{TEAL};--cb:#06b6d4;}}.scard.am{{--ca:{AMBER};--cb:#f59e0b;}}.scard.sl{{--ca:{TXT_M};--cb:{BORDER2};}}
.sc-icon{{font-size:1.45rem;margin-bottom:0.55rem;}}.sc-lbl{{font-size:0.65rem;text-transform:uppercase;letter-spacing:0.12em;color:{TXT_M};font-weight:600;margin-bottom:0.3rem;}}
.sc-val{{font-size:1.95rem;font-weight:700;color:{TXT};line-height:1;font-family:'Playfair Display',serif;}}.sc-sub{{font-size:0.71rem;color:{TXT_M};margin-top:0.3rem;}}
.sbar{{border-radius:12px;padding:0.7rem 1.3rem;font-size:0.8rem;font-weight:500;display:flex;align-items:center;gap:0.65rem;margin-bottom:1.8rem;border:1px solid;}}
.sbar.ok{{background:{GREEN_LT};border-color:{GREEN_MD};color:{GREEN};}}.sbar.err{{background:{RED_LT};border-color:{RED_MD};color:{RED};}}
.dot-p{{width:9px;height:9px;border-radius:50%;flex-shrink:0;background:{GREEN};box-shadow:0 0 0 3px {GREEN_MD};animation:dp 2s ease-in-out infinite;}}
.dot-e{{background:{RED};box-shadow:none;animation:none;}}
@keyframes dp{{0%,100%{{box-shadow:0 0 0 3px {GREEN_MD};}}50%{{box-shadow:0 0 0 6px rgba(74,222,128,0.08);}}}}
.sbar code{{font-family:'IBM Plex Mono',monospace;font-size:0.75rem;background:rgba(74,222,128,0.15);padding:1px 7px;border-radius:5px;}}
.sbar.err code{{background:rgba(248,113,113,0.15);}}
.slbl{{font-size:0.66rem;font-weight:700;text-transform:uppercase;letter-spacing:0.16em;color:{TXT_M};display:flex;align-items:center;gap:0.6rem;margin:0 0 1.1rem;}}
.slbl::after{{content:'';flex:1;height:1px;background:{BORDER};}}
.fcard{{background:{CARD};border:1px solid {BORDER};border-radius:20px;padding:2rem 2.2rem;margin-bottom:1.4rem;box-shadow:{SHADOW};}}
.fhead{{display:flex;align-items:center;gap:0.7rem;font-size:0.72rem;font-weight:700;color:{TXT_S};text-transform:uppercase;letter-spacing:0.11em;margin:0 0 1.4rem;padding-bottom:1rem;border-bottom:1px solid {BORDER};}}
.fhd{{width:28px;height:28px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:0.88rem;flex-shrink:0;}}
.fhd-b{{background:{BLUE_LT};}}.fhd-t{{background:{TEAL_LT};}}.fhd-a{{background:{AMBER_LT};}}
.stNumberInput > div > div > input{{background:{INP}!important;border:1.5px solid {BORDER2}!important;border-radius:10px!important;color:{TXT}!important;font-family:'IBM Plex Sans',sans-serif!important;font-size:0.95rem!important;font-weight:500!important;padding:0.55rem 0.9rem!important;}}
.stNumberInput > div > div > input:focus{{border-color:{BLUE}!important;box-shadow:0 0 0 3px {BLUE_MD}!important;background:{CARD}!important;}}
div[data-baseweb="select"] > div{{background:{INP}!important;border:1.5px solid {BORDER2}!important;border-radius:10px!important;color:{TXT}!important;font-family:'IBM Plex Sans',sans-serif!important;font-weight:500!important;}}
div[data-baseweb="select"] > div:focus-within{{border-color:{BLUE}!important;box-shadow:0 0 0 3px {BLUE_MD}!important;}}
div[data-baseweb="popover"] li{{color:{TXT}!important;background:{CARD}!important;}}
div[data-baseweb="popover"] li:hover{{background:{BLUE_LT}!important;}}
div[data-baseweb="popover"] > div > div{{background:{CARD}!important;border-color:{BORDER}!important;}}
.stSlider > div > div > div > div{{background:{BLUE}!important;}}
.stSlider [data-testid="stThumbValue"]{{color:{BLUE}!important;font-weight:700!important;font-family:'IBM Plex Mono',monospace!important;font-size:0.82rem!important;background:{CARD}!important;border:1px solid {BORDER2}!important;border-radius:6px!important;padding:1px 6px!important;}}
label{{color:{TXT_S}!important;font-size:0.72rem!important;font-weight:600!important;text-transform:uppercase!important;letter-spacing:0.10em!important;font-family:'IBM Plex Sans',sans-serif!important;}}
.stFormSubmitButton > button{{width:100%!important;background:linear-gradient(135deg,{BLUE} 0%,#4f46e5 100%)!important;border:none!important;border-radius:12px!important;color:#fff!important;font-family:'IBM Plex Sans',sans-serif!important;font-weight:700!important;font-size:1rem!important;letter-spacing:0.04em!important;padding:0.95rem 2rem!important;box-shadow:{BTN_SHADOW}!important;transition:all .22s!important;}}
.stFormSubmitButton > button:hover{{transform:translateY(-2px)!important;box-shadow:0 8px 28px rgba(29,78,216,0.55)!important;background:linear-gradient(135deg,#1e40af 0%,#4338ca 100%)!important;}}
.stFormSubmitButton > button p{{color:#fff!important;font-size:1rem!important;font-weight:700!important;}}
.stButton > button{{background:{CARD2}!important;border:1.5px solid {BORDER2}!important;color:{TXT_S}!important;border-radius:10px!important;font-family:'IBM Plex Sans',sans-serif!important;font-weight:600!important;font-size:0.82rem!important;padding:0.5rem 1rem!important;transition:all .18s!important;}}
.stButton > button:hover{{border-color:{BLUE}!important;color:{BLUE}!important;background:{BLUE_LT}!important;}}
.rcard{{background:{CARD};border:1px solid {BORDER};border-radius:20px;padding:2.2rem 2.5rem;box-shadow:{SHADOW};position:relative;overflow:hidden;}}
.rcard.high{{border-left:5px solid {RED};}}.rcard.low{{border-left:5px solid {GREEN};}}
.rbadge{{display:inline-flex;align-items:center;gap:0.4rem;padding:0.28rem 1rem;border-radius:100px;border:1px solid;font-size:0.67rem;font-weight:800;letter-spacing:0.14em;text-transform:uppercase;margin-bottom:1rem;font-family:'IBM Plex Mono',monospace;}}
.rbadge.high{{background:{RED_LT};border-color:{RED_MD};color:{RED};}}.rbadge.low{{background:{GREEN_LT};border-color:{GREEN_MD};color:{GREEN};}}
.rpct{{font-size:4.5rem;font-weight:900;line-height:1;margin-bottom:0.35rem;letter-spacing:-0.03em;font-family:'Playfair Display',serif;}}
.rpct.high{{color:{RED};}}.rpct.low{{color:{GREEN};}}
.rdesc{{font-size:0.84rem;color:{TXT_S};margin-bottom:1.2rem;line-height:1.6;}}
.rconf{{display:inline-block;background:{CARD2};border:1px solid {BORDER2};border-radius:8px;padding:0.3rem 0.9rem;font-size:0.72rem;color:{TXT_S};font-family:'IBM Plex Mono',monospace;font-weight:500;}}
.tiles{{display:flex;flex-wrap:wrap;gap:0.65rem;margin-top:1.5rem;}}
.tile{{background:{CARD2};border:1px solid {BORDER};border-radius:12px;padding:0.8rem 1.1rem;min-width:82px;text-align:center;transition:transform .18s,border-color .18s;}}
.tile:hover{{transform:translateY(-2px);border-color:{BLUE};}}
.tv{{font-size:1.15rem;font-weight:700;color:{TXT};font-family:'Playfair Display',serif;}}.tl{{font-size:0.6rem;color:{TXT_M};text-transform:uppercase;letter-spacing:0.1em;margin-top:3px;font-weight:600;}}
.ftbl{{width:100%;border-collapse:collapse;font-size:0.83rem;margin-top:0.8rem;}}
.ftbl th{{background:{CARD2};color:{TXT_M};font-weight:700;text-transform:uppercase;letter-spacing:0.1em;font-size:0.65rem;padding:0.7rem 1rem;text-align:left;border-bottom:1.5px solid {BORDER};}}
.ftbl td{{padding:0.7rem 1rem;border-bottom:1px solid {BORDER};color:{TXT_S};}}
.ftbl tr:last-child td{{border-bottom:none;}}.ftbl tr:hover td{{background:{BLUE_LT};}}
.fval{{font-weight:700;color:{BLUE};font-family:'IBM Plex Mono',monospace;font-size:0.9rem;}}
.fmono{{font-family:'IBM Plex Mono',monospace;font-size:0.73rem;color:{TXT_M};}}
.disc{{background:{AMBER_LT};border:1px solid {DISC_BORD};border-radius:12px;padding:1rem 1.3rem;font-size:0.77rem;color:{DISC_TXT};line-height:1.65;margin-top:1.5rem;}}
.hitem{{background:{CARD2};border:1px solid {BORDER};border-radius:12px;padding:0.9rem 1.2rem;margin-bottom:0.6rem;display:flex;align-items:center;gap:1rem;transition:border-color .18s;}}
.hitem:hover{{border-color:{BLUE};}}
.hbadge{{padding:0.22rem 0.75rem;border-radius:100px;font-size:0.64rem;font-weight:800;letter-spacing:0.1em;text-transform:uppercase;flex-shrink:0;border:1px solid;font-family:'IBM Plex Mono',monospace;}}
.hbadge.high{{background:{RED_LT};color:{RED};border-color:{RED_MD};}}.hbadge.low{{background:{GREEN_LT};color:{GREEN};border-color:{GREEN_MD};}}
.hprob{{font-size:1.25rem;font-weight:700;color:{TXT};font-family:'Playfair Display',serif;}}.hmeta{{font-size:0.7rem;color:{TXT_M};margin-top:2px;}}
.stTabs [data-baseweb="tab-list"]{{background:transparent;gap:0;border-bottom:1.5px solid {BORDER};}}
.stTabs [data-baseweb="tab"]{{background:transparent;color:{TXT_M};border:none;font-family:'IBM Plex Sans',sans-serif;font-size:0.83rem;font-weight:600;padding:0.6rem 1.4rem;border-radius:8px 8px 0 0;transition:color .18s,background .18s;}}
.stTabs [aria-selected="true"]{{background:{BLUE_LT}!important;color:{BLUE}!important;border-bottom:2.5px solid {BLUE}!important;}}
.stTabs [data-baseweb="tab-panel"]{{padding-top:1.6rem!important;}}
.stDownloadButton > button{{background:{CARD2}!important;border:1.5px solid {BORDER2}!important;color:{TXT_S}!important;border-radius:10px!important;font-family:'IBM Plex Sans',sans-serif!important;font-weight:600!important;font-size:0.85rem!important;padding:0.7rem 1.4rem!important;width:100%!important;transition:all .18s!important;}}
.stDownloadButton > button:hover{{border-color:{BLUE}!important;color:{BLUE}!important;background:{BLUE_LT}!important;}}
hr{{border-color:{BORDER}!important;margin:1.2rem 0!important;}}
.stSpinner > div{{border-top-color:{BLUE}!important;}}
[data-testid="stMarkdownContainer"] p{{color:{TXT_S}!important;}}
/* Streamlit native chat styling overrides */
.stChatMessage{{background:{CARD2}!important;border:1px solid {BORDER}!important;border-radius:14px!important;}}
[data-testid="stChatMessageContent"] p{{color:{TXT_S}!important;font-size:0.9rem!important;}}
.stChatInputContainer{{background:{CARD}!important;border:1.5px solid {BORDER2}!important;border-radius:14px!important;}}
.stChatInputContainer textarea{{color:{TXT}!important;background:{INP}!important;font-family:'IBM Plex Sans',sans-serif!important;}}
</style>
""", unsafe_allow_html=True)


# ── NAV ───────────────────────────────────────────────────────────────────────
nc, tc = st.columns([6, 1])
with nc:
    st.markdown(f"""
    <div class="pcn-nav">
        <div class="pcn-nl">
            <div class="pcn-logo">PCN</div>
            <div>
                <div class="pcn-title">PCN Early Detection System</div>
                <div class="pcn-sub">Pancreatic Cancer &amp; Neurodegenerative Disorder · Medical AI</div>
            </div>
        </div>
        <div class="pcn-tags">
            <span class="ptag ptag-b">🔬 Risk Assessment</span>
            <span class="ptag ptag-t">⚡ ML v2.0</span>
            <span class="ptag ptag-m">Synthetic EHR</span>
            <span class="ptag ptag-m">Final Year Project</span>
        </div>
    </div>""", unsafe_allow_html=True)
with tc:
    st.markdown("<div style='height:0.55rem'></div>", unsafe_allow_html=True)
    if st.button("☀️ Light" if D else "🌙 Dark", use_container_width=True):
        st.session_state.dark_mode = not D
        st.rerun()

# ── STAT CARDS ────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="stat-row">
    <div class="scard bl"><div class="sc-icon">🧬</div><div class="sc-lbl">Clinical Features</div><div class="sc-val">18</div><div class="sc-sub">13 base · 5 engineered</div></div>
    <div class="scard te"><div class="sc-icon">🎯</div><div class="sc-lbl">Detection Targets</div><div class="sc-val">2-in-1</div><div class="sc-sub">Pancreatic + Neuro Disorder</div></div>
    <div class="scard am"><div class="sc-icon">📊</div><div class="sc-lbl">Risk Threshold</div><div class="sc-val">40%</div><div class="sc-sub">High-risk cutoff probability</div></div>
    <div class="scard sl"><div class="sc-icon">🔄</div><div class="sc-lbl">Assessments Run</div><div class="sc-val">{st.session_state.assessment_count}</div><div class="sc-sub">This session</div></div>
</div>""", unsafe_allow_html=True)

# ── API HEALTH ────────────────────────────────────────────────────────────────
@st.cache_data(ttl=20)
def api_health():
    try:
        r = requests.get(f"{API_URL}/health", timeout=3)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None

health  = api_health()
now_t   = datetime.datetime.now().strftime("%H:%M:%S")
rag_ok  = health.get("rag_ready", "") == "Ready" if health else False

if health:
    st.markdown(
        f'<div class="sbar ok"><div class="dot-p"></div>'
        f'<strong>API Online</strong> &nbsp;·&nbsp; '
        f'Model: <code>{health.get("model_loaded","—")}</code> &nbsp;·&nbsp; '
        f'Scaler: <code>{health.get("scaler_loaded","—")}</code> &nbsp;·&nbsp; '
        f'RAG: <code>{health.get("rag_ready","—")}</code> &nbsp;·&nbsp; '
        f'<span style="font-family:\'IBM Plex Mono\',monospace;font-size:0.75rem">{now_t}</span></div>',
        unsafe_allow_html=True)
else:
    st.markdown(
        f'<div class="sbar err"><div class="dot-p dot-e"></div>'
        f'<strong>API Offline</strong> &nbsp;·&nbsp; Run: <code>uvicorn api:app --reload</code></div>',
        unsafe_allow_html=True)

# ── FORM ──────────────────────────────────────────────────────────────────────
st.markdown('<div class="slbl">Patient Data Entry</div>', unsafe_allow_html=True)

with st.form("pcn_form"):
    st.markdown('<div class="fhead"><div class="fhd fhd-b">👤</div>Demographics &amp; Glycaemic Markers</div>', unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    with c1: age    = st.number_input("Age (years)",  1,   120,  50, 1)
    with c2: gender = st.selectbox("Gender",          ["Male","Female"])
    with c3: bmi    = st.number_input("BMI",          10.0, 60.0, 25.0, 0.1, format="%.1f")
    with c4: hba1c  = st.number_input("HbA1c Level",  3.0,  15.0, 5.5,  0.1, format="%.1f")
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="fhead"><div class="fhd fhd-t">🫀</div>Liver Enzymes &amp; Lipid Panel</div>', unsafe_allow_html=True)
    c5,c6,c7 = st.columns(3)
    with c5: ldl = st.number_input("LDL Cholesterol (mg/dL)", 30.0,  400.0, 120.0, 1.0, format="%.1f")
    with c6: ast = st.number_input("AST Level (U/L)",         5.0,   500.0, 25.0,  1.0, format="%.1f")
    with c7: alt = st.number_input("ALT Level (U/L)",         5.0,   500.0, 25.0,  1.0, format="%.1f")
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="fhead"><div class="fhd fhd-a">🧠</div>Genetic, Nutritional &amp; Neurological Indicators</div>', unsafe_allow_html=True)
    c8,c9,c10 = st.columns(3)
    with c8:  apoe     = st.selectbox("APOE-e4 Gene Present?",            ["No","Yes"])
    with c9:  fam_hist = st.selectbox("Family History (Neuro Disorders)?",["No","Yes"])
    with c10: b12      = st.number_input("Vitamin B12 (pg/mL)", 50.0, 2000.0, 400.0, 5.0, format="%.1f")
    c11,c12,c13 = st.columns(3)
    with c11: memory     = st.slider("Memory Score (1–10)",     1.0, 10.0, 7.0, 0.5)
    with c12: sleep      = st.slider("Sleep Hours / Night",     1.0, 12.0, 7.0, 0.5)
    with c13: depression = st.slider("Depression Score (0–10)", 0.0, 10.0, 2.0, 0.5)
    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
    submitted = st.form_submit_button("🔍  Run Risk Assessment", use_container_width=True)

# ── PDF ───────────────────────────────────────────────────────────────────────
def make_pdf(payload, result, eng):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT
    from reportlab.graphics.shapes import Drawing, Rect, String, Line
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
        leftMargin=2.2*cm, rightMargin=2.2*cm, topMargin=2.2*cm, bottomMargin=2.2*cm)
    CB=colors.HexColor("#1d4ed8"); CG=colors.HexColor("#15803d")
    CR=colors.HexColor("#b91c1c"); CS=colors.HexColor("#334155")
    CLG=colors.HexColor("#f1f5f9"); CMG=colors.HexColor("#e2e8f0")
    CDG=colors.HexColor("#64748b"); CW=colors.white
    is_high=result["risk_label"]=="High Risk"
    RC=CR if is_high else CG
    RC_BG=colors.HexColor("#fef2f2") if is_high else colors.HexColor("#f0fdf4")
    prob_pct=result["probability_percentage"]; conf=result["confidence"]
    lat=result["processing_time_ms"]; prob_raw=result["probability_raw"]
    label=result["risk_label"]
    base=getSampleStyleSheet()
    def PS(n,**kw): return ParagraphStyle(n, parent=base["Normal"], **kw)
    H2=PS("H2",fontName="Helvetica-Bold",fontSize=10.5,textColor=CB,spaceBefore=14,spaceAfter=5)
    BODY=PS("BODY",fontName="Helvetica",fontSize=9,textColor=CS,leading=14)
    MONO=PS("MONO",fontName="Courier",fontSize=8,textColor=CDG)
    CENT=PS("CENT",fontName="Helvetica",fontSize=9,textColor=CDG,alignment=TA_CENTER)
    RT=PS("RT",fontName="Helvetica",fontSize=8,textColor=CDG,alignment=TA_RIGHT)
    DISC=PS("DISC",fontName="Helvetica-Oblique",fontSize=7.5,textColor=colors.HexColor("#92400e"),leading=11.5)
    def HR(): return HRFlowable(width="100%",thickness=0.5,color=CMG,spaceAfter=6,spaceBefore=6)
    def SEC(t): return [Paragraph(t,H2),HR()]
    def TS():
        return TableStyle([("BACKGROUND",(0,0),(-1,0),CB),("TEXTCOLOR",(0,0),(-1,0),CW),
            ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,0),8),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[CW,CLG]),("GRID",(0,0),(-1,-1),0.3,CMG),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),("TOPPADDING",(0,0),(-1,-1),6),
            ("BOTTOMPADDING",(0,0),(-1,-1),6),("LEFTPADDING",(0,0),(-1,-1),9)])
    story=[]
    hdr=Table([[
        Paragraph('<font name="Helvetica-Bold" size="14" color="#1d4ed8">PCN</font>',base["Normal"]),
        Paragraph('<font name="Helvetica-Bold" size="17" color="#1e3a8a">PCN Early Detection System</font><br/>'                  '<font name="Helvetica" size="8.5" color="#64748b">Pancreatic Cancer &amp; Neurodegenerative Disorder · Clinical Assessment Report</font>',base["Normal"]),
        Paragraph(f'<font name="Helvetica" size="7.5" color="#94a3b8">'                  f'Date: {datetime.datetime.now().strftime("%d %b %Y")}<br/>'                  f'Time: {datetime.datetime.now().strftime("%H:%M:%S")}<br/>'                  f'Report ID: PCN-{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}</font>',RT),
    ]],colWidths=[1.8*cm,10*cm,4.5*cm])
    hdr.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE"),("LINEBELOW",(0,0),(-1,0),1.5,CB),
        ("BACKGROUND",(0,0),(0,0),colors.HexColor("#eef2ff")),("PADDING",(0,0),(-1,-1),7),("ALIGN",(0,0),(0,0),"CENTER")]))
    story+=[hdr,Spacer(1,12)]
    col_hex="#b91c1c" if is_high else "#15803d"
    icon_txt="⚠  HIGH RISK" if is_high else "✓  LOW RISK"
    rbox=Table([[
        Paragraph(f'<font name="Helvetica-Bold" size="10.5" color="{col_hex}">{icon_txt}</font>',CENT),
        Paragraph(f'<font name="Helvetica-Bold" size="30" color="{col_hex}">{prob_pct}</font><br/>'                  f'<font name="Helvetica" size="8.5" color="#64748b">Combined PCN risk probability</font>',PS("PB",alignment=TA_CENTER)),
        Paragraph(f'<font name="Helvetica-Bold" size="7.5" color="#334155">CONFIDENCE</font><br/>'                  f'<font name="Courier-Bold" size="9.5" color="#1d4ed8">{conf}</font><br/><br/>'                  f'<font name="Helvetica-Bold" size="7.5" color="#334155">THRESHOLD</font><br/>'                  f'<font name="Courier-Bold" size="9.5" color="#b45309">40%</font><br/><br/>'                  f'<font name="Helvetica-Bold" size="7.5" color="#334155">LATENCY</font><br/>'                  f'<font name="Courier-Bold" size="9.5" color="#64748b">{lat} ms</font>',PS("STK",alignment=TA_CENTER)),
    ]],colWidths=[4.5*cm,6.5*cm,4.5*cm])
    rbox.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),RC_BG),("BOX",(0,0),(-1,-1),1.8,RC),
        ("LINEAFTER",(0,0),(1,0),0.5,CMG),("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("TOPPADDING",(0,0),(-1,-1),14),("BOTTOMPADDING",(0,0),(-1,-1),14),
        ("LEFTPADDING",(0,0),(-1,-1),14),("RIGHTPADDING",(0,0),(-1,-1),14)]))
    story+=[rbox,Spacer(1,14)]
    story+=SEC("📋  Patient Input Parameters")
    pdata=[[Paragraph('<font color="white"><b>Parameter</b></font>',MONO),Paragraph('<font color="white"><b>Value</b></font>',MONO),
            Paragraph('<font color="white"><b>Parameter</b></font>',MONO),Paragraph('<font color="white"><b>Value</b></font>',MONO)],
           ["Age",f"{payload['age']} years","Gender",payload["gender"]],
           ["BMI",f"{payload['bmi']:.1f}","HbA1c",f"{payload['hba1c']:.1f}"],
           ["LDL Cholesterol",f"{payload['ldl']:.1f} mg/dL","AST",f"{payload['ast']:.1f} U/L"],
           ["ALT",f"{payload['alt']:.1f} U/L","Vitamin B12",f"{payload['vitamin_b12']:.1f} pg/mL"],
           ["Memory Score",str(payload["memory_score"]),"Sleep Hours",str(payload["sleep_hours"])],
           ["Depression Score",str(payload["depression_score"]),"APOE-e4 Gene",payload["apoe_e4"]],
           ["Family History (Neuro)",payload["family_history_neuro"],"",""]]
    pt=Table(pdata,colWidths=[4.2*cm,3.5*cm,4.2*cm,3.5*cm],repeatRows=1); pt.setStyle(TS()); story+=[pt,Spacer(1,14)]
    story+=SEC("⚗️  Engineered Biomarker Features")
    edata=[[Paragraph('<font color="white"><b>Feature</b></font>',MONO),Paragraph('<font color="white"><b>Formula</b></font>',MONO),Paragraph('<font color="white"><b>Value</b></font>',MONO)],
           ["Metabolic Index","(BMI x HbA1c) / 10",str(eng["metabolic_index"])],
           ["Liver Stress Score","AST + ALT",str(eng["liver_stress_score"])],
           ["Neuro-Genetic Risk","(Age x APOE) + (FamHist x 10)",str(eng["neuro_genetic_risk"])],
           ["Vascular / B12","LDL / (Vitamin B12 + 1)",str(eng["vascular_b12_ratio"])],
           ["Mental Health Index","Memory - (Depression x 0.7)",str(eng["mental_health_index"])]]
    et=Table(edata,colWidths=[5*cm,7.2*cm,3.2*cm],repeatRows=1); et.setStyle(TS()); story+=[et,Spacer(1,14)]
    story+=SEC("📊  Engineered Feature Visual")
    v2=[eng["metabolic_index"],eng["liver_stress_score"],eng["neuro_genetic_risk"],eng["vascular_b12_ratio"],eng["mental_health_index"]]
    lbls=["Metabolic","Liver Stress","Neuro-Genetic","Vascular/B12","Mental Health"]
    bcols=["#1d4ed8","#0f766e","#7c3aed","#b45309","#db2777"]; mv=max(v2) if max(v2)>0 else 1
    d=Drawing(430,130)
    for i,(lb,v,bc) in enumerate(zip(lbls,v2,bcols)):
        bx=35+i*76; bh=max(3,int((v/mv)*78))
        d.add(Rect(bx,28,50,bh,fillColor=colors.HexColor(bc),strokeColor=None))
        d.add(String(bx+25,28+bh+4,f"{v:.2f}",fontSize=7,textAnchor="middle",fontName="Helvetica-Bold",fillColor=colors.HexColor("#334155")))
        d.add(String(bx+25,8,lb,fontSize=6.5,textAnchor="middle",fontName="Helvetica",fillColor=colors.HexColor("#64748b")))
    d.add(Line(30,28,415,28,strokeColor=CMG,strokeWidth=0.5)); story+=[d,Spacer(1,12)]
    pct_i=int(prob_raw*100); fb="="*int(pct_i/5)+"-"*(20-int(pct_i/5))
    story+=SEC("Risk Probability Gauge")
    story.append(Paragraph(f'<font name="Courier-Bold" size="10" color="{col_hex}">[{fb}] {pct_i}%</font>',base["Normal"]))
    story.append(Spacer(1,14))
    story+=SEC("🩺  Clinical Interpretation")
    txt=(f"The patient demonstrates a <b>HIGH RISK</b> probability of {prob_pct} exceeding the 40% threshold. "         "Immediate specialist referral with imaging (CT/MRI), tumor markers (CA 19-9), and neurological evaluation is strongly advised."
         if is_high else
         f"The patient demonstrates a <b>LOW RISK</b> probability of {prob_pct}, below the 40% threshold. "         "Standard follow-up per clinical guidelines recommended.")
    story+=[Paragraph(txt,BODY),Spacer(1,14)]
    story+=SEC("⚠️  Disclaimer")
    dbox=Table([[Paragraph("<b>IMPORTANT:</b> This report is generated by an AI model trained on synthetic EHR for research/decision-support only. "        "Results must be reviewed by a licensed oncologist or neurologist.",DISC)]],colWidths=[15.1*cm])
    dbox.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#fffbeb")),
        ("BOX",(0,0),(-1,-1),1,colors.HexColor("#fde68a")),("PADDING",(0,0),(-1,-1),10)]))
    story+=[dbox,Spacer(1,12)]
    foot=Table([[Paragraph(
        f'<font name="Helvetica" size="7" color="#94a3b8">PCN Early Detection System · Final Year Project · GCUF · ML v2.0 · XGBoost · FastAPI · Streamlit<br/>'        f'Generated: {datetime.datetime.now().strftime("%d %B %Y at %H:%M:%S")} · Report ID: PCN-{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}</font>',
        PS("FT",alignment=TA_CENTER))]],colWidths=[15.1*cm])
    foot.setStyle(TableStyle([("LINEABOVE",(0,0),(-1,0),0.5,CMG),("TOPPADDING",(0,0),(-1,-1),8)]))
    story.append(foot); doc.build(story); buf.seek(0); return buf.getvalue()


# ── PREDICTION ────────────────────────────────────────────────────────────────
if submitted:
    payload={"age":age,"gender":gender,"bmi":bmi,"hba1c":hba1c,"ldl":ldl,"ast":ast,"alt":alt,
             "apoe_e4":apoe,"memory_score":memory,"sleep_hours":sleep,"vitamin_b12":b12,
             "depression_score":depression,"family_history_neuro":fam_hist}
    with st.spinner("Analysing biomarkers…"):
        time.sleep(0.5)
        try:
            resp  = requests.post(f"{API_URL}/predict", json=payload, timeout=10)
            result= resp.json()
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to API. Run: `uvicorn api:app --reload`"); st.stop()
        except Exception as ex:
            st.error(f"Unexpected error: {ex}"); st.stop()
    if result.get("status") != "success":
        st.error(f"API error: {result.get('detail','Unknown')}"); st.stop()

    st.session_state.assessment_count += 1
    st.session_state.history.insert(0,{"time":datetime.datetime.now().strftime("%H:%M:%S"),
        "label":result["risk_label"],"pct":result["probability_percentage"],"age":age,"bmi":bmi})
    if len(st.session_state.history)>8: st.session_state.history=st.session_state.history[:8]

    prob_raw=result["probability_raw"]; prob_pct=result["probability_percentage"]
    label=result["risk_label"]; confidence=result["confidence"]
    eng=result["engineered_features"]; latency=result["processing_time_ms"]
    is_high=(label=="High Risk"); cls="high" if is_high else "low"
    icon="⚠" if is_high else "✓"; gauge_col=RED if is_high else GREEN

    tab1,tab2,tab3,tab4 = st.tabs([
        "  📊  Result Overview  ",
        "  🧬  Feature Analysis  ",
        "  📈  Biomarker Charts  ",
        "  📋  Clinical Report  ",
    ])

    with tab1:
        L,R=st.columns([1.2,1],gap="large")
        with L:
            desc=("Patient exceeds the 40% risk threshold. Immediate specialist referral and diagnostic workup strongly recommended."
                  if is_high else "Risk is within acceptable range. Routine monitoring per clinical guidelines is advised.")
            st.markdown(f"""
            <div class="rcard {cls}">
                <div class="rbadge {cls}">{icon} &nbsp;{label}</div>
                <div class="rpct {cls}">{prob_pct}</div>
                <div class="rdesc">{desc}</div>
                <div class="rconf">Confidence &nbsp;·&nbsp; {confidence} &nbsp;·&nbsp; Latency: {latency} ms</div>
            </div>
            <div class="tiles">
                <div class="tile"><div class="tv">{age}</div><div class="tl">Age</div></div>
                <div class="tile"><div class="tv">{gender[0]}</div><div class="tl">Gender</div></div>
                <div class="tile"><div class="tv">{bmi:.1f}</div><div class="tl">BMI</div></div>
                <div class="tile"><div class="tv">{hba1c:.1f}</div><div class="tl">HbA1c</div></div>
                <div class="tile"><div class="tv">{apoe}</div><div class="tl">APOE-e4</div></div>
                <div class="tile"><div class="tv">{fam_hist}</div><div class="tl">Fam Hx</div></div>
                <div class="tile"><div class="tv">{memory}</div><div class="tl">Memory</div></div>
                <div class="tile"><div class="tv">{sleep}h</div><div class="tl">Sleep</div></div>
            </div>""", unsafe_allow_html=True)
        with R:
            gauge=go.Figure(go.Indicator(mode="gauge+number+delta",value=round(prob_raw*100,1),
                delta={"reference":40,"valueformat":".1f","suffix":"%","font":{"size":12,"color":TICK}},
                number={"suffix":"%","font":{"size":34,"color":gauge_col,"family":"IBM Plex Mono"}},
                gauge={"axis":{"range":[0,100],"tickcolor":TICK,"tickfont":{"color":TICK,"size":9},"tickwidth":1,"dtick":20},
                       "bar":{"color":gauge_col,"thickness":0.2},"bgcolor":GAUGE_BG,"borderwidth":0,
                       "steps":[{"range":[0,40],"color":"#f0fdf4" if not D else "rgba(74,222,128,0.06)"},
                                {"range":[40,65],"color":"#fffbeb" if not D else "rgba(251,191,36,0.06)"},
                                {"range":[65,100],"color":"#fef2f2" if not D else "rgba(248,113,113,0.08)"}],
                       "threshold":{"line":{"color":"#f59e0b","width":2.5},"thickness":0.72,"value":40}},
                title={"text":"PCN Risk Score","font":{"color":TICK,"size":12,"family":"IBM Plex Sans"}}))
            gauge.update_layout(paper_bgcolor=PLY_PAPER,plot_bgcolor=PLY_BG,height=280,margin=dict(l=20,r=20,t=60,b=10),font_color=TXT)
            st.plotly_chart(gauge,use_container_width=True)
        st.markdown(f'<div class="disc"><strong>⚠ Clinical Disclaimer:</strong> This tool provides decision support based on synthetic EHR-trained models. Results must be reviewed by a licensed oncologist or neurologist.</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="slbl">Engineered Biomarker Features</div>', unsafe_allow_html=True)
        cats=["Metabolic Index","Liver Stress","Neuro-Genetic Risk","Vascular / B12","Mental Health"]
        vals=[eng["metabolic_index"],eng["liver_stress_score"],eng["neuro_genetic_risk"],eng["vascular_b12_ratio"],eng["mental_health_index"]]
        col_r,col_t=st.columns([1.1,1],gap="large")
        with col_r:
            radar=go.Figure(); radar.add_trace(go.Scatterpolar(r=vals+[vals[0]],theta=cats+[cats[0]],fill="toself",
                line=dict(color=BLUE,width=2.5),fillcolor=f"rgba({'79,142,247' if D else '29,78,216'},0.12)",marker=dict(size=7,color=BLUE)))
            radar.update_layout(polar=dict(bgcolor=PLY_BG,
                radialaxis=dict(visible=True,color=TICK,gridcolor=GRID,tickfont=dict(color=TICK,size=8),linecolor=GRID),
                angularaxis=dict(color=TXT_S,gridcolor=GRID,tickfont=dict(color=TXT_S,size=10.5))),
                paper_bgcolor=PLY_PAPER,height=340,margin=dict(l=55,r=55,t=30,b=30),showlegend=False)
            st.plotly_chart(radar,use_container_width=True)
        with col_t:
            rows=[("Metabolic Index","(BMI x HbA1c) / 10",eng["metabolic_index"]),
                  ("Liver Stress Score","AST + ALT",eng["liver_stress_score"]),
                  ("Neuro-Genetic Risk","(Age x APOE) + (FamHist x 10)",eng["neuro_genetic_risk"]),
                  ("Vascular / B12","LDL / (Vitamin B12 + 1)",eng["vascular_b12_ratio"]),
                  ("Mental Health Index","Memory - (Depression x 0.7)",eng["mental_health_index"])]
            h='<table class="ftbl"><thead><tr><th>Feature</th><th>Formula</th><th>Value</th></tr></thead><tbody>'
            for nm,formula,val in rows: h+=f'<tr><td><strong>{nm}</strong></td><td class="fmono">{formula}</td><td class="fval">{val}</td></tr>'
            st.markdown(h+"</tbody></table>",unsafe_allow_html=True)

    with tab3:
        eng_names=["Metabolic Index","Liver Stress","Neuro-Genetic","Vascular/B12","Mental Health"]
        eng_vals=[eng["metabolic_index"],eng["liver_stress_score"],eng["neuro_genetic_risk"],eng["vascular_b12_ratio"],eng["mental_health_index"]]
        eng_colors=["#1d4ed8","#0f766e","#7c3aed","#b45309","#db2777"]
        cb,cp=st.columns([1.3,1],gap="large")
        with cb:
            st.markdown('<div class="slbl">Engineered Feature Values</div>', unsafe_allow_html=True)
            fb=go.Figure(go.Bar(x=eng_names,y=eng_vals,marker=dict(color=eng_colors,opacity=0.88,line=dict(width=0)),
                text=[f"{v:.2f}" for v in eng_vals],textposition="outside",textfont=dict(color=TICK,size=10.5,family="IBM Plex Mono")))
            fb.update_layout(paper_bgcolor=PLY_PAPER,plot_bgcolor=PLY_BG,height=290,margin=dict(l=10,r=10,t=20,b=30),
                font=dict(color=TICK,family="IBM Plex Sans"),
                xaxis=dict(gridcolor=GRID,zeroline=False,linecolor=GRID,tickfont=dict(color=TXT_S,size=10)),
                yaxis=dict(gridcolor=GRID,zeroline=False,linecolor=GRID,tickfont=dict(color=TICK)),bargap=0.38)
            st.plotly_chart(fb,use_container_width=True)
        with cp:
            st.markdown('<div class="slbl">Risk Distribution</div>', unsafe_allow_html=True)
            pct_val=round(prob_raw*100,1)
            fp=go.Figure(go.Pie(labels=["Risk","Safe Margin"],values=[pct_val,round(100-pct_val,1)],hole=0.66,
                marker=dict(colors=[gauge_col,BORDER],line=dict(color=PLY_BG,width=2.5)),textfont=dict(family="IBM Plex Sans",size=11)))
            fp.add_annotation(text=f"<b>{pct_val}%</b>",x=0.5,y=0.5,font=dict(size=24,family="IBM Plex Mono",color=gauge_col),showarrow=False)
            fp.update_layout(paper_bgcolor=PLY_PAPER,height=290,margin=dict(l=10,r=10,t=20,b=10),
                legend=dict(font=dict(color=TXT_S,family="IBM Plex Sans",size=11),bgcolor=PLY_BG,bordercolor=GRID,borderwidth=1))
            st.plotly_chart(fp,use_container_width=True)
        st.markdown('<div class="slbl">Raw Biomarker Values</div>', unsafe_allow_html=True)
        raw_n=["Age","BMI","HbA1c","LDL","AST","ALT","B12","Memory","Sleep","Depression"]
        raw_v=[age,bmi,hba1c,ldl,ast,alt,b12,memory,sleep,depression]
        fr=go.Figure(go.Bar(x=raw_n,y=raw_v,marker=dict(color=BLUE,opacity=0.80,line=dict(width=0)),
            text=[f"{v:.1f}" for v in raw_v],textposition="outside",textfont=dict(color=TICK,size=10,family="IBM Plex Mono")))
        fr.update_layout(paper_bgcolor=PLY_PAPER,plot_bgcolor=PLY_BG,height=270,margin=dict(l=10,r=10,t=16,b=30),
            font=dict(color=TICK,family="IBM Plex Sans"),
            xaxis=dict(gridcolor=GRID,zeroline=False,linecolor=GRID,tickfont=dict(color=TXT_S,size=11)),
            yaxis=dict(gridcolor=GRID,zeroline=False,linecolor=GRID,tickfont=dict(color=TICK)),bargap=0.36)
        st.plotly_chart(fr,use_container_width=True)

    with tab4:
        st.markdown('<div class="slbl">Clinical Assessment Report</div>', unsafe_allow_html=True)
        rmd=(f"# PCN Early Detection — Clinical Report\n**Generated:** {datetime.datetime.now().strftime('%d %B %Y at %H:%M:%S')}\n\n---\n"
             f"## Assessment Summary\n| Field | Value |\n|---|---|\n| **Risk Label** | {label} |\n| **Probability** | {prob_pct} |\n"
             f"| **Confidence** | {confidence} |\n| **Threshold** | 40% |\n| **Processing Time** | {latency} ms |\n\n---\n"
             f"## Patient Input\n| Parameter | Value |\n|---|---|\n| Age | {age} years |\n| Gender | {gender} |\n"
             f"| BMI | {bmi:.1f} |\n| HbA1c | {hba1c:.1f} |\n| LDL | {ldl:.1f} mg/dL |\n| AST | {ast:.1f} U/L |\n"
             f"| ALT | {alt:.1f} U/L |\n| Vitamin B12 | {b12:.1f} pg/mL |\n| Memory | {memory} |\n| Sleep | {sleep} hrs |\n"
             f"| Depression | {depression} |\n| APOE-e4 | {apoe} |\n| Family History | {fam_hist} |\n\n---\n"
             f"> **Disclaimer:** AI model on synthetic EHR. Must be reviewed by a licensed clinician.\n")
        st.markdown(rmd)
        st.markdown("<br>", unsafe_allow_html=True)
        d1,d2=st.columns(2,gap="medium")
        with d1:
            st.download_button("⬇  Download (.md)",data=rmd,
                file_name=f"pcn_{age}_{label.replace(' ','_').lower()}.md",mime="text/markdown",use_container_width=True)
        with d2:
            try:
                pdf_data=make_pdf(payload,result,eng)
                st.download_button("⬇  Download PDF Report",data=pdf_data,
                    file_name=f"pcn_{age}_{label.replace(' ','_').lower()}.pdf",mime="application/pdf",use_container_width=True)
            except Exception as e:
                st.error(f"PDF error: {e}")

# ── HISTORY ───────────────────────────────────────────────────────────────────
if st.session_state.history:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="slbl">Session Assessment History</div>', unsafe_allow_html=True)
    hh=""
    for i,h in enumerate(st.session_state.history):
        c="high" if h["label"]=="High Risk" else "low"; ic="⚠" if c=="high" else "✓"
        hh+=(f'<div class="hitem"><span style="font-family:\'IBM Plex Mono\',monospace;font-size:0.7rem;color:{TXT_M};min-width:55px">#{i+1} {h["time"]}</span>'             f'<div class="hbadge {c}">{ic} {h["label"]}</div>'             f'<div><div class="hprob">{h["pct"]}</div><div class="hmeta">Age {h["age"]} · BMI {h["bmi"]:.1f}</div></div></div>')
    st.markdown(hh, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ── PCN-AI CHATBOT  (outside prediction block — always visible) ───────────────
# ── Uses st.chat_input + st.chat_message to PREVENT page reset issue ─────────
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="slbl">🤖 PCN-AI Medical Chatbot</div>', unsafe_allow_html=True)

chat_col, info_col = st.columns([1.9, 1], gap="large")

with chat_col:
    # Status header
    if rag_ok:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,{BLUE} 0%,#4f46e5 100%);
            border-radius:14px 14px 0 0;padding:0.9rem 1.3rem;
            display:flex;align-items:center;gap:0.85rem;">
            <div style="width:40px;height:40px;border-radius:50%;background:rgba(255,255,255,0.18);
                display:flex;align-items:center;justify-content:center;font-size:1.3rem">🧬</div>
            <div>
                <div style="font-weight:700;font-size:0.95rem;color:#fff">PCN-AI Medical Assistant</div>
                <div style="font-size:0.71rem;color:rgba(255,255,255,0.72);display:flex;align-items:center;gap:5px;margin-top:2px">
                    <span style="width:7px;height:7px;border-radius:50%;background:#4ade80;display:inline-block;box-shadow:0 0 0 2px rgba(74,222,128,0.3)"></span>
                    Online · RAG + Groq Llama3 · 17 knowledge chunks
                </div>
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background:{CARD};border:1px solid {BORDER};border-radius:14px 14px 0 0;
            padding:0.9rem 1.3rem;display:flex;align-items:center;gap:0.85rem;">
            <div style="font-size:1.3rem">🧬</div>
            <div>
                <div style="font-weight:700;font-size:0.95rem;color:{TXT}">PCN-AI Medical Assistant</div>
                <div style="font-size:0.71rem;color:{RED};margin-top:2px">
                    ⚠ Offline — Set GROQ_API_KEY in .env then restart server
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    # Chat container
    with st.container():
        # Welcome message (shown once, not stored in history)
        if not st.session_state.chat_messages:
            with st.chat_message("assistant", avatar="🧬"):
                st.markdown(
                    "**Salam! PCN-AI mein khush aamdeed!** 👋\n\n"
                    "Main Pancreatic Cancer aur Neurodegenerative Disorders ka "
                    "medical assistant hoon.\n\n"
                    "Mujhse pooch saktay hain:\n"
                    "• Risk factors aur symptoms\n"
                    "• PCN model kaise kaam karta hai\n"
                    "• Biomarker normal ranges\n"
                    "• Prevention strategies\n\n"
                    + ("**Ready!** Apna sawal likhein 👇"
                       if rag_ok else
                       "⚠️ **Bot offline** — `.env` mein `GROQ_API_KEY` set karein.")
                )

        # Render existing messages from session state
        for msg in st.session_state.chat_messages:
            avatar = "🧬" if msg["role"] == "assistant" else "👤"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])
                # Show source pills under assistant messages
                if msg["role"] == "assistant" and msg.get("sources"):
                    pills = " &nbsp; ".join(
                        f'<span style="background:{BLUE_LT};border:1px solid {BLUE_MD};'
                        f'color:{BLUE};border-radius:100px;font-size:0.63rem;'
                        f'font-weight:600;padding:1px 9px;">📄 {s["topic"][:28]}</span>'
                        for s in msg["sources"][:3]
                    )
                    st.markdown(pills, unsafe_allow_html=True)

    # ── PROCESS pending message (from PREVIOUS run) ───────────────────────────
    # This is the key fix: process message BEFORE rendering chat_input
    # so the answer is stored before the next rerun
    if st.session_state.pending_msg and rag_ok:
        q = st.session_state.pending_msg
        st.session_state.pending_msg = None   # clear immediately

        # Build history list for context — safe pair extraction
        history_for_engine = []
        msgs = st.session_state.chat_messages
        i = 0
        while i < len(msgs) - 1:
            if msgs[i]["role"] == "user" and msgs[i+1]["role"] == "assistant":
                history_for_engine.append({
                    "user":      msgs[i]["content"],
                    "assistant": msgs[i+1]["content"],
                })
                i += 2
            else:
                i += 1

        with st.spinner("PCN-AI jawab de raha hai…"):
            try:
                resp = requests.post(
                    f"{API_URL}/chat",
                    json={"message": q, "history": history_for_engine},
                    timeout=30,
                )
                data   = resp.json()
                answer = data.get("answer", "⚠️ No answer received.")
                sources= data.get("sources", [])
            except Exception as ex:
                answer  = f"⚠️ Error: {ex}"
                sources = []

        st.session_state.chat_messages.append({
            "role":    "assistant",
            "content": answer,
            "sources": sources,
        })
        st.rerun()

    # ── st.chat_input — CORRECT way in Streamlit, no page reset ──────────────
    user_input = st.chat_input(
        placeholder="Koi bhi medical sawal poochein…",
        disabled=not rag_ok,
        key="pcn_chat_input",
    )

    if user_input and user_input.strip():
        # Store user message in session state
        st.session_state.chat_messages.append({
            "role":    "user",
            "content": user_input.strip(),
            "sources": [],
        })
        # Store as pending — will be processed on next run (above)
        st.session_state.pending_msg = user_input.strip()
        st.rerun()

    # Clear button
    if st.session_state.chat_messages:
        if st.button("🗑 Clear Chat", key="clr_chat_btn", use_container_width=True):
            st.session_state.chat_messages = []
            st.session_state.pending_msg   = None
            st.rerun()

with info_col:
    # Bot status
    status_c = GREEN if rag_ok else RED
    status_t = "Active · RAG Ready" if rag_ok else "Offline"
    st.markdown(f"""
    <div style="background:{CARD2};border:1px solid {BORDER};border-radius:14px;padding:1rem 1.2rem;margin-bottom:0.8rem">
        <div style="font-size:0.67rem;font-weight:700;text-transform:uppercase;letter-spacing:0.13em;color:{TXT_M};margin-bottom:0.6rem">🤖 Bot Status</div>
        <div style="display:flex;align-items:center;gap:0.55rem">
            <div style="width:9px;height:9px;border-radius:50%;background:{status_c}"></div>
            <div style="font-weight:700;font-size:0.88rem;color:{status_c}">{status_t}</div>
        </div>
        <div style="font-size:0.73rem;color:{TXT_M};margin-top:0.35rem">Key loaded from .env · No frontend exposure</div>
    </div>""", unsafe_allow_html=True)

    # Knowledge base
    st.markdown(f"""
    <div style="background:{CARD2};border:1px solid {BORDER};border-radius:14px;padding:1rem 1.2rem">
        <div style="font-size:0.67rem;font-weight:700;text-transform:uppercase;letter-spacing:0.13em;color:{TXT_M};margin-bottom:0.75rem">📚 Knowledge Base</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;margin-bottom:0.8rem">
            <div style="background:{CARD};border:1px solid {BORDER};border-radius:10px;padding:0.55rem;text-align:center">
                <div style="font-size:1.35rem;font-weight:700;color:{BLUE};font-family:'Playfair Display',serif">17</div>
                <div style="font-size:0.6rem;color:{TXT_M};text-transform:uppercase;letter-spacing:0.08em;font-weight:600;margin-top:2px">Chunks</div>
            </div>
            <div style="background:{CARD};border:1px solid {BORDER};border-radius:10px;padding:0.55rem;text-align:center">
                <div style="font-size:1.35rem;font-weight:700;color:{GREEN};font-family:'Playfair Display',serif">6</div>
                <div style="font-size:0.6rem;color:{TXT_M};text-transform:uppercase;letter-spacing:0.08em;font-weight:600;margin-top:2px">Topics</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    for ico, topic, cnt, clr in [("🦠","Pancreatic Cancer","6",RED),("🧠","Neuro Disorders","5",PURPLE),
                                   ("⚗️","PCN ML Model","4",BLUE),("🥗","Prevention","2",GREEN)]:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:0.55rem;padding:0.38rem 0;border-bottom:1px solid {BORDER};">
            <span>{ico}</span>
            <div style="flex:1"><div style="font-size:0.78rem;font-weight:600;color:{TXT}">{topic}</div>
            <div style="font-size:0.67rem;color:{TXT_M}">{cnt} chunks</div></div>
            <div style="width:7px;height:7px;border-radius:50%;background:{clr}"></div>
        </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Sample questions
    st.markdown(f"""
    <div style="background:{CARD2};border:1px solid {BORDER};border-radius:14px;padding:1rem 1.2rem;margin-top:0.8rem">
        <div style="font-size:0.67rem;font-weight:700;text-transform:uppercase;letter-spacing:0.13em;color:{TXT_M};margin-bottom:0.6rem">💡 Try These</div>
    """, unsafe_allow_html=True)
    for sq in ["APOE-e4 gene kya hota hai?","Pancreatic cancer symptoms?",
               "Vitamin B12 normal range?","Metabolic Index formula?",
               "SMOTE kya hota hai?","89.36% ROC-AUC ka matlab?"]:
        st.markdown(f'<div style="font-size:0.77rem;color:{TXT_S};padding:0.3rem 0;border-bottom:1px solid {BORDER};">❓ {sq}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Setup guide if offline
    if not rag_ok:
        st.markdown(f"""
        <div style="background:{AMBER_LT};border:1px solid {DISC_BORD};border-radius:12px;
            padding:0.9rem 1.1rem;margin-top:0.8rem;font-size:0.78rem;color:{DISC_TXT};line-height:1.75">
            <b>🔑 Activate Guide:</b><br>
            1. <b>console.groq.com</b> → Free signup<br>
            2. API Keys → Create New Key<br>
            3. Open <code>.env</code> in project folder<br>
            4. Set: <code>GROQ_API_KEY=gsk_...</code><br>
            5. Restart: <code>streamlit run app.py</code>
        </div>""", unsafe_allow_html=True)


# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(f"""
<div style="text-align:center;color:{TXT_M};font-size:0.7rem;font-family:'IBM Plex Sans',sans-serif;
    letter-spacing:0.05em;border-top:1px solid {BORDER};padding-top:1.5rem;line-height:2.2;">
    PCN Early Detection System &nbsp;·&nbsp; Pancreatic Cancer &amp; Neurodegenerative Disorder &nbsp;·&nbsp; GCUF · Final Year Project<br>
    FastAPI &nbsp;·&nbsp; XGBoost &nbsp;·&nbsp; Streamlit &nbsp;·&nbsp; Plotly &nbsp;·&nbsp;
    ReportLab &nbsp;·&nbsp; Groq RAG &nbsp;·&nbsp; {datetime.datetime.now().year}
</div>""", unsafe_allow_html=True)