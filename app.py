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
import nest_asyncio
import edge_tts
import asyncio

# Asyncio Fix
nest_asyncio.apply()

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

    /* Hide Elements */
    header, footer, #MainMenu, div[data-testid="stStatusWidget"], .stDeployButton {{
        display: none !important;
        visibility: hidden !important;
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
        padding-bottom: 100px !important;
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

# --- 6. API Setup (અહીં સુધારો કર્યો છે) ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
    
    # 🛑 SYSTEM INSTRUCTION (આનાથી તેને યાદ રહેશે)
    sys_prompt = """
    તારું નામ DEV (દેવ) છે. 
    તું દેવેન્દ્ર રામાનુજ દ્વારા બનાવાયેલો એક સ્માર્ટ AI બોટ છે.
    તારે હંમેશા ગુજરાતીમાં જ જવાબ આપવાનો છે (સિવાય કે યુઝર બીજી ભાષા માંગે).
    તું ઈન્ટરનેટ પર સર્ચ કરી શકે છે, ફોટા જોઈ શકે છે અને PDF વાંચી શકે છે.
    તારો સ્વભાવ મદદગાર, વિવેકી અને જ્ઞાની છે.
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

async def generate_smart_audio(text, filename):
    try:
        voice = "gu-IN-NiranjanNeural" 
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(filename)
        return True
    except:
        return False

# --- 8. Chat Logic ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "જયશ્રી કૃષ્ણ! 🙏 હું DEV છું. બોલો!"}
    ]

for message in st.session_state.messages:
    avatar = "🤖" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
        if "audio_file" in message:
            st.audio(message["audio_file"], format="audio/mp3")
        elif "audio_bytes" in message:
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
                
                # 1. Internet
                if web_search:
                    current_time = get_current_time()
                    st.toast(f"Searching Web... 🌍")
                    search_results = search_internet(user_input)
                    prompt = f"Time: {current_time}\nInfo: {search_results}\nQuestion: {user_input}\nAnswer in Gujarati."
                    response = model.generate_content(prompt)
                    response_text = response.text

                # 2. Image
                elif uploaded_file is not None and uploaded_file.name.endswith(('.jpg', '.png', '.jpeg')):
                    image = Image.open(uploaded_file)
                    response = model.generate_content([user_input, image])
                    response_text = response.text
                
                # 3. PDF
                elif uploaded_file is not None and uploaded_file.name.endswith('.pdf'):
                    pdf_reader = PyPDF2.PdfReader(uploaded_file)
                    pdf_text = ""
                    for page in pdf_reader.pages:
                        pdf_text += page.extract_text()
                    prompt = f"PDF: {pdf_text}\nQuestion: {user_input}"
                    response = model.generate_content(prompt)
                    response_text = response.text
                
                # 4. Normal
                else:
                    current_time = get_current_time()
                    chat_history = []
                    for m in st.session_state.messages:
                        if m["role"] != "system" and "audio_file" not in m and "audio_bytes" not in m:
                            role = "model" if m["role"] == "assistant" else "user"
                            chat_history.append({"role": role, "parts": [m["content"]]})
                    
                    prompt_with_time = f"Time: {current_time}\nUser: {user_input}"
                    chat_history.append({"role": "user", "parts": [prompt_with_time]})
                    
                    response = model.generate_content(chat_history)
                    response_text = response.text

                st.markdown(response_text)
                
                # Voice Output
                clean_voice_text = clean_text_for_audio(response_text)
                if clean_voice_text:
                    audio_filename = f"audio_{len(st.session_state.messages)}.mp3"
                    success = asyncio.run(generate_smart_audio(clean_voice_text, audio_filename))
                    
                    if success:
                        st.audio(audio_filename, format="audio/mp3")
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": response_text, 
                            "audio_file": audio_filename
                        })
                    else:
                        # Fallback to gTTS
                        try:
                            tts = gTTS(text=clean_voice_text, lang='gu') 
                            audio_bytes = io.BytesIO()
                            tts.write_to_fp(audio_bytes)
                            audio_bytes.seek(0)
                            st.audio(audio_bytes, format="audio/mp3")
                            st.session_state.messages.append({"role": "assistant", "content": response_text, "audio_bytes": audio_bytes})
                        except:
                            st.session_state.messages.append({"role": "assistant", "content": response_text})
                else:
                    st.session_state.messages.append({"role": "assistant", "content": response_text})

    except Exception as e:
        st.error(f"Error: {e}")
