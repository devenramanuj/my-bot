import streamlit as st
import google.generativeai as genai
from PIL import Image
import PyPDF2
from gtts import gTTS
import io
from duckduckgo_search import DDGS
from datetime import datetime
import pytz
import re

# --- 1. Page Config ---
st.set_page_config(page_title="DEV", page_icon="🤖", layout="centered")

# --- 2. Theme Logic ---
if "theme" not in st.session_state:
    st.session_state.theme = False

def toggle_theme():
    st.session_state.theme = not st.session_state.theme

if st.session_state.theme:
    # 🌙 Night Mode
    main_bg = "#0E1117"
    text_color = "#FFFFFF"
    title_color = "#00C6FF"
else:
    # ☀️ Day Mode
    main_bg = "#FFFFFF"
    text_color = "#000000"
    title_color = "#00008B"

# --- 3. CSS Styling ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap');

    .stApp {{
        background-color: {main_bg} !important;
        color: {text_color} !important;
    }}
    
    p, div, span, li, label, h1, h2, h3, h4, h5, h6, .stMarkdown {{
        color: {text_color} !important;
    }}

    /* 🛑 1. MANAGE APP BUTTON REMOVER (આ કોડ તેને છુપાવશે) */
    div[data-testid="stStatusWidget"], 
    div[data-testid="stToolbar"], 
    header, footer, #MainMenu, .stDeployButton {{
        visibility: hidden !important;
        display: none !important;
    }}

    /* 🛑 2. WHATSAPP STYLE INPUT (Bottom Fixed) */
    .stChatInput {{
        position: fixed !important;
        bottom: 0px !important;
        left: 0px !important;
        right: 0px !important;
        padding-bottom: 15px !important;
        padding-top: 15px !important;
        background-color: {main_bg} !important;
        z-index: 999999 !important;
        border-top: 1px solid {text_color};
    }}

    /* Settings Menu */
    .streamlit-expanderContent {{
        background-color: #FFFFFF !important;
        border: 1px solid #000000 !important;
        border-radius: 10px;
    }}
    .streamlit-expanderContent * {{
        color: #000000 !important;
    }}

    h1 {{
        font-family: 'Orbitron', sans-serif !important;
        color: {title_color} !important;
        text-align: center;
        font-size: 3rem !important;
        margin-top: 10px;
    }}

    .block-container {{
        padding-top: 2rem !important;
        padding-bottom: 130px !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. Layout ---
st.markdown(f"""
    <h1 style='display: flex; align-items: center; justify-content: center; gap: 15px;'>
        <img src="https://cdn-icons-png.flaticon.com/512/2040/2040946.png" width="50" height="50" style="vertical-align: middle;">
        DEV
    </h1>
    <div style='text-align: center; color: {text_color}; font-size: 13px; margin-bottom: 10px; opacity: 0.9;'>
        Developed by <b>Devendra Ramanuj</b> | 📱 9276505035
    </div>
    """, unsafe_allow_html=True)

st.write("---")

# --- 5. Settings Menu ---
web_search = False

with st.expander("⚙️"):
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("###### 🎨 Theme")
        st.toggle("🌗 Mode", value=st.session_state.theme, on_change=toggle_theme)
    with col_b:
        st.write("###### 🌍 Internet")
        web_search = st.toggle("Live Search")
    
    st.divider()
    st.write("###### 📂 Files")
    uploaded_file = st.file_uploader("Upload", type=["jpg", "pdf"])
    
    st.divider()
    if st.button("🗑️ Reset Chat"):
        st.session_state.messages = []
        st.rerun()

# --- 6. API Setup ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
    
    sys_prompt = """
    તારું નામ DEV (દેવ) છે. 
    તું દેવેન્દ્રભાઈ રામાનુજ દ્વારા બનાવાયેલો પરિવારનો એક સભ્ય છે.
    તારે હંમેશા ગુજરાતીમાં જ વાત કરવાની છે.
    તારે કોઈપણ પ્રશ્નનો જવાબ ટૂંકમાં નથી આપવાનો, પણ **વિસ્તૃત (Detailed)** સમજાવીને આપવાનો છે.
    """
    model = genai.GenerativeModel('gemini-2.0-flash', system_instruction=sys_prompt)
except:
    st.error("Error: Please check API Key.")
    st.stop()

# --- 7. Functions ---
def get_current_time():
    IST = pytz.timezone('Asia/Kolkata')
    now = datetime.now(IST)
    return now.strftime("%Y-%m-%d %H:%M:%S %p")

def search_internet(query):
    try:
        results = DDGS().text(query, max_results=3)
        if results:
            return "\n".join([f"- {r['body']}" for r in results])
        return "No results found."
    except Exception as e:
        return f"Search Error: {e}"

def clean_text_for_audio(text):
    clean = re.sub(r'[*#_`~]', '', text)
    return clean.strip()

# --- 8. Chat Logic ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "જયશ્રી કૃષ્ણ! 🙏 હું DEV છું."}
    ]

for message in st.session_state.messages:
    avatar = "🤖" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
        if "audio_bytes" in message: # ફિક્સ કરેલું નામ
            st.audio(message["audio_bytes"], format="audio/mp3")

# --- 9. Input Processing ---
if user_input := st.chat_input("Ask DEV... (કી-બોર્ડનું માઈક 🎙️ વાપરો)"):
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("વિચારી રહ્યો છું..."):
                response_text = ""
                
                # Logic
                if web_search:
                    current_time = get_current_time()
                    st.toast(f"Searching Web... 🌍")
                    search_results = search_internet(user_input)
                    prompt = f"Time: {current_time}\nInfo: {search_results}\nQuestion: {user_input}\nAnswer in Gujarati in detail."
                    response = model.generate_content(prompt)
                    response_text = response.text
                elif uploaded_file is not None and uploaded_file.name.endswith(('.jpg', '.png', '.jpeg')):
                    image = Image.open(uploaded_file)
                    response = model.generate_content([user_input, image])
                    response_text = response.text
                elif uploaded_file is not None and uploaded_file.name.endswith('.pdf'):
                    pdf_reader = PyPDF2.PdfReader(uploaded_file)
                    pdf_text = ""
                    for page in pdf_reader.pages:
                        pdf_text += page.extract_text()
                    prompt = f"PDF Context: {pdf_text}\n\nQuestion: {user_input}\nAnswer in detail."
                    response = model.generate_content(prompt)
                    response_text = response.text
                else:
                    chat_history = []
                    for m in st.session_state.messages:
                        if m["role"] != "system" and "audio_bytes" not in m:
                            role = "model" if m["role"] == "assistant" else "user"
                            if m["content"] != user_input: 
                                chat_history.append({"role": role, "parts": [m["content"]]})
                    
                    chat = model.start_chat(history=chat_history)
                    response = chat.send_message(user_input + " (વિસ્તારથી સમજાવ)")
                    response_text = response.text

                st.markdown(response_text)
                
                # Voice (Fixed with Bytes)
                try:
                    clean_voice_text = clean_text_for_audio(response_text)
                    if clean_voice_text:
                        tts = gTTS(text=clean_voice_text, lang='gu') 
                        
                        # બફર બનાવો
                        audio_buffer = io.BytesIO()
                        tts.write_to_fp(audio_buffer)
                        # બાઈટ્સ મેળવો (આ ક્યારેય ડિલીટ ન થાય)
                        audio_data = audio_buffer.getvalue()
                        
                        st.audio(audio_data, format="audio/mp3")
                        st.session_state.messages.append({"role": "assistant", "content": response_text, "audio_bytes": audio_data})
                    else:
                        st.session_state.messages.append({"role": "assistant", "content": response_text})
                except:
                    st.session_state.messages.append({"role": "assistant", "content": response_text})

    except Exception as e:
        st.error(f"Error: {e}")
