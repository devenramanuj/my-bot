import streamlit as st
import google.generativeai as genai

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="Dev Bot",
    page_icon="🤖",
    layout="centered"
)

# --- 2. Custom CSS & Footer (તમારા નામ સાથે) ---
st.markdown("""
    <style>
    /* એપનું બેકગ્રાઉન્ડ */
    .stApp {
        background-color: #f0f2f6;
    }
    
    /* ટાઈટલનું સેટિંગ */
    h1 {
        color: #1f618d;
        text-align: center;
        font-family: sans-serif;
    }
    
    /* નીચેનું ફુટર (Footer) */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #2c3e50;
        color: white;
        text-align: center;
        padding: 10px;
        font-size: 14px;
        font-weight: bold;
        z-index: 999;
    }
    
    /* મેઈન કન્ટેન્ટ ફુટર પાછળ ન દબાય તે માટે */
    .block-container {
        padding-bottom: 80px;
    }
    </style>
    
    <div class="footer">
        Developed by Devendra Ramanuj | 📱 9276505035
    </div>
    """, unsafe_allow_html=True)

# --- 3. Sidebar (મેનુ) ---
with st.sidebar:
    st.title("⚙️ સેટિંગ્સ")
    st.info("દેવ બોટ: તમારો લાગણીશીલ સાથી.")
    
    # ક્લિયર ચેટ બટન
    if st.button("🗑️ નવી વાતચીત (Clear Chat)"):
        st.session_state.messages = []
        st.rerun()

# --- 4. Main Title ---
st.title("🤖 દેવ બોટ")
st.caption("હું તમારી લાગણીઓ સમજું છું. ગુજરાતી અથવા English માં વાત કરો.")

# --- 5. API Setup ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
except Exception as e:
    st.error("Error: API Key અથવા Model માં ભૂલ છે.")
    st.stop()

# --- 6. Chat Logic ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "નમસ્તે! હું છું દેવ બોટ. આજે હું તમારી શું મદદ કરી શકું?"}
    ]

# મેસેજ બતાવો
for message in st.session_state.messages:
    avatar = "🤖" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# ઇનપુટ અને જવાબ
if user_input := st.chat_input("અહીં લખો..."):
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        # હિસ્ટ્રી તૈયાર કરવી
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
        st.error("કનેક્શન એરર. ફરી પ્રયત્ન કરો.")
