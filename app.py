import streamlit as st
import google.generativeai as genai

# --- 1. Page Config ---
st.set_page_config(
    page_title="Dev Bot",
    page_icon="🤖",
    layout="centered"
)

# --- 2. CSS (Hide Logos + Clean Look) ---
st.markdown("""
    <style>
    /* બેકગ્રાઉન્ડ */
    .stApp {
        background-color: #f0f2f6;
    }

    /* બધું છુપાવો (Header, Footer, Toolbar) */
    [data-testid="stToolbar"], 
    [data-testid="stDecoration"], 
    footer, 
    header {
        visibility: hidden !important;
        display: none !important;
    }

    /* મોબાઈલ મેનુ બટન દેખાવું જોઈએ */
    [data-testid="stSidebarCollapsedControl"] {
        display: block !important;
        visibility: visible !important;
        top: 15px !important;
        z-index: 99999 !important;
    }

    /* ટાઈટલનું સેટિંગ */
    h1 {
        color: #1f618d;
        text-align: center;
        font-family: sans-serif;
        margin-bottom: 5px; /* નીચે ઓછી જગ્યા */
        margin-top: -40px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Sidebar (ફક્ત Clear Chat માટે) ---
with st.sidebar:
    st.title("Settings")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- 4. Main Title & Developer Credit (અહીં જ દેખાશે) ---
st.title("Dev Bot")

# તમારું નામ અહીં મુક્યું છે (ટાઈટલની નીચે)
st.markdown("""
    <div style='text-align: center; color: grey; font-size: 14px; margin-bottom: 20px;'>
        Developed by <b>Devendra Ramanuj</b> | 📱 9276505035
    </div>
    """, unsafe_allow_html=True)

st.caption("Emotional AI Companion (Gujarati / English)")

# --- 5. API Setup ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
except:
    st.error("Error: Please check API Key.")
    st.stop()

# --- 6. Chat Logic ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am Dev Bot. (હું ગુજરાતી સમજું છું. બોલો, શું મદદ કરું?)"}
    ]

# મેસેજ બતાવો
for message in st.session_state.messages:
    avatar = "🤖" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# --- 7. Input & Response ---
if user_input := st.chat_input("Message Dev Bot..."):
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
