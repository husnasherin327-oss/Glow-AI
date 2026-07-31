import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from graph.workflow import build_graph
from core.config import settings


# ──────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GlowAI — Premium Skincare Consultant",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ──────────────────────────────────────────────────────────────────────────
# LUXURY PASTEL CSS  (Rhode Skin × Glow Recipe × Apple × Beauty of Joseon)
# ──────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,500&family=Inter:wght@300;400;500;600;700;800&display=swap');

:root{
    --blush:       #ffd9e2;
    --blush-deep:  #ffb8c9;
    --cream:       #fdf6f0;
    --sand:        #f4e9dd;
    --lavender:    #ece3fb;
    --sage:        #e6f0e6;
    --gold:        #c9a876;
    --gold-deep:   #b8935e;
    --rose:        #e8a0ab;
    --ink:         #3a2e2f;
    --ink-soft:    #6b5a5c;
    --ink-mute:    #9c8a8c;
    --white-glass: rgba(255,255,255,0.62);
    --white-glass-strong: rgba(255,255,255,0.85);
    --border-soft: rgba(255,255,255,0.9);
    --shadow-soft: 0 8px 32px rgba(201,158,168,0.18);
    --shadow-hover: 0 16px 48px rgba(201,158,168,0.28);
}

html, body, [class*="css"]{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* ── App background: soft pastel gradient wash ────────────────────────── */
.stApp{
    background:
        radial-gradient(circle at 10% 0%, rgba(255,217,226,0.55) 0%, transparent 45%),
        radial-gradient(circle at 90% 10%, rgba(236,227,251,0.55) 0%, transparent 45%),
        radial-gradient(circle at 50% 100%, rgba(230,240,230,0.45) 0%, transparent 50%),
        linear-gradient(180deg, #fffaf6 0%, #fdf6f0 40%, #fbf1f4 100%);
    background-attachment: fixed;
}

/* Hide default chrome */
#MainMenu, footer, header{ visibility:hidden; }
.block-container{ padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1100px; }

/* ── Scrollbar polish ─────────────────────────────────────────────────── */
::-webkit-scrollbar{ width:8px; height:8px; }
::-webkit-scrollbar-track{ background:transparent; }
::-webkit-scrollbar-thumb{ background:var(--blush-deep); border-radius:10px; }

/* ── HERO SECTION ─────────────────────────────────────────────────────── */
.hero-wrap{
    text-align:center;
    padding: 18px 12px 30px;
    margin-bottom: 8px;
    animation: fadeInDown 0.7s ease;
}
.hero-badge{
    display:inline-block;
    background: var(--white-glass-strong);
    border: 1px solid var(--border-soft);
    color: var(--gold-deep);
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 7px 20px;
    border-radius: 30px;
    margin-bottom: 18px;
    backdrop-filter: blur(10px);
    box-shadow: var(--shadow-soft);
}
.hero-title{
    font-family: 'Playfair Display', serif;
    font-weight: 700;
    font-size: 3.4rem;
    line-height: 1.08;
    margin: 0 0 10px;
    background: linear-gradient(100deg, #e8a0ab 0%, #c9a876 45%, #b98fd6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub{
    font-size: 1.05rem;
    color: var(--ink-soft);
    font-weight: 400;
    max-width: 560px;
    margin: 0 auto;
    line-height: 1.6;
}
@keyframes fadeInDown{
    from{ opacity:0; transform: translateY(-14px); }
    to{ opacity:1; transform: translateY(0); }
}

/* ── SIDEBAR ──────────────────────────────────────────────────────────── */
section[data-testid="stSidebar"]{
    background: linear-gradient(180deg, #fff6f8 0%, #fdf3ee 55%, #f7f0fa 100%);
    border-right: 1px solid rgba(232,160,171,0.25);
}
section[data-testid="stSidebar"] .block-container{ padding-top: 2rem; }

.sidebar-logo{
    font-family: 'Playfair Display', serif;
    font-weight: 700;
    font-size: 1.7rem;
    background: linear-gradient(100deg, #e8a0ab, #c9a876);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0;
}
.sidebar-tagline{
    color: var(--ink-mute);
    font-size: 12.5px;
    letter-spacing: 0.3px;
    margin-top: -2px;
}
.sidebar-section-title{
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.6px;
    text-transform: uppercase;
    color: var(--gold-deep);
    margin: 4px 0 10px;
}
.profile-empty{
    color: var(--ink-mute);
    font-style: italic;
    font-size: 13px;
    background: var(--white-glass);
    border: 1px dashed rgba(201,168,118,0.4);
    padding: 16px;
    border-radius: 16px;
    text-align:center;
    line-height: 1.5;
}
.profile-card{
    background: var(--white-glass-strong);
    border: 1px solid var(--border-soft);
    border-radius: 18px;
    padding: 16px 16px 4px;
    box-shadow: var(--shadow-soft);
    backdrop-filter: blur(12px);
}
.tag-label{
    font-size: 10.5px;
    color: var(--ink-mute);
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin-bottom: 6px;
    font-weight: 700;
}
.skin-tag{
    display:inline-block;
    background: linear-gradient(135deg, var(--blush), #ffeef2);
    border: 1px solid rgba(232,160,171,0.5);
    color: #8a4a56;
    padding: 4px 13px;
    border-radius: 20px;
    font-size: 12.5px;
    font-weight: 500;
    margin: 0 5px 10px 0;
}
.footer-credit{
    font-size: 10.5px;
    color: #c4b4b6;
    text-align:center;
    margin-top: 26px;
    letter-spacing: 0.5px;
}

/* Sidebar divider spacing */
section[data-testid="stSidebar"] hr{ margin: 1.1rem 0; border-color: rgba(201,158,168,0.25); }

/* ── BUTTONS ──────────────────────────────────────────────────────────── */
.stButton > button{
    background: linear-gradient(135deg, #f0b7c4, #d9b8ee) !important;
    color: #4a2f36 !important;
    border: none !important;
    border-radius: 30px !important;
    font-weight: 600 !important;
    font-size: 13.5px !important;
    padding: 10px 22px !important;
    box-shadow: 0 4px 16px rgba(217,184,238,0.35) !important;
    transition: all 0.25s ease !important;
}
.stButton > button:hover{
    transform: translateY(-2px) scale(1.01);
    box-shadow: 0 10px 26px rgba(217,184,238,0.5) !important;
}
.stButton > button:active{ transform: translateY(0); }

/* ── CHAT MESSAGES / BUBBLES ─────────────────────────────────────────── */
.stChatMessage{
    background: var(--white-glass-strong) !important;
    border: 1px solid var(--border-soft) !important;
    border-radius: 22px !important;
    backdrop-filter: blur(14px);
    box-shadow: var(--shadow-soft);
    padding: 4px 6px !important;
    margin-bottom: 14px !important;
    animation: fadeInUp 0.35s ease;
}
@keyframes fadeInUp{
    from{ opacity:0; transform: translateY(8px); }
    to{ opacity:1; transform: translateY(0); }
}
.stChatMessage p, .stChatMessage li{ color: var(--ink); font-size: 14.5px; line-height: 1.65; }

div[data-testid="stChatMessageAvatarUser"]{
    background: linear-gradient(135deg, #e8a0ab, #d9b8ee) !important;
}
div[data-testid="stChatMessageAvatarAssistant"], div[data-testid="stChatMessageAvatarCustom"]{
    background: linear-gradient(135deg, #c9e6c9, #ffe4b8) !important;
}

/* Chat input */
.stChatInput{ margin-top: 6px; }
.stChatInput textarea, div[data-testid="stChatInput"] textarea{
    background: var(--white-glass-strong) !important;
    border: 1.5px solid rgba(232,160,171,0.4) !important;
    border-radius: 30px !important;
    color: var(--ink) !important;
    padding: 12px 18px !important;
    box-shadow: var(--shadow-soft) !important;
}
div[data-testid="stChatInput"]{
    border-radius: 30px;
}
div[data-testid="stChatInput"] button{
    background: linear-gradient(135deg, #e8a0ab, #d9b8ee) !important;
    border-radius: 50% !important;
}

/* ── SECTION HEADERS ──────────────────────────────────────────────────── */
.section-heading{
    font-family: 'Playfair Display', serif;
    font-size: 1.7rem;
    font-weight: 600;
    color: var(--ink);
    margin: 6px 0 18px;
    display:flex; align-items:center; gap:10px;
}

/* ── ANALYSIS BOX ─────────────────────────────────────────────────────── */
.analysis-box{
    background: linear-gradient(135deg, rgba(236,227,251,0.55), rgba(255,217,226,0.4));
    border: 1px solid rgba(217,184,238,0.5);
    border-radius: 22px;
    padding: 22px 24px;
    margin-bottom: 26px;
    backdrop-filter: blur(10px);
    box-shadow: var(--shadow-soft);
}
.analysis-title{
    color: #8a6ab8;
    font-weight: 700;
    font-size: 13px;
    letter-spacing: 0.5px;
    margin-bottom: 10px;
    text-transform: uppercase;
}
.analysis-summary{
    font-size: 14.5px;
    color: var(--ink-soft);
    margin-bottom: 10px;
    line-height: 1.6;
}
.analysis-good{ font-size: 12.5px; color: #4f9a6a; font-weight: 500; margin: 2px 0; }
.analysis-avoid{ font-size: 12.5px; color: #d16b7a; font-weight: 500; margin: 2px 0; }

/* ── PRODUCT CARDS ────────────────────────────────────────────────────── */
.product-card{
    background: var(--white-glass-strong);
    border: 1px solid var(--border-soft);
    border-radius: 24px;
    padding: 24px 22px;
    margin-bottom: 18px;
    backdrop-filter: blur(14px);
    box-shadow: var(--shadow-soft);
    transition: all 0.3s cubic-bezier(.2,.8,.2,1);
    height: 100%;
}
.product-card:hover{
    transform: translateY(-6px);
    box-shadow: var(--shadow-hover);
    border-color: rgba(232,160,171,0.6);
}
.prod-brand{
    font-size: 10.5px;
    color: var(--gold-deep);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.6px;
}
.prod-name{
    font-family: 'Playfair Display', serif;
    font-size: 20px;
    font-weight: 600;
    color: var(--ink);
    margin: 6px 0 6px;
    line-height: 1.3;
}
.prod-meta{
    display:inline-block;
    font-size: 11.5px;
    color: #8a6ab8;
    background: rgba(236,227,251,0.6);
    padding: 3px 12px;
    border-radius: 20px;
    margin-bottom: 16px;
    font-weight: 600;
}
.prod-pros-title{ font-size: 12px; color: #4f9a6a; font-weight: 700; margin-bottom: 2px; }
.prod-cons-title{ font-size: 12px; color: #d16b7a; font-weight: 700; margin-bottom: 2px; }
.product-card ul{ margin: 4px 0 12px; padding-left: 18px; }
.product-card li{ color: var(--ink-soft); font-size: 12.8px; line-height: 1.55; margin-bottom: 2px; }

.buy-link{
    background: linear-gradient(135deg, #f0b7c4, #d9b8ee);
    color: #4a2f36 !important;
    text-decoration: none;
    padding: 7px 16px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    margin-right: 8px;
    display: inline-block;
    margin-top: 6px;
    box-shadow: 0 3px 10px rgba(217,184,238,0.35);
    transition: all 0.25s ease;
}
.buy-link:hover{
    transform: translateY(-2px);
    box-shadow: 0 8px 18px rgba(217,184,238,0.5);
}

/* ── DIVIDERS ─────────────────────────────────────────────────────────── */
hr{ border-color: rgba(201,158,168,0.25) !important; }

/* ── SPINNER / LOADING ────────────────────────────────────────────────── */
.stSpinner > div{
    border-top-color: var(--rose) !important;
}
.stSpinner p{ color: var(--ink-soft) !important; font-style: italic; }

/* ── ALERTS ───────────────────────────────────────────────────────────── */
div[data-testid="stAlert"]{
    border-radius: 16px !important;
    background: var(--white-glass-strong) !important;
    border: 1px solid rgba(232,160,171,0.4) !important;
}

/* ── RESPONSIVE ───────────────────────────────────────────────────────── */
@media (max-width: 768px){
    .hero-title{ font-size: 2.3rem; }
    .hero-sub{ font-size: 0.92rem; }
    .block-container{ padding-left: 1rem; padding-right: 1rem; }
}

/* ---------- Remove Streamlit black bottom bar ---------- */

[data-testid="stBottomBlockContainer"]{
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

[data-testid="stBottom"]{
    background: transparent !important;
}

[data-testid="stChatInputContainer"]{
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

footer{
    display:none !important;
}

</style>
""", unsafe_allow_html=True)




# ──────────────────────────────────────────────────────────────────────────
# SESSION STATE  (unchanged)
# ──────────────────────────────────────────────────────────────────────────
if "messages"      not in st.session_state: st.session_state.messages      = []
if "skin_profile"  not in st.session_state: st.session_state.skin_profile  = {}
if "products"       not in st.session_state: st.session_state.products      = []
if "skin_analysis" not in st.session_state: st.session_state.skin_analysis = None
if "graph_cache"   not in st.session_state: st.session_state.graph_cache   = {}


def get_graph(api_key: str):
    if api_key not in st.session_state.graph_cache:
        st.session_state.graph_cache[api_key] = build_graph(api_key)
    return st.session_state.graph_cache[api_key]


# ──────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<p class='sidebar-logo'>🌸 GlowAI</p>", unsafe_allow_html=True)
    st.markdown("<p class='sidebar-tagline'>Your AI Skincare Consultant</p>", unsafe_allow_html=True)
    st.divider()

    st.markdown("<p class='sidebar-section-title'>🧴 Your Skin Profile</p>", unsafe_allow_html=True)
    profile = st.session_state.skin_profile

    if not profile or not any(v for v in profile.values() if v):
        st.markdown(
            "<div class='profile-empty'>💬 Chat with me to build your<br>personalized skin profile!</div>",
            unsafe_allow_html=True,
        )
    else:
        def render_tags(label, values):
            if not values:
                return ""
            if isinstance(values, str):
                values = [values]
            values = [v for v in values if v]
            if not values:
                return ""
            tags_html = "".join([f"<span class='skin-tag'>{v}</span>" for v in values])
            return (
                f"<p class='tag-label'>{label}</p>"
                f"<div style='margin-bottom:6px;'>{tags_html}</div>"
            )

        profile_html = "<div class='profile-card'>"
        profile_html += render_tags("Skin Type",     [profile.get("skin_type")] if profile.get("skin_type") else [])
        profile_html += render_tags("Conditions",    profile.get("conditions", []))
        profile_html += render_tags("Concerns",      profile.get("concerns", []))
        profile_html += render_tags("Problem Areas", profile.get("problem_areas", []))
        profile_html += render_tags("Budget",        [profile.get("budget")] if profile.get("budget") else [])
        profile_html += "</div>"
        st.markdown(profile_html, unsafe_allow_html=True)

    st.divider()

    if st.button("↺  Reset Conversation", use_container_width=True):
        st.session_state.messages      = []
        st.session_state.skin_profile  = {}
        st.session_state.products      = []
        st.session_state.skin_analysis = None
        st.rerun()

    st.markdown(
        "<p class='footer-credit'>LangGraph · Gemini · DuckDuckGo RAG</p>",
        unsafe_allow_html=True,
    )


# ──────────────────────────────────────────────────────────────────────────
# HERO SECTION
# ──────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class='hero-wrap'>
    <div class='hero-badge'>✨ Personalized · AI-Powered · Dermatologist-Informed</div>
    <div class='hero-title'>GlowAI</div>
    <p class='hero-sub'>Your bespoke skincare consultant. Share your skin type and concerns,
    and receive thoughtfully curated product recommendations — made just for you.</p>
</div>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────
# CHAT HISTORY
# ──────────────────────────────────────────────────────────────────────────
if not st.session_state.messages:
    with st.chat_message("assistant", avatar="✨"):
        st.markdown(
            "Hello! I'm **GlowAI**, your AI skincare consultant. 🌸\n\n"
            "Tell me about your **skin type** and **concerns** to get personalized product recommendations!"
        )

for msg in st.session_state.messages:
    role = msg["role"]
    with st.chat_message(role, avatar="🧴" if role == "assistant" else "👤"):
        st.markdown(msg["content"])


# ──────────────────────────────────────────────────────────────────────────
# PRODUCT RECOMMENDATIONS
# ──────────────────────────────────────────────────────────────────────────
if st.session_state.products:
    st.divider()
    st.markdown("<div class='section-heading'>💄 Your Personalized Recommendations</div>", unsafe_allow_html=True)

    analysis = st.session_state.skin_analysis
    if analysis and isinstance(analysis, dict) and analysis.get("profile_summary"):
        good  = " · ".join(analysis.get("good_ingredients", []))
        avoid = " · ".join(analysis.get("avoid_ingredients", []))
        st.markdown(f"""
        <div class='analysis-box'>
            <p class='analysis-title'>🔬 AI Skin Analysis</p>
            <p class='analysis-summary'>{analysis["profile_summary"]}</p>
            {"<p class='analysis-good'>✅ Good ingredients: " + good + "</p>" if good else ""}
            {"<p class='analysis-avoid'>❌ Avoid: " + avoid + "</p>" if avoid else ""}
        </div>
        """, unsafe_allow_html=True)

    cols = st.columns(len(st.session_state.products))
    for col, p in zip(cols, st.session_state.products):
        if not isinstance(p, dict):
            continue
        with col:
            merits   = "".join([f"<li>{m}</li>" for m in p.get("merits", [])])
            demerits = "".join([f"<li>{d}</li>" for d in p.get("demerits", [])])
            links    = "".join([
                f"<a href='{l.get('url','#')}' target='_blank' class='buy-link'>{l.get('store','Buy')}</a>"
                for l in p.get("buy_links", []) if isinstance(l, dict)
            ])

            st.markdown(f"""
            <div class='product-card'>
                <div class='prod-brand'>{p.get('brand','')}</div>
                <div class='prod-name'>{p.get('name','')}</div>
                <div class='prod-meta'>{p.get('category','').title()} · {p.get('price_range','')}</div>
                {"<p class='prod-pros-title'>✅ Pros</p><ul>" + merits + "</ul>" if merits else ""}
                {"<p class='prod-cons-title'>⚠️ Cons</p><ul>" + demerits + "</ul>" if demerits else ""}
                <div style='margin-top:12px;'>{links}</div>
            </div>
            """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────
# CHAT INPUT + GRAPH INVOCATION  (backend logic unchanged)
# ──────────────────────────────────────────────────────────────────────────
user_input = st.chat_input("E.g., My skin is oily and I have acne on my cheeks...")

if user_input:
    # API key is provisioned server-side on Railway — no user input required.
    active_key = settings.GEMINI_API_KEY
    if not active_key or active_key == "YOUR_GEMINI_API_KEY_HERE":
        with st.chat_message("assistant", avatar="✨"):
            st.warning("⚠️ GlowAI is temporarily unavailable. Please try again shortly.")
        st.stop()

    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    lc_messages = []
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            lc_messages.append(HumanMessage(content=msg["content"]))
        else:
            lc_messages.append(AIMessage(content=msg["content"]))
    lc_messages.append(HumanMessage(content=user_input))

    initial_state = {
        "messages":       lc_messages,
        "skin_profile":   st.session_state.skin_profile,
        "search_results": "",
        "products":       [],
        "skin_analysis":  None,
        "response_type":  "chat",
        "final_message":  "",
    }

    with st.chat_message("assistant", avatar="✨"):
        with st.spinner("GlowAI is thinking..."):
            try:
                graph  = get_graph(active_key)
                result = graph.invoke(initial_state)

                response_type   = result.get("response_type", "chat")
                final_message   = result.get("final_message", "")
                updated_profile = result.get("skin_profile", {})
                products        = result.get("products", [])
                skin_analysis   = result.get("skin_analysis")

                # Update session state
                st.session_state.messages.append({"role": "user",      "content": user_input})
                st.session_state.messages.append({"role": "assistant", "content": final_message})
                st.session_state.skin_profile  = updated_profile
                st.session_state.skin_analysis = skin_analysis

                if response_type == "products" and products:
                    st.session_state.products = products

                st.markdown(final_message)

            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.session_state.messages.append({"role": "user",      "content": user_input})
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                st.error(error_msg)

    st.rerun()