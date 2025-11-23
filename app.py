import streamlit as st
import google.generativeai as genai

# --- 1. Page Config ---
st.set_page_config(
    page_title="DEV",
    page_icon="🤖",
    layout="centered"
)

# --- 2. Theme Logic ---
if "theme" not in st.session_state:
    st.session_state.theme = False # Default Light

def toggle_theme():
    st.session_state.theme = not st.session_state.theme

# --- 3. Color Settings ---
if st.session_state.theme:
    # 🌙 Night Mode
    main_bg = "#0E1117"
    text_color = "#FFFFFF"
    title_color = "#00C6FF"  # Neon Blue
else:
    # ☀️ Day Mode
    main_bg = "#FFFFFF"
    text_color = "#000000"
    title_color = "#00008B"  # Dark Blue

# --- 4. CSS Styling ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap');

    /* Background & Text */
    .stApp {{
        background-color: {main_bg} !important;
        color: {text_color} !important;
    }}

    /* All Text Elements */
    p, div, span, li, .stMarkdown, .stCaption {{
        color: {text_color} !important;
    }}
    
    /* Title Font (Orbitron) */
    h1 {{
        font-family: 'Orbitron', sans-serif !important;
        color: {title_color} !important;
        text-align: center;
        font-size: 3rem !important; /* અક્ષરો મોટા કર્યા */
        letter-spacing: 3px;
        margin-top: -10px;
    }}

    /* Mobile Menu Button Color */
    [data-testid="stSidebarCollapsedControl"] {{
        color: {text_color} !important;
        display: block !important;
        z-index: 99999 !important;
    }}
    
    /* Hide Streamlit Branding */
    [data-testid="stToolbar"], 
    [data-testid="stDecoration"], 
    footer, 
    header {{
        visibility: hidden !important;
        display: none !important;
    }}

    .block-container {{
        padding-top: 2rem !important;
        padding-bottom: 5rem !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. Layout Elements ---

# Title (DEV) with AI Logo
st.markdown(f"""
    <h1 style='display: flex; align-items: center; justify-content: center; gap: 15px;'>
        <img src="https://cdn-icons-png.flaticon.com/512/2040/2040946.png" width="50" height="50" style="vertical-align: middle;">
        DEV
    </h1>
    """, unsafe_allow_html=True)

# Developer Info
st.markdown(f"""
    <div style='text-align: center; color: {text_color}; font-size: 13px; margin-bottom: 5px; opacity: 0.9;'>
        Developed by <b>Devendra Ramanuj</b> | 📱 9276505035
    </div>
    """, unsafe_allow_html=True)

# Switch
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    mode = st.toggle("🌗 Day / Night Mode", value=st.session_state.theme, on_change=toggle_theme)

# --- 6. Sidebar ---
with st.sidebar:
    st.title("Settings")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- 7. API Setup ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
except:
    st.error("Error: Please check API Key.")
    st.stop()

# --- 8. Chat Logic ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "જયશ્રી કૃષ્ણ! 🙏 હું DEV છું. બોલો, આજે હું તમારી શું સેવા કરું?"}
    ]

for message in st.session_state.messages:
    avatar = "🤖" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# --- 9. Input ---
if user_input := st.chat_input("Ask DEV..."):
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
