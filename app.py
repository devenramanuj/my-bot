import streamlit as st
import google.generativeai as genai

# --- Page Setup ---
st.set_page_config(page_title="My Gujarati AI Friend", page_icon="❤️")
st.title("❤️ મારો AI મિત્ર")
st.caption("હું તમારી લાગણીઓ સમજું છું. ગુજરાતી કે English માં વાત કરો.")

# --- API Key Setup ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
except:
    st.error("API Key Error: Please check Streamlit secrets.")
    st.stop()

# --- Model Setup (Standard Model) ---
# આપણે હવે 'gemini-pro' વાપરીશું જે સૌથી સ્ટેબલ છે.
model = genai.GenerativeModel('gemini-pro')

# --- Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    # સ્વાગત સંદેશ
    st.session_state.messages.append({"role": "assistant", "content": "નમસ્તે! કેમ છો? આજે તમારો મૂડ કેવો છે?"})

# --- Display History ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat Logic ---
if user_input := st.chat_input("અહીં લખો..."):
    # યુઝરનો મેસેજ
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # AI નો જવાબ
    try:
        # મેસેજ મોકલો (સરળ પદ્ધતિ)
        response = model.generate_content(user_input)
        ai_text = response.text
        
        with st.chat_message("assistant"):
            st.markdown(ai_text)
        st.session_state.messages.append({"role": "assistant", "content": ai_text})

    except Exception as e:
        st.error(f"Error: {e}")
