# """
# ╔══════════════════════════════════════════════════════════════════╗
# ║  PCN CHATBOT TAB — Paste this into your existing app.py         ║
# ║  Add "📱 PCN-AI Chatbot" as a new tab in your tabs section      ║
# ╚══════════════════════════════════════════════════════════════════╝

# STEP 1: Add these imports at the TOP of your app.py
# STEP 2: Add chatbot session states
# STEP 3: Add the tab content below
# STEP 4: Add sidebar API key input

# Full integration guide at bottom of this file.
# """

# # ════════════════════════════════════════════════════════════════════
# # STEP 1 ── ADD THESE IMPORTS at top of app.py (after existing ones)
# # ════════════════════════════════════════════════════════════════════
# IMPORTS_TO_ADD = """
# import sys, os
# sys.path.insert(0, os.path.dirname(__file__))

# try:
#     from rag.rag_engine import get_rag_engine, SimpleFallbackRAG
#     from rag.knowledge_base import get_topics
#     RAG_AVAILABLE = True
# except ImportError:
#     RAG_AVAILABLE = False
# """

# # ════════════════════════════════════════════════════════════════════
# # STEP 2 ── ADD THESE SESSION STATES (after existing session states)
# # ════════════════════════════════════════════════════════════════════
# SESSION_STATES_TO_ADD = """
# if "chat_history"  not in st.session_state: st.session_state.chat_history  = []
# if "rag_engine"    not in st.session_state: st.session_state.rag_engine    = None
# if "rag_ready"     not in st.session_state: st.session_state.rag_ready     = False
# if "groq_api_key"  not in st.session_state: st.session_state.groq_api_key  = ""
# """

# # ════════════════════════════════════════════════════════════════════
# # STEP 3 ── CHATBOT CSS (add inside your existing <style> block)
# # ════════════════════════════════════════════════════════════════════
# # Add this CSS string into your existing st.markdown(f"""<style>...""")
# CHATBOT_CSS = """
# /* ─── CHATBOT ──────────────────────────────────────────────────── */
# .chat-wrap {{
#     background:{CARD}; border:1px solid {BORDER};
#     border-radius:16px; padding:0;
#     box-shadow:{SHADOW}; overflow:hidden;
#     margin-bottom:1rem;
# }}
# .chat-header {{
#     background:linear-gradient(135deg,{BLUE} 0%,#4f46e5 100%);
#     padding:1rem 1.4rem; display:flex; align-items:center; gap:0.8rem;
# }}
# .chat-avatar {{
#     width:40px; height:40px; border-radius:50%;
#     background:rgba(255,255,255,0.2);
#     display:flex; align-items:center; justify-content:center;
#     font-size:1.2rem; flex-shrink:0;
# }}
# .chat-hname  {{ font-weight:700; font-size:1rem; color:#fff; }}
# .chat-hstatus {{ font-size:0.72rem; color:rgba(255,255,255,0.7); }}
# .chat-status-dot {{
#     width:8px; height:8px; border-radius:50%; background:#4ade80;
#     display:inline-block; margin-right:4px;
#     box-shadow:0 0 0 3px rgba(74,222,128,0.25);
#     animation:dp 2s infinite;
# }}
# .chat-body {{
#     padding:1rem 1.2rem; max-height:460px; overflow-y:auto;
#     display:flex; flex-direction:column; gap:0.85rem;
#     scroll-behavior:smooth;
# }}
# .chat-body::-webkit-scrollbar {{ width:4px; }}
# .chat-body::-webkit-scrollbar-track {{ background:transparent; }}
# .chat-body::-webkit-scrollbar-thumb {{ background:{BORDER2}; border-radius:4px; }}

# .msg-row {{ display:flex; gap:0.6rem; align-items:flex-end; }}
# .msg-row.user {{ flex-direction:row-reverse; }}
# .msg-av {{
#     width:30px; height:30px; border-radius:50%; flex-shrink:0;
#     display:flex; align-items:center; justify-content:center;
#     font-size:0.85rem;
# }}
# .msg-av.ai  {{ background:{BLUE_LT}; }}
# .msg-av.usr {{ background:{BLUE}; }}

