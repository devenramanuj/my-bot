import streamlit as st
import google.generativeai as genai

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="Dev Bot",
    page_icon="🤖",
    layout="centered"
)

# --- 2. Strong CSS (બધું છુપાવવા માટેનો ખાસ કોડ) ---
st.markdown("""
    <style>
    /* 1. આખા પેજનું બેકગ્રાઉન્ડ */
    .stApp {
        background-color: #f0f2f6;
    }
    
    /* 2. ઉપરનું ટૂલબાર (જ્યાં GitHub અને મેનુ આવે છે) તેને જડમૂળથી છુપાવો */
    [data-testid="stToolbar"] {
        visibility: hidden !important;
        display: none !important;
    }
    
    /* 3. ઉપરનું Header Decoration (રંગબેરંગી પટ્ટી) */
    header {
        visibility: hidden !important;
    }
    
    /* 4. નીચેનું Footer (Made with Streamlit) */
    footer {
        visibility: hidden !important;
        display: none !important;
    }
    
    /* 5. ટાઈટલ સેન્ટરમાં અને સુંદર */
    h1 {
        color: #1f618d;
        text-align: center;
        font-family: sans-serif;
        margin-top: -50px; /* ઉપર જગ્યા ખાલી ન રહે એટલે થોડું ઉપર ખેંચ્યું */
    }
    
    /* 6. મોબાઈલમાં મેનુ બટન માટે જગ્યા (જો સાઈડબાર વાપરવી હોય તો) */
    .st-emotion-cache-16txtl3 {
        padding-top: 1rem; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Sidebar (મેનુ) ---
with st.sidebar:
    st.title("Settings")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: grey;'>
        <b>Developed by:</b><br>
        Devendra Ramanuj<br>
        📱 9276505035
    </div>
    """, unsafe_allow_html=True)

# --- 4. Main Title ---
st.title("Dev Bot")
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
        {"role": "assistant", "content": "Hello! I am Dev Bot. How can I help you? (તમે ગુજરાતીમાં વાત કરી શકો છો.)"}
    ]

# મેસેજ બતાવો
for message in st.session_state.messages:
    avatar = "🤖" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# ઇનપુટ બોક્સ
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
