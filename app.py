import streamlit as st
import google.generativeai as genai

# --- 1. Page Config ---
st.set_page_config(
    page_title="Dev Bot",
    page_icon="🤖",
    layout="centered"
)

# --- 2. CSS Magic (Input Box ને ઉપર લેવા માટે) ---
st.markdown("""
    <style>
    /* 1. બેકગ્રાઉન્ડ */
    .stApp {
        background-color: #f0f2f6;
    }

    /* 2. ફૂટર અને હેડર ગાયબ */
    [data-testid="stToolbar"], 
    [data-testid="stDecoration"], 
    footer {
        visibility: hidden !important;
        display: none !important;
    }

    /* 3. ચેટ બોક્સનું સેટિંગ (આ મહત્વનું છે) */
    .stChatInput {
        position: fixed;
        bottom: 50px !important; /* બોક્સને 50px ઉપર ખેંચ્યું */
        z-index: 10000 !important; /* સૌથી ઉપર દેખાય */
        background-color: #f0f2f6; /* પાછળનું ઢાંકવા માટે */
        padding-bottom: 20px;
    }
    
    /* 4. ચેટ બોક્સની નીચે ખાલી જગ્યા મુકો (Safety Margin) */
    .stMain {
        padding-bottom: 100px; 
    }

    /* 5. ટાઈટલ */
    h1 {
        color: #1f618d;
        text-align: center;
        font-family: sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Sidebar ---
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

# --- 4. Content ---
st.title("Dev Bot")
st.caption("Emotional AI Companion (Gujarati / English)")

try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
except:
    st.error("Error: Please check API Key.")
    st.stop()

# --- 5. Chat ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am Dev Bot. (ગુજરાતીમાં વાત કરવા માટે તૈયાર છું.)"}
    ]

for message in st.session_state.messages:
    avatar = "🤖" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# --- 6. Input & Response ---
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