# .msg-bubble {{
#     max-width:78%; padding:0.75rem 1rem;
#     border-radius:16px; font-size:0.88rem; line-height:1.6;
#     font-family:'IBM Plex Sans',sans-serif;
# }}
# .msg-bubble.ai {{
#     background:{CARD2}; border:1px solid {BORDER};
#     color:{TXT_S}; border-bottom-left-radius:4px;
# }}
# .msg-bubble.user {{
#     background:linear-gradient(135deg,{BLUE} 0%,#4f46e5 100%);
#     color:#fff; border-bottom-right-radius:4px;
# }}
# .msg-bubble.ai strong {{ color:{BLUE}; }}
# .msg-bubble.ai code {{
#     background:{BLUE_LT}; color:{BLUE};
#     padding:1px 5px; border-radius:4px;
#     font-family:'IBM Plex Mono',monospace; font-size:0.82rem;
# }}
# .msg-time {{ font-size:0.65rem; color:{TXT_M}; margin-top:2px; text-align:right; }}

# .src-pill {{
#     display:inline-flex; align-items:center; gap:0.3rem;
#     background:{BLUE_LT}; border:1px solid {BLUE_MD};
#     color:{BLUE}; border-radius:100px;
#     font-size:0.65rem; font-weight:600; padding:0.15rem 0.6rem;
#     margin:2px; cursor:default;
# }}
# .src-row {{ display:flex; flex-wrap:wrap; gap:2px; margin-top:6px; }}

# .quick-btns {{
#     display:flex; flex-wrap:wrap; gap:0.5rem; padding:0.8rem 1.2rem;
#     border-top:1px solid {BORDER};
# }}
# .qbtn {{
#     background:{CARD2}; border:1px solid {BORDER2};
#     color:{TXT_S}; border-radius:100px;
#     font-size:0.72rem; font-weight:500; padding:0.3rem 0.8rem;
#     cursor:pointer; transition:all .18s;
#     font-family:'IBM Plex Sans',sans-serif;
# }}
# .qbtn:hover {{ border-color:{BLUE}; color:{BLUE}; background:{BLUE_LT}; }}

# .api-box {{
#     background:{CARD2}; border:1px solid {BORDER};
#     border-radius:12px; padding:1.2rem 1.4rem; margin-bottom:1rem;
# }}
# .api-label {{ font-size:0.72rem; font-weight:700; color:{TXT_M};
#     text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.5rem; }}

# .sources-card {{
#     background:{CARD2}; border:1px solid {BORDER};
#     border-radius:12px; padding:1rem 1.2rem; margin-top:0.8rem;
# }}
# .sources-title {{ font-size:0.72rem; font-weight:700; color:{TXT_M};
#     text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.6rem; }}
# .source-item {{
#     display:flex; gap:0.6rem; padding:0.5rem 0;
#     border-bottom:1px solid {BORDER};
# }}
# .source-item:last-child {{ border-bottom:none; }}
# .source-num {{
#     width:22px; height:22px; border-radius:50%;
#     background:{BLUE_LT}; color:{BLUE};
#     font-size:0.7rem; font-weight:700;
#     display:flex; align-items:center; justify-content:center; flex-shrink:0;
# }}
# .source-txt {{ font-size:0.78rem; color:{TXT_S}; line-height:1.4; }}
# .source-topic {{ font-weight:700; color:{TXT}; font-size:0.8rem; }}
# """

# # ════════════════════════════════════════════════════════════════════
# # STEP 4 ── CHATBOT TAB CONTENT
# # Copy this inside: with tab_chat:
# # ════════════════════════════════════════════════════════════════════
# CHATBOT_TAB_CODE = """
# with tab_chat:
#     import datetime as _dt

#     # ── API Key Setup ────────────────────────────────────────────────
#     col_key, col_info = st.columns([2, 1], gap="large")

#     with col_key:
#         st.markdown(f'''
#         <div class="api-box">
#             <div class="api-label">🔑 Groq API Key (Required)</div>
#         </div>
#         ''', unsafe_allow_html=True)

#         api_key_input = st.text_input(
#             "Groq API Key",
#             value=st.session_state.groq_api_key,
#             type="password",
#             placeholder="gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx",
#             help="Get your free key at console.groq.com",
#             label_visibility="collapsed",
#         )

