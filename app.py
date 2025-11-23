import streamlit as st
import google.generativeai as genai

# --- 1. Page Config ---
st.set_page_config(
    page_title="Dev Bot",
    page_icon="🤖",
    layout="centered"
)

# --- 2. Sidebar Settings ---
with st.sidebar:
    st.title("⚙️ Settings")
    
    # Day / Night Switch
    theme_mode = st.toggle("🌗 Day / Night Mode", value=False)
    
    # Clear Chat Button
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
        
    st.divider()
    
    # Developer Credit
    st.markdown("""
    <div style='text-align: center; color: grey;'>
        <small>Developed by</small><br>
        <b>Devendra Ramanuj</b><br>
        📱 9276505035
    </div>
    """, unsafe_allow_html=True)

# --- 3. Dynamic CSS (AI Look) ---
if theme_mode:
    main_bg = "#0E1117"      # Dark
    text_color = "#E0E0E0"   # Light Text
    title_color = "#00C6FF"  # Neon Blue
else:
    main_bg = "#FFFFFF"      # White
    text_color = "#000000"   # Black Text
    title_color = "#00008B"  # Dark Blue

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap');

    .stApp {{
        background-color: {main_bg} !important;
        color: {text_color} !important;
    }}
    
    h1 {{
        font-family: 'Orbitron', sans-serif !important;
        color: {title_color} !important;
        text-align: center;
        font-size: 3rem !important;
        letter-spacing: 2px;
        margin-top: -20px;
    }}

    .stCaption, p, li {{
        color: {text_color} !important;
    }}
    
    [data-testid="stToolbar"], 
    [data-testid="stDecoration"], 
    footer, 
    header {{
        visibility: hidden !important;
        display: none !important;
    }}

    [data-testid="stSidebarCollapsedControl"] {{
        display: block !important;
        visibility: visible !important;
        color: {text_color} !important;
        top: 15px !important;
        z-index: 99999 !important;
    }}
    
    .block-container {{
        padding-top: 2rem !important;
        padding-bottom: 5rem !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. Developer Info (Top Header) ---
st.markdown(f"""
    <div style='text-align: center; color: {text_color}; font-size: 13px; margin-bottom: 5px; opacity: 0.8;'>
        Developed by <b>Devendra Ramanuj</b> | 📱 9276505035
    </div>
    """, unsafe_allow_html=True)

# --- 5. Main Title ---
st.markdown(f"""
    <h1 style='display: flex; align-items: center; justify-content: center; gap: 15px;'>
        <img src="https://cdn-icons-png.flaticon.com/512/2040/2040946.png" width="50" height="50" style="vertical-align: middle;">
        DEV BOT
    </h1>
    """, unsafe_allow_html=True)

st.caption("Advanced AI Agent (Gujarati / English)")

# --- 6. API Setup ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
except:
    st.error("Error: Please check API Key.")
    st.stop()

# --- 7. Chat Logic (જયશ્રી કૃષ્ણ વાળો ફેરફાર) ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        # અહીં મેસેજ બદલ્યો છે
        {"role": "assistant", "content": "જયશ્રી કૃષ્ણ! 🙏 હું દેવ બોટ છું. બોલો, આજે હું તમારી શું સેવા કરું?"}
    ]

for message in st.session_state.messages:
    avatar = "🤖" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# --- 8. Input & Response ---
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
