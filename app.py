import streamlit as st
import google.generativeai as genai

# --- 1. Page Config ---
st.set_page_config(
    page_title="Dev Bot",
    page_icon="🤖",
    layout="centered"
)

# --- 2. Theme Logic ---
if "theme" not in st.session_state:
    st.session_state.theme = False

def toggle_theme():
    st.session_state.theme = not st.session_state.theme

if st.session_state.theme:
    main_bg = "#0E1117"
    text_color = "#E0E0E0"
    title_color = "#00C6FF"
else:
    main_bg = "#FFFFFF"
    text_color = "#000000"
    title_color = "#00008B"

# --- 3. SUPER STRONG CSS ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap');

    /* કલર્સ */
    .stApp {{
        background-color: {main_bg} !important;
        color: {text_color} !important;
    }}
    
    h1 {{
        font-family: 'Orbitron', sans-serif !important;
        color: {title_color} !important;
        text-align: center;
        font-size: 2.5rem !important;
        margin-top: -10px;
    }}

    .dev-text {{
        text-align: center;
        color: {text_color};
        font-size: 13px;
        opacity: 0.8;
        margin-bottom: 10px;
    }}

    /* ================================================= */
    /* 🛑 ULTIMATE HIDDEN MODE (બધું જ સાફ)            */
    /* ================================================= */
    
    /* 1. Streamlit Header (ઉપરની પટ્ટી) */
    header[data-testid="stHeader"] {{
        display: none !important;
        visibility: hidden !important;
    }}

    /* 2. Toolbar (જમણી બાજુના 3 ટપકાં & મેનુ) */
    div[data-testid="stToolbar"] {{
        display: none !important;
        visibility: hidden !important;
    }}

    /* 3. Decoration (રંગબેરંગી લાઈન) */
    div[data-testid="stDecoration"] {{
        display: none !important;
        visibility: hidden !important;
    }}

    /* 4. Status Widget (Manage App Button - જમણે નીચે) */
    div[data-testid="stStatusWidget"] {{
        display: none !important;
        visibility: hidden !important;
    }}

    /* 5. Footer (Made with Streamlit) */
    footer {{
        display: none !important;
        visibility: hidden !important;
    }}

    /* 6. ખાસ Deploy Button */
    .stDeployButton {{
        display: none !important;
        visibility: hidden !important;
    }}
    
    /* ================================================= */

    /* મોબાઈલ સાઈડબાર મેનુ બટન (આ રાખવું પડશે નહિતર મેનુ નહીં ખૂલે) */
    [data-testid="stSidebarCollapsedControl"] {{
        display: block !important;
        visibility: visible !important;
        color: {text_color} !important;
        top: 15px !important;
        z-index: 999999 !important;
    }}
    
    /* મોબાઈલમાં જગ્યા સેટ કરવા */
    .block-container {{
        padding-top: 3rem !important;
        padding-bottom: 5rem !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. Layout Elements ---

# Title
st.markdown(f"""
    <h1 style='display: flex; align-items: center; justify-content: center; gap: 10px;'>
        <img src="https://cdn-icons-png.flaticon.com/512/2040/2040946.png" width="45" height="45" style="vertical-align: middle;">
        DEV BOT
    </h1>
    """, unsafe_allow_html=True)

# Info
st.markdown(f"""
    <div class="dev-text">
        Developed by <b>Devendra Ramanuj</b> | 📱 9276505035
    </div>
    """, unsafe_allow_html=True)

# Switch
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    mode = st.toggle("🌗 Day / Night Mode", value=st.session_state.theme, on_change=toggle_theme)

# --- 5. Sidebar ---
with st.sidebar:
    st.title("Settings")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- 6. API Setup ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
except:
    st.error("Error: Please check API Key.")
    st.stop()

# --- 7. Chat Logic ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "જયશ્રી કૃષ્ણ! 🙏 હું દેવ બોટ છું. બોલો, આજે હું તમારી શું સેવા કરું?"}
    ]

for message in st.session_state.messages:
    avatar = "🤖" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# --- 8. Input ---
if user_input := st.chat_input("Ask Dev Bot..."):
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        chat_history = []
        for m in st.session_state.messages:
            if m["role"] != "system":
                role = "model" if m["role"] == "assistant" else "user"
                chat_history.append({"role": role, "parts": [m["content"]]})

        response = model.generate_content(chat_history)
        
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

    except Exception as e:
        st.error("Connection Error.")