#         key_cols = st.columns([1, 1, 1])
#         with key_cols[0]:
#             if st.button("🚀 Activate PCN-AI", use_container_width=True):
#                 if api_key_input.strip():
#                     st.session_state.groq_api_key = api_key_input.strip()
#                     with st.spinner("Initialising RAG engine…"):
#                         engine = get_rag_engine(st.session_state.groq_api_key)
#                         ok, errs = engine.initialize()
#                         if ok:
#                             st.session_state.rag_engine = engine
#                             st.session_state.rag_ready  = True
#                             st.success("✅ PCN-AI is ready!")
#                         else:
#                             st.error(f"❌ {' · '.join(errs)}")
#                 else:
#                     st.warning("Please enter your Groq API key.")
#         with key_cols[1]:
#             if st.button("🗑 Clear Chat", use_container_width=True):
#                 st.session_state.chat_history = []
#                 st.rerun()
#         with key_cols[2]:
#             status_txt = "🟢 Active" if st.session_state.rag_ready else "🔴 Not Active"
#             st.markdown(
#                 f'<div style="text-align:center;padding:0.5rem;font-size:0.8rem;'
#                 f'font-weight:600;color:{\\'#22c55e\\' if st.session_state.rag_ready else \\'#ef4444\\'};">'
#                 f'{status_txt}</div>',
#                 unsafe_allow_html=True
#             )

#     with col_info:
#         st.markdown(f'''
#         <div class="api-box">
#             <div class="api-label">ℹ️ How to get Groq API Key</div>
#             <div style="font-size:0.8rem;color:{TXT_S};line-height:1.7;">
#                 1️⃣ Go to <strong>console.groq.com</strong><br>
#                 2️⃣ Sign up (free)<br>
#                 3️⃣ API Keys → Create Key<br>
#                 4️⃣ Paste above & activate<br>
#                 <span style="color:{TEAL};font-size:0.75rem;">✦ Free tier: 30 req/min</span>
#             </div>
#         </div>
#         ''', unsafe_allow_html=True)

#     # ── Chat Interface ────────────────────────────────────────────────
#     L_chat, R_chat = st.columns([1.8, 1], gap="large")

#     with L_chat:
#         # Chat header
#         st.markdown(f'''
#         <div class="chat-wrap">
#             <div class="chat-header">
#                 <div class="chat-avatar">🧬</div>
#                 <div>
#                     <div class="chat-hname">PCN-AI Medical Assistant</div>
#                     <div class="chat-hstatus">
#                         <span class="chat-status-dot"></span>
#                         {"Online · RAG + Groq Llama3" if st.session_state.rag_ready else "Waiting for API key…"}
#                     </div>
#                 </div>
#             </div>
#         ''', unsafe_allow_html=True)

#         # Messages
#         chat_html = '<div class="chat-body" id="chat-body">'

#         # Welcome message
#         if not st.session_state.chat_history:
#             now = _dt.datetime.now().strftime("%H:%M")
#             chat_html += f'''
#             <div class="msg-row">
#                 <div class="msg-av ai">🧬</div>
#                 <div>
#                     <div class="msg-bubble ai">
#                         <strong>Welcome to PCN-AI!</strong> 👋<br><br>
#                         I am your medical assistant specialised in
#                         <strong>Pancreatic Cancer</strong> and
#                         <strong>Neurodegenerative Disorders</strong> detection.<br><br>
#                         I can help you understand:<br>
#                         • Risk factors & symptoms<br>
#                         • How our ML model works<br>
#                         • Biomarker interpretation<br>
#                         • Prevention strategies<br><br>
#                         Enter your Groq API key and ask me anything! 🔬
#                     </div>
#                     <div class="msg-time">{now}</div>
#                 </div>
#             </div>'''

#         for turn in st.session_state.chat_history:
#             t = turn.get("time","")
#             # User message
#             chat_html += f'''
#             <div class="msg-row user">
#                 <div class="msg-av usr">👤</div>
#                 <div>
#                     <div class="msg-bubble user">{turn["user"]}</div>
#                     <div class="msg-time" style="text-align:right">{t}</div>
#                 </div>
#             </div>'''
#             # AI message
#             ai_txt = turn["assistant"].replace("\\n","<br>").replace("**","<strong>",1)
#             # Simple markdown bold
#             import re
#             ai_txt = re.sub(r'\\*\\*(.*?)\\*\\*', r'<strong>\\1</strong>', turn["assistant"])
#             ai_txt = ai_txt.replace("\\n","<br>")

