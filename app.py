import streamlit as st
import google.generativeai as genai

# --- 1. Page Configuration ---
st.set_page_config(page_title="My Gujarati AI Friend", page_icon="❤️")
st.title("❤️ મારો AI મિત્ર")
st.caption("હું તમારી લાગણીઓ સમજું છું. ગુજરાતી કે English માં વાત કરો.")

# --- 2. Setup API Key ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
except:
    st.error("API Key મળી નથી. કૃપા કરીને Streamlit Secrets માં કી સેટ કરો.")
    st.stop()

# --- 3. Smart Model Selection (આપોઆપ મોડેલ શોધશે) ---
model_name_to_use = ""

try:
    # Google ને પૂછો કે કયા મોડેલ ઉપલબ્ધ છે
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            if 'gemini' in m.name:
                model_name_to_use = m.name
                break # જેવું પહેલું મોડેલ મળે તે લઈ લો
except Exception as e:
    st.error(f"મોડેલ શોધવામાં ભૂલ: {e}")
    st.stop()

if model_name_to_use == "":
    st.error("તમારા એકાઉન્ટમાં કોઈ Gemini મોડેલ મળતું નથી. નવી API Key બનાવવી પડી શકે.")
    st.stop()

# (Debugging માટે - તમને દેખાશે કે કયું મોડેલ વપરાયું)
# st.success(f"Connected to: {model_name_to_use}")

# --- 4. Setup Chatbot ---
system_instruction = """
You are a deeply empathetic, sensitive, and caring AI companion. 
- Respond with warmth and understanding.
- If user speaks Gujarati, reply in Gujarati.
- If user speaks English, reply in English.
- Validate their feelings before giving advice.
"""

try:
    model = genai.GenerativeModel(
        model_name=model_name_to_use,
        system_instruction=system_instruction
    )
except:
    # જો System Instruction સપોર્ટ ન કરે તો સાદું મોડેલ
    model = genai.GenerativeModel(model_name=model_name_to_use)

# --- 5. Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "નમસ્તે! આજે તમારો મૂડ કેવો છે? હું તમારી વાત સાંભળવા અહીં જ છું."}]

# જૂની વાતચીત બતાવો
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 6. User Input & Response ---
if user_input := st.chat_input("અહીં લખો..."):
    # યુઝરનો મેસેજ
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # AI નો જવાબ
    try:
        # History તૈયાર કરો
        chat_history = []
        for m in st.session_state.messages:
            if m["role"] != "system":
                chat_history.append({"role": m["role"], "parts": [m["content"]]})

        # જવાબ જનરેટ કરો
        response = model.generate_content(chat_history)
        ai_text = response.text
        
        with st.chat_message("assistant"):
            st.markdown(ai_text)
        st.session_state.messages.append({"role": "assistant", "content": ai_text})

    except Exception as e:
        st.error(f"ફરીથી ભૂલ આવી: {e}")
