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

# --- 2. CSS Styling (PREMIUM DARK MODE) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap');

    /* 1. Main Background (Dark) */
    .stApp {
        background-color: #0E1117 !important;
        color: #FFFFFF !important;
    }
    
    /* 2. All Text Colors (White) */
    p, div, span, li, label, h1, h2, h3, h4, h5, h6, .stMarkdown, .stCaption {
        color: #FFFFFF !important;
    }

    /* 3. SETTINGS MENU STYLING (Thin Border) */
    div[data-testid="stPopoverBody"] {
        background-color: #1E1E1E !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important; /* આછી બોર્ડર */
        border-radius: 10px;
    }
    div[data-testid="stPopoverBody"] * {
        color: #FFFFFF !important;
    }

    /* 4. INPUT BOX STYLING (White Text + Thin Border) */
    .stChatInput {
        position: fixed !important;
        bottom: 0px !important;
        left: 0px !important;
        right: 0px !important;
        padding-bottom: 15px !important;
        padding-top: 15px !important;
        background-color: #0E1117 !important;
        z-index: 999999 !important;
        border-top: 1px solid rgba(255, 255, 255, 0.2); /* ઉપર આછી લાઈન */
    }
    
    /* અંદરનું બોક્સ */
    .stChatInput textarea {
        background-color: #1E1E1E !important;
        color: #FFFFFF !important; /* લખેલું સફેદ દેખાશે */
        border: 1px solid rgba(255, 255, 255, 0.3) !important; /* પાતળી બોર્ડર */
        border-radius: 10px !important;
    }
    
    /* Placeholder (દેવને પૂછો...) */
    .stChatInput textarea::placeholder {
        color: rgba(255, 255, 255, 0.6) !important; /* થોડું આછું સફેદ */
    }

    /* Hide Extra Elements */
    header, footer, #MainMenu, div[data-testid="stStatusWidget"], .stDeployButton {
        display: none !important;
        visibility: hidden !important;
    }

    /* Title Font */
    h1 {
        font-family: 'Orbitron', sans-serif !important;
        color: #00C6FF !important; /* Neon Blue Title */
        text-align: center;
        font-size: 3rem !important;
        margin-top: 10px;
    }

    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 130px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Layout ---
st.markdown("""
    <h1 style='display: flex; align-items: center; justify-content: center; gap: 15px;'>
        <img src="https://cdn-icons-png.flaticon.com/512/2040/2040946.png" width="50" height="50" style="vertical-align: middle;">
        DEV
    </h1>
    <div style='text-align: center; color: #FFFFFF; font-size: 13px; margin-bottom: 10px; opacity: 0.7;'>
        Developed by <b>Devendra Ramanuj</b> | 📱 9276505035
    </div>
    """, unsafe_allow_html=True)

st.write("---")

# --- 4. Settings Menu ---
web_search = False

col1, col2 = st.columns([6, 1]) 

with col2:
    # નાનું બટન
    with st.popover("⚙️", use_container_width=True):
        st.write("###### 🌍 Internet")
        web_search = st.toggle("Live Search")
        
        st.divider()
        st.write("###### 📂 Files")
        uploaded_file = st.file_uploader("Upload", type=["jpg", "pdf"])
        
        st.divider()
        if st.button("🗑️ Reset"):
            st.session_state.messages = []
            st.rerun()

# --- 5. API Setup ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
    
    sys_prompt = """
    તારું નામ DEV (દેવ) છે. 
    તું દેવેન્દ્રભાઈ રામાનુજ દ્વારા બનાવાયેલો પરિવારનો એક સભ્ય છે.
    તારે હંમેશા ગુજરાતીમાં જ વાત કરવાની છે.
    """
    model = genai.GenerativeModel('gemini-2.0-flash', system_instruction=sys_prompt)
except:
    st.error("Error: Please check API Key.")
    st.stop()

# --- 6. Functions ---
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

# --- 7. Chat Logic ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "જયશ્રી કૃષ્ણ! 🙏 હું DEV છું. બોલો!"}
    ]

for message in st.session_state.messages:
    avatar = "🤖" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
        if "audio_bytes" in message:
            st.audio(message["audio_bytes"], format="audio/mp3")

# --- 8. Input Processing ---
if user_input := st.chat_input("દેવને પૂછો, અથવા કીબોર્ડનુ માઈક વાપરો."):
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking..."):
                response_text = ""
                
                # Logic
                if web_search:
                    current_time = get_current_time()
                    st.toast(f"Searching Web... 🌍")
                    search_results = search_internet(user_input)
                    prompt = f"Time: {current_time}\nInfo: {search_results}\nQuestion: {user_input}\nAnswer in Gujarati politely."
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
                    response = chat.send_message(user_input)
                    response_text = response.text

                st.markdown(response_text)
                
                # Voice
                try:
                    clean_voice_text = clean_text_for_audio(response_text)
                    if clean_voice_text:
                        tts = gTTS(text=clean_voice_text, lang='gu') 
                        audio_bytes = io.BytesIO()
                        tts.write_to_fp(audio_bytes)
                        audio_bytes.seek(0)
                        st.audio(audio_bytes, format="audio/mp3")
                        st.session_state.messages.append({"role": "assistant", "content": response_text, "audio_bytes": audio_bytes})
                    else:
                        st.session_state.messages.append({"role": "assistant", "content": response_text})
                except:
                    st.session_state.messages.append({"role": "assistant", "content": response_text})

    except Exception as e:
        st.error(f"Error: {e}")
