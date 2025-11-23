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
    st.error("API Key મળી નથી. કૃપા કરીને Streamlit Secrets ચેક કરો.")
    st.stop()

# --- Model Setup (તમારા લિસ્ટમાંથી લીધેલું પાકું મોડેલ) ---
try:
    # આ મોડેલ તમારા લિસ્ટમાં ઉપલબ્ધ છે અને ફ્રી છે
    model = genai.GenerativeModel('gemini-2.0-flash')
except Exception as e:
    st.error(f"મોડેલ લોડ કરવામાં ભૂલ: {e}")
    st.stop()

# --- Chat History & Logic ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "નમસ્તે! હું તૈયાર છું. તમે કેમ છો?"}]

# જૂની ચેટ બતાવો
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# નવો મેસેજ
if user_input := st.chat_input("અહીં લખો..."):
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        # મેસેજ મોકલો
        chat_history = []
        for m in st.session_state.messages:
            if m["role"] != "system":
                role = "model" if m["role"] == "assistant" else "user"
                chat_history.append({"role": role, "parts": [m["content"]]})

        response = model.generate_content(chat_history)
        
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

    except Exception as e:
        # જો કોઈ કારણસર 2.0-flash ન ચાલે તો Error બતાવશે
        st.error(f"ક્ષમા કરશો. (Error: {e})")
