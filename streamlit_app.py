import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from graph.workflow import build_graph
from core.config import settings


st.set_page_config(
    page_title="GlowAI — Premium Skincare Consultant",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

#css
st.markdown("""
<style>
/* Dark background */
.stApp {
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
}

/* Hide Streamlit default elements */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; padding-bottom: 2rem; }

/* Chat message styling */
.stChatMessage {
    background: rgba(30, 41, 59, 0.8) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 16px !important;
    backdrop-filter: blur(16px);
}

/* Input box */
.stChatInput textarea {
    background: rgba(0,0,0,0.3) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 30px !important;
    color: white !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(15, 23, 42, 0.95) !important;
    border-right: 1px solid rgba(255,255,255,0.1);
}

/* Tags */
.skin-tag {
    display: inline-block;
    background: rgba(244,63,94,0.15);
    border: 1px solid rgba(244,63,94,0.4);
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 13px;
    color: #f8fafc;
    margin: 3px;
}

/* Product card */
.product-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 16px;
    transition: all 0.3s ease;
}

.prod-brand {
    font-size: 11px;
    color: #f43f5e;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.prod-name {
    font-size: 20px;
    font-weight: 700;
    color: #f8fafc;
    margin: 6px 0 4px;
}

.prod-meta {
    font-size: 13px;
    color: #94a3b8;
    margin-bottom: 14px;
}

.analysis-box {
    background: rgba(139,92,246,0.1);
    border: 1px solid rgba(139,92,246,0.3);
    border-radius: 16px;
    padding: 16px;
    margin-bottom: 20px;
}

/* Gradient title */
.glow-title {
    background: linear-gradient(90deg, #f43f5e, #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.4rem;
    font-weight: 800;
    margin-bottom: 0;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #f43f5e, #8b5cf6) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    padding: 8px 24px !important;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(244,63,94,0.4) !important;
}
</style>
""", unsafe_allow_html=True)



if "messages"     not in st.session_state: st.session_state.messages     = []
if "skin_profile" not in st.session_state: st.session_state.skin_profile = {}
if "products"     not in st.session_state: st.session_state.products     = []
if "skin_analysis"not in st.session_state: st.session_state.skin_analysis= None
if "graph_cache"  not in st.session_state: st.session_state.graph_cache  = {}



def get_graph(api_key: str):
    if api_key not in st.session_state.graph_cache:
        st.session_state.graph_cache[api_key] = build_graph(api_key)
    return st.session_state.graph_cache[api_key]


with st.sidebar:
    st.markdown("## 🌿 GlowAI")
    st.markdown("<p style='color:#94a3b8;font-size:13px;'>AI Skincare Consultant</p>",
                unsafe_allow_html=True)
    st.divider()

    # API Key input
    st.markdown("### 🔑 Gemini API Key")
    api_key = st.text_input(
        label="api_key",
        value=settings.GEMINI_API_KEY if settings.GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE" else "",
        type="password",
        placeholder="AIza...",
        label_visibility="collapsed",
    )
    st.markdown(
        "<p style='font-size:11px;color:#64748b;'>"
        "Get a free key at <a href='https://aistudio.google.com/app/apikey' "
        "target='_blank' style='color:#8b5cf6;'>aistudio.google.com</a></p>",
        unsafe_allow_html=True,
    )

    st.divider()

  
    st.markdown("### 🧴 Your Skin Profile")
    profile = st.session_state.skin_profile

    if not profile or not any(v for v in profile.values() if v):
        st.markdown(
            "<p style='color:#94a3b8;font-style:italic;font-size:13px;"
            "background:rgba(0,0,0,0.2);padding:12px;border-radius:10px;'>"
            "💬 Chat with me to build your skin profile!</p>",
            unsafe_allow_html=True,
        )
    else:
        def render_tags(label, values):
            if not values:
                return
            if isinstance(values, str):
                values = [values]
            values = [v for v in values if v]
            if not values:
                return
            st.markdown(
                f"<p style='font-size:11px;color:#94a3b8;text-transform:uppercase;"
                f"letter-spacing:1px;margin-bottom:4px;'>{label}</p>",
                unsafe_allow_html=True,
            )
            tags_html = "".join([f"<span class='skin-tag'>{v}</span>" for v in values])
            st.markdown(
                f"<div style='margin-bottom:12px;'>{tags_html}</div>",
                unsafe_allow_html=True,
            )

        render_tags("Skin Type",     [profile.get("skin_type")] if profile.get("skin_type") else [])
        render_tags("Conditions",    profile.get("conditions", []))
        render_tags("Concerns",      profile.get("concerns", []))
        render_tags("Problem Areas", profile.get("problem_areas", []))
        render_tags("Budget",        [profile.get("budget")] if profile.get("budget") else [])

    st.divider()

   
    if st.button("↺ Reset Conversation", use_container_width=True):
        st.session_state.messages      = []
        st.session_state.skin_profile  = {}
        st.session_state.products      = []
        st.session_state.skin_analysis = None
        st.rerun()

    st.markdown(
        "<p style='font-size:11px;color:#334155;text-align:center;margin-top:20px;'>"
        "LangGraph · Gemini · DuckDuckGo RAG</p>",
        unsafe_allow_html=True,
    )



st.markdown("<div class='glow-title'>🌿 GlowAI</div>", unsafe_allow_html=True)
st.markdown(
    "<p style='color:#94a3b8;margin-top:0;margin-bottom:24px;'>"
    "Powered by Google Gemini + LangGraph · Personalized skincare recommendations</p>",
    unsafe_allow_html=True,
)


if not st.session_state.messages:
    with st.chat_message("assistant", avatar="✨"):
        st.markdown(
            "Hello! I'm **GlowAI**, your AI skincare consultant powered by Google Gemini. 🌿\n\n"
            "Tell me about your **skin type** and **concerns** to get personalized product recommendations!"
        )

for msg in st.session_state.messages:
    role = msg["role"]
    with st.chat_message(role, avatar="🧴" if role == "assistant" else "👤"):
        st.markdown(msg["content"])


if st.session_state.products:
    st.divider()
    st.markdown("### 💄 Your Personalized Recommendations")

    # Skin analysis box
    analysis = st.session_state.skin_analysis
    if analysis and isinstance(analysis, dict) and analysis.get("profile_summary"):
        good  = " · ".join(analysis.get("good_ingredients", []))
        avoid = " · ".join(analysis.get("avoid_ingredients", []))
        st.markdown(f"""
        <div class='analysis-box'>
            <p style='color:#8b5cf6;font-weight:700;margin-bottom:8px;'>🔬 AI Skin Analysis</p>
            <p style='font-size:14px;color:#cbd5e1;margin-bottom:8px;'>{analysis["profile_summary"]}</p>
            {"<p style='font-size:12px;color:#10b981;'>✅ Good ingredients: " + good + "</p>" if good else ""}
            {"<p style='font-size:12px;color:#f43f5e;'>❌ Avoid: " + avoid + "</p>" if avoid else ""}
        </div>
        """, unsafe_allow_html=True)

  
    cols = st.columns(len(st.session_state.products))
    for col, p in zip(cols, st.session_state.products):
        if not isinstance(p, dict):
            continue
        with col:
            merits   = "".join([f"<li style='color:#cbd5e1;font-size:13px;'>{m}</li>"
                                 for m in p.get("merits", [])])
            demerits = "".join([f"<li style='color:#cbd5e1;font-size:13px;'>{d}</li>"
                                 for d in p.get("demerits", [])])
            links    = "".join([
                f"<a href='{l.get('url','#')}' target='_blank' "
                f"style='background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.15);"
                f"color:white;text-decoration:none;padding:6px 14px;border-radius:8px;"
                f"font-size:12px;margin-right:6px;display:inline-block;margin-top:4px;'>"
                f"{l.get('store','Buy')}</a>"
                for l in p.get("buy_links", []) if isinstance(l, dict)
            ])

            st.markdown(f"""
            <div class='product-card'>
                <div class='prod-brand'>{p.get('brand','')}</div>
                <div class='prod-name'>{p.get('name','')}</div>
                <div class='prod-meta'>{p.get('category','').title()} · {p.get('price_range','')}</div>
                {"<p style='font-size:12px;color:#10b981;font-weight:600;'>✅ Pros</p><ul style='margin:4px 0 10px;padding-left:18px;'>" + merits + "</ul>" if merits else ""}
                {"<p style='font-size:12px;color:#f43f5e;font-weight:600;'>⚠️ Cons</p><ul style='margin:4px 0 12px;padding-left:18px;'>" + demerits + "</ul>" if demerits else ""}
                <div style='margin-top:12px;'>{links}</div>
            </div>
            """, unsafe_allow_html=True)



user_input = st.chat_input("E.g., My skin is oily and I have acne on my cheeks...")

if user_input:
   
    active_key = (api_key or "").strip() or settings.GEMINI_API_KEY
    if not active_key or active_key == "YOUR_GEMINI_API_KEY_HERE":
        with st.chat_message("assistant", avatar="✨"):
            st.warning("⚠️ Please enter your Gemini API key in the sidebar.")
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
