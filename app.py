import streamlit as st
import google.generativeai as genai

# પેજનું સેટિંગ
st.set_page_config(page_title="My Gujarati AI Friend", page_icon="❤️")

st.title("❤️ મારો AI મિત્ર")
st.caption("હું તમારી લાગણીઓ સમજું છું. ગુજરાતી કે English માં વાત કરો.")

# API Key સુરક્ષા માટે (Cloud માંથી લેશે)
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
except:
    st.error("API Key મળી નથી. કૃપા કરીને Streamlit Secrets માં કી સેટ કરો.")
    st.stop()

# AI નો સ્વભાવ (System Prompt)
system_instruction = """
You are a deeply empathetic and caring AI companion. 
- Respond with warmth.
- If user speaks Gujarati, reply in Gujarati.
- If user speaks English, reply in English.
"""

model = genai.GenerativeModel(
    model_name="gemini-pro",
    system_instruction=system_instruction
)

# વાતચીત યાદ રાખવા માટે
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "કેમ છો? આજે તમારો મૂડ કેવો છે?"}]

# જૂની ચેટ બતાવો
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# નવો મેસેજ હેન્ડલ કરો
if user_input := st.chat_input("અહીં લખો..."):
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        chat_history = [{"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages if m["role"] != "system"]
        response = model.generate_content(chat_history)
        
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
    except Exception as e:

        st.error(f"સાચી એરર આ છે: {e}")

