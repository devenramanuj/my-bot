import streamlit as st
import google.generativeai as genai

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="Dev Bot",
    page_icon="🤖",
    layout="centered"
)

# --- 2. Custom CSS (Mobile Friendly) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #f0f2f6;
    }
    h1 {
        color: #1f618d;
        text-align: center;
        font-family: sans-serif;
    }
    /* મોબાઈલમાં મેનુ આઈકન માટે */
    .st-emotion-cache-16txtl3 {
        padding-top: 2rem; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Sidebar (મેનુ અને ડેવલપર નામ) ---
with st.sidebar:
    st.title("Settings")
    
    # વાતચીત ડિલીટ બટન
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    
    # --- Developer Credit ---
    st.markdown("""
    <div style='text-align: center; color: grey;'>
        <b>Developed by:</b><br>
        Devendra Ramanuj<br>
        📱 9276505035
    </div>
    """, unsafe_allow_html=True)

# --- 4. Main Title (ફક્ત અંગ્રેજી નામ, કોઈ આઈકન નહીં) ---
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
        {"role": "assistant", "content": "Hello! I am Dev Bot. How can I help you today? (તમે ગુજરાતીમાં પણ પૂછી શકો છો.)"}
    ]

# મેસેજ બતાવો
for message in st.session_state.messages:
    # બોટ માટે રોબોટ, યુઝર માટે માણસ
    avatar = "🤖" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# ઇનપુટ બોક્સ
if user_input := st.chat_input("Message Dev Bot..."):
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        # History
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
        st.error("Connection Error. Please try again.")