#             # Sources pills
#             src_pills = ""
#             if turn.get("sources"):
#                 src_pills = '<div class="src-row">'
#                 for s in turn["sources"][:3]:
#                     src_pills += f'<span class="src-pill">📄 {s["topic"][:30]}</span>'
#                 src_pills += '</div>'

#             chat_html += f'''
#             <div class="msg-row">
#                 <div class="msg-av ai">🧬</div>
#                 <div>
#                     <div class="msg-bubble ai">{ai_txt}{src_pills}</div>
#                     <div class="msg-time">{t}</div>
#                 </div>
#             </div>'''

#         chat_html += '</div>'

#         # Quick questions
#         quick_qs = [
#             "What are pancreatic cancer symptoms?",
#             "Explain APOE-e4 gene risk",
#             "What does HbA1c indicate?",
#             "How does the PCN model work?",
#             "Normal Vitamin B12 range?",
#             "How to prevent Alzheimer's?",
#         ]
#         chat_html += '<div class="quick-btns">'
#         for q in quick_qs:
#             chat_html += f'<span class="qbtn">💬 {q}</span>'
#         chat_html += '</div></div>'

#         st.markdown(chat_html, unsafe_allow_html=True)

#         # Auto-scroll JS
#         st.markdown("""
#         <script>
#         const cb = document.getElementById('chat-body');
#         if(cb) cb.scrollTop = cb.scrollHeight;
#         </script>
#         """, unsafe_allow_html=True)

#         # Input area
#         with st.form("chat_form", clear_on_submit=True):
#             ic1, ic2 = st.columns([5, 1])
#             with ic1:
#                 user_q = st.text_input(
#                     "Ask PCN-AI",
#                     placeholder="e.g. What are the symptoms of pancreatic cancer?",
#                     label_visibility="collapsed",
#                 )
#             with ic2:
#                 send = st.form_submit_button("Send ➤", use_container_width=True)

#         if send and user_q.strip():
#             if not st.session_state.rag_ready:
#                 st.warning("⚠️ Please activate PCN-AI with your Groq API key first.")
#             else:
#                 with st.spinner("PCN-AI is thinking…"):
#                     answer, sources = st.session_state.rag_engine.chat(
#                         user_q,
#                         chat_history=st.session_state.chat_history
#                     )
#                 st.session_state.chat_history.append({
#                     "user":      user_q,
#                     "assistant": answer,
#                     "sources":   sources,
#                     "time":      _dt.datetime.now().strftime("%H:%M"),
#                 })
#                 st.rerun()

#     # ── Right Panel: Info + Sources ───────────────────────────────────
#     with R_chat:
#         # Knowledge base stats
#         st.markdown(f'''
#         <div class="sources-card">
#             <div class="sources-title">📚 Knowledge Base</div>
#             <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;margin-bottom:0.8rem">
#                 <div style="background:{BLUE_LT};border:1px solid {BLUE_MD};
#                     border-radius:8px;padding:0.6rem;text-align:center;">
#                     <div style="font-size:1.3rem;font-weight:700;color:{BLUE}">17</div>
#                     <div style="font-size:0.65rem;color:{TXT_M};text-transform:uppercase;
#                         letter-spacing:0.08em">Knowledge Chunks</div>
#                 </div>
#                 <div style="background:{GREEN_LT};border:1px solid {GREEN_MD};
#                     border-radius:8px;padding:0.6rem;text-align:center;">
#                     <div style="font-size:1.3rem;font-weight:700;color:{GREEN}">6</div>
#                     <div style="font-size:0.65rem;color:{TXT_M};text-transform:uppercase;
#                         letter-spacing:0.08em">Topic Categories</div>
#                 </div>
#             </div>
#         ''', unsafe_allow_html=True)

