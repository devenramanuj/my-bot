import streamlit as st
import google.generativeai as genai

# --- 1. Page Configuration (પેજ સેટિંગ) ---
st.set_page_config(
    page_title="My Gujarati AI Friend",
    page_icon="❤️",
    layout="centered"
)

st.title("❤️ મારો AI મિત્ર")
st.caption("હું તમારી લાગણીઓ સમજું છું. મને ગુજરાતી અથવા English માં કઈ પણ પૂછો.")

# --- 2. API Key Setup (સિક્રેટ કી મેળવવી) ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
except Exception as e:
    st.error("ભૂલ: API Key મળી નથી. કૃપા કરીને Streamlit Settings > Secrets માં કી ચેક કરો.")
    st.stop()

# --- 3. Model Configuration (આ મોડેલ ફ્રી છે) ---
# અહીં આપણે 'gemini-1.5-flash' વાપરીશું જે ફ્રી અને ઝડપી છે.
model_name = "gemini-1.5-flash"

system_instruction = """
You are a deeply empathetic, sensitive, and caring AI companion. 
- Your goal is to connect emotionally with the user.
- If the user speaks Gujarati, reply in warm, natural Gujarati.
- If the user speaks English, reply in kind English.
- Always be supportive and validate their feelings.
"""

try:
    model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=system_instruction
    )
except Exception as e:
    st.error(f"મોડેલ લોડ કરવામાં તકલીફ છે: {e}")
    st.stop()

# --- 4. Chat History (વાતચીત યાદ રાખવી) ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "નમસ્તે! કેમ છો? આજે તમારો દિવસ કેવો રહ્યો?"}
    ]

# જૂની ચેટ સ્ક્રીન પર બતાવો
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. User Input & AI Response (વાતચીત શરૂ) ---
if user_input := st.chat_input("તમારા મનની વાત અહીં લખો..."):
    
    # 1. યુઝરનો મેસેજ બતાવો
    with st.chat_message("user"):
        st.markdown(user_input)
    # હિસ્ટ્રીમાં ઉમેરો
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 2. AI પાસે જવાબ માંગો
    try:
        # ગુગલને મોકલવા માટે હિસ્ટ્રી તૈયાર કરવી
        chat_history = []
        for m in st.session_state.messages:
            if m["role"] != "system": # સિસ્ટમ મેસેજ મોકલવાની જરૂર નથી
                # Streamlit માં 'assistant' હોય, પણ Google ને 'model' જોઈએ
                role = "model" if m["role"] == "assistant" else "user"
                chat_history.append({"role": role, "parts": [m["content"]]})

        # જવાબ જનરેટ કરો
        response = model.generate_content(chat_history)
        ai_response = response.text
        
        # 3. AI નો જવાબ બતાવો
        with st.chat_message("assistant"):
            st.markdown(ai_response)
        
        # હિસ્ટ્રીમાં ઉમેરો
        st.session_state.messages.append({"role": "assistant", "content": ai_response})

    except Exception as e:
        st.error(f"ક્ષમા કરશો, નાની ટેકનિકલ ભૂલ આવી છે. ફરી પ્રયત્ન કરો. \n(Error Detail: {e})")
