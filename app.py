import streamlit as st
import google.generativeai as genai

# --- 1. Page Config ---
st.set_page_config(
    page_title="Dev Bot",
    page_icon="🤖",
    layout="centered"
)

# --- 2. CSS (Color & Layout Fixing) ---
st.markdown("""
    <style>
    /* 1. આખા પેજનું બેકગ્રાઉન્ડ */
    .stApp {
        background-color: #f0f2f6 !important;
    }

    /* 2. વધારાની જગ્યા કાઢવા */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 5rem !important;
    }

    /* 3. હેડર, ફૂટર, લોગો ગાયબ */
    [data-testid="stToolbar"], 
    [data-testid="stDecoration"], 
    footer, 
    header {
        visibility: hidden !important;
        display: none !important;
    }

    /* 4. મોબાઈલ મેનુ બટન (કાળા રંગનું) */
    [data-testid="stSidebarCollapsedControl"] {
        display: block !important;
        visibility: visible !important;
        top: 10px !important;
        z-index: 99999 !important;
        color: #000000 !important;
    }

    /* 5. ડેવલપર નામનો કલર (કાળો/ડાર્ક) */
    .dev-text {
        color: #000000 !important;
        text-align: center;
        font-size: 13px;
        margin-bottom: 5px;
        font-weight: bold;
        font-family: sans-serif;
    }
    
    /* 6. કેપ્શન પણ ડાર્ક */
    .stCaption {
        color: #333333 !important;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Sidebar ---
with st.sidebar:
    st.title("Settings")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- 4. Developer Credit ---
st.markdown("""
    <div class="dev-text">
        Developed by <b>Devendra Ramanuj</b> | 📱 9276505035
    </div>
    """, unsafe_allow_html=True)

# --- 5. Main Title with AI Logo (અહીં ફેરફાર કર્યો છે) ---
# આપણે st.title ની જગ્યાએ HTML વાપર્યું છે જેથી ઈમેજ મુકી શકાય
st.markdown("""
    <h1 style='text-align: center; color: #00008B; font-family: sans-serif; margin-top: -10px; display: flex; align-items: center; justify-content: center; gap: 10px;'>
        <img src="https://cdn-icons-png.flaticon.com/512/2040/2040946.png" width="40" height="40" style="vertical-align: middle;">
        Dev Bot
    </h1>
    """, unsafe_allow_html=True)

st.caption("Emotional AI Companion (Gujarati / English)")

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
        {"role": "assistant", "content": "Hello! I am Dev Bot. (હું ગુજરાતી સમજું છું. બોલો, શું મદદ કરું?)"}
    ]

for message in st.session_state.messages:
    avatar = "🤖" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# --- 8. Input & Response ---
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
