import streamlit as st
import google.generativeai as genai
from PIL import Image
import PyPDF2
from gtts import gTTS
import io
from streamlit_mic_recorder import speech_to_text

# --- 1. Page Config ---
st.set_page_config(
    page_title="DEV",
    page_icon="🤖",
    layout="centered"
)

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
    popover_bg = "#1E1E1E" # મેનુનું બેકગ્રાઉન્ડ (Dark)
else:
    # ☀️ Day Mode
    main_bg = "#FFFFFF"
    text_color = "#000000"
    title_color = "#00008B"
    popover_bg = "#F0F2F6" # મેનુનું બેકગ્રાઉન્ડ (Light)

# --- 3. CSS Styling ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap');

    .stApp {{
        background-color: {main_bg} !important;
        color: {text_color} !important;
    }}

    /* સામાન્ય લખાણ */
    p, div, span, li, .stMarkdown, .stCaption, h3, label {{
        color: {text_color} !important;
    }}
    
    /* 🛑 POPOVER MENU COLOR FIX (આનાથી સેટિંગ્સ વંચાશે) */
    [data-testid="stPopoverBody"] {{
        background-color: {popover_bg} !important;
        border: 1px solid {text_color};
    }}
    
    h1 {{
        font-family: 'Orbitron', sans-serif !important;
        color: {title_color} !important;
        text-align: center;
        font-size: 3rem !important;
        letter-spacing: 3px;
        margin-top: 10px;
    }}
    
    /* માઈક બટન */
    .stButton button {{
        width: 100%;
        border-radius: 10px;
        font-weight: bold;
        border: 1px solid {text_color};
    }}

    /* બધું છુપાવો */
    [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], 
    [data-testid="stToolbar"], [data-testid="stDecoration"], footer, header {{
        display: none !important;
        visibility: hidden !important;
    }}

    .block-container {{
        padding-top: 2rem !important;
        padding-bottom: 5rem !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. Layout ---
st.markdown(f"""
    <h1 style='display: flex; align-items: center; justify-content: center; gap: 15px;'>
        <img src="https://cdn-icons-png.flaticon.com/512/2040/2040946.png" width="50" height="50" style="vertical-align: middle;">
        DEV
    </h1>
    """, unsafe_allow_html=True)

st.markdown(f"""
    <div style='text-align: center; color: {text_color}; font-size: 13px; margin-bottom: 10px; opacity: 0.9;'>
        Developed by <b>Devendra Ramanuj</b> | 📱 9276505035
    </div>
    """, unsafe_allow_html=True)

# --- 5. VOICE BUTTON & SETTINGS ---
st.write("---") 
col_mic, col_sets = st.columns([2, 1])

voice_input = None

with col_mic:
    # માઈક બટન
    text = speech_to_text(
        language='gu-IN',
        start_prompt="🎤 બોલવા માટે દબાવો",
        stop_prompt="⏹️ બંધ કરીને મોકલો",
        just_once=True,
        key='mic_main'
    )
    if text:
        voice_input = text

with col_sets:
    # સેટિંગ્સ મેનુ
    with st.popover("⚙️ સેટિંગ્સ"):
        st.write("###### 🎨 Theme")
        st.toggle("🌗 Mode", value=st.session_state.theme, on_change=toggle_theme)
        
        st.write("###### 📂 Files")
        uploaded_file = st.file_uploader("Upload", type=["jpg", "pdf"])
        
        if st.button("🗑️ Reset Chat"):
            st.session_state.messages = []
            st.rerun()

# --- 6. API Setup ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
except:
    st.error("Error: Please check API Key.")
    st.stop()

# --- 7. Chat Logic ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "જયશ્રી કૃષ્ણ! 🙏 હું DEV છું. બોલો અથવા લખો!"}
    ]

for message in st.session_state.messages:
    avatar = "🤖" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
        if "audio" in message:
            st.audio(message["audio"], format="audio/mp3")

# --- 8. INPUT HANDLING (Main Logic) ---

final_input = None

# Logic: જો માઈકમાંથી અવાજ આવ્યો હોય તો તેને વાપરો, નહિતર ટાઈપિંગ જુઓ
if voice_input:
    final_input = voice_input
elif chat_input := st.chat_input("Ask DEV..."):
    final_input = chat_input

# જો કોઈ પણ ઈનપુટ (અવાજ કે લખાણ) મળ્યું હોય તો જ આગળ વધો
if final_input:
    # યુઝરનો મેસેજ બતાવો
    with st.chat_message("user", avatar="👤"):
        st.markdown(final_input)
    st.session_state.messages.append({"role": "user", "content": final_input})

    # AI જવાબ આપે છે
    try:
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("વિચારી રહ્યો છું..."):
                response_text = ""
                
                # Image Logic
                if uploaded_file is not None and uploaded_file.name.endswith(('.jpg', '.png', '.jpeg')):
                    image = Image.open(uploaded_file)
                    response = model.generate_content([final_input, image])
                    response_text = response.text
                
                # PDF Logic
                elif uploaded_file is not None and uploaded_file.name.endswith('.pdf'):
                    pdf_reader = PyPDF2.PdfReader(uploaded_file)
                    pdf_text = ""
                    for page in pdf_reader.pages:
                        pdf_text += page.extract_text()
                    prompt = f"PDF Context:\n{pdf_text}\n\nQuestion: {final_input}"
                    response = model.generate_content(prompt)
                    response_text = response.text
                
                # Text Logic
                else:
                    chat_history = []
                    for m in st.session_state.messages:
                        if m["role"] != "system" and "audio" not in m:
                            role = "model" if m["role"] == "assistant" else "user"
                            chat_history.append({"role": role, "parts": [m["content"]]})
                    response = model.generate_content(chat_history)
                    response_text = response.text

                # ટેક્સ્ટ બતાવો
                st.markdown(response_text)
                
                # Voice Output (બોલવાનું)
                try:
                    tts = gTTS(text=response_text, lang='gu') 
                    audio_bytes = io.BytesIO()
                    tts.write_to_fp(audio_bytes)
                    audio_bytes.seek(0)
                    st.audio(audio_bytes, format="audio/mp3")
                    
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": response_text,
                        "audio": audio_bytes
                    })
                except:
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": response_text
                    })

    except Exception as e:
        st.error(f"Error: {e}")