#         topics_list = [
#             ("🦠", "Pancreatic Cancer", "6 chunks"),
#             ("🧠", "Neuro Disorders",   "5 chunks"),
#             ("⚗️",  "PCN ML Model",     "4 chunks"),
#             ("🥗", "Prevention",        "2 chunks"),
#         ]
#         for icon, topic, count in topics_list:
#             st.markdown(f'''
#             <div style="display:flex;align-items:center;gap:0.6rem;
#                 padding:0.4rem 0;border-bottom:1px solid {BORDER};">
#                 <span style="font-size:1rem">{icon}</span>
#                 <div style="flex:1">
#                     <div style="font-size:0.8rem;font-weight:600;color:{TXT}">{topic}</div>
#                     <div style="font-size:0.68rem;color:{TXT_M}">{count}</div>
#                 </div>
#             </div>''', unsafe_allow_html=True)
#         st.markdown("</div>", unsafe_allow_html=True)

#         # Last sources used
#         if st.session_state.chat_history:
#             last_turn = st.session_state.chat_history[-1]
#             if last_turn.get("sources"):
#                 st.markdown(f'''
#                 <div class="sources-card" style="margin-top:0.8rem">
#                     <div class="sources-title">🔍 Sources Used (Last Response)</div>
#                 ''', unsafe_allow_html=True)
#                 for i, src in enumerate(last_turn["sources"][:4], 1):
#                     score_pct = int(src.get("score", 0) * 100)
#                     st.markdown(f'''
#                     <div class="source-item">
#                         <div class="source-num">{i}</div>
#                         <div class="source-txt">
#                             <div class="source-topic">{src["topic"]}</div>
#                             <div style="font-size:0.7rem;color:{TXT_M}">
#                                 Relevance: {score_pct}% · ID: {src["id"]}
#                             </div>
#                         </div>
#                     </div>''', unsafe_allow_html=True)
#                 st.markdown("</div>", unsafe_allow_html=True)

#         # Sample questions
#         st.markdown(f'''
#         <div class="sources-card" style="margin-top:0.8rem">
#             <div class="sources-title">💡 Sample Questions</div>
#         ''', unsafe_allow_html=True)
#         sample_qs = [
#             "What is APOE-e4 gene?",
#             "Explain Metabolic Index formula",
#             "When should I see a doctor?",
#             "What does 89.36% ROC-AUC mean?",
#             "Normal BMI for healthy adult?",
#             "How is Vitamin B12 related to brain?",
#             "What is SMOTE balancing?",
#         ]
#         for sq in sample_qs:
#             st.markdown(
#                 f'<div style="font-size:0.78rem;color:{TXT_S};padding:0.3rem 0;'
#                 f'border-bottom:1px solid {BORDER};">❓ {sq}</div>',
#                 unsafe_allow_html=True
#             )
#         st.markdown("</div>", unsafe_allow_html=True)
# """


# # ════════════════════════════════════════════════════════════════════
# # COMPLETE INTEGRATION GUIDE
# # ════════════════════════════════════════════════════════════════════
# INTEGRATION_GUIDE = """
# HOW TO INTEGRATE INTO YOUR app.py:
# =====================================

# 1. Install dependencies:
#    pip install groq faiss-cpu sentence-transformers

# 2. Add imports at top of app.py:
#    from rag.rag_engine import get_rag_engine
#    from rag.knowledge_base import get_topics

# 3. Add session states (after existing ones):
#    if "chat_history" not in st.session_state: st.session_state.chat_history = []
#    if "rag_engine"   not in st.session_state: st.session_state.rag_engine   = None
#    if "rag_ready"    not in st.session_state: st.session_state.rag_ready    = False
#    if "groq_api_key" not in st.session_state: st.session_state.groq_api_key = ""

# 4. Change your tabs line to include chatbot:
#    tab1, tab2, tab3, tab4, tab_chat = st.tabs([
#        "  📊  Result Overview  ",
#        "  🧬  Feature Analysis  ",
#        "  📈  Biomarker Charts  ",
#        "  📋  Clinical Report  ",
#        "  🤖  PCN-AI Chatbot  ",   ← ADD THIS
#    ])

# 5. Add CSS from CHATBOT_CSS into your existing <style> block

# 6. Add the chatbot tab content (see chatbot_tab.py)

# 7. Get Groq API key FREE at: https://console.groq.com

# 8. Folder structure:
#    LAST_PROJ_MEDI/
#    ├── app.py
#    ├── api.py
#    ├── rag/
#    │   ├── __init__.py
#    │   ├── knowledge_base.py
#    │   ├── rag_engine.py
#    └── requirements.txt
# """

# print(INTEGRATION_GUIDE)