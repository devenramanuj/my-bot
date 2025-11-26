import streamlit as st
import io
import pytz
from datetime import datetime
import re

# --- Crash-proof langdetect import ---
try:
    from langdetect import detect
except ImportError:
    detect = lambda x: 'en'  # fallback

# --- Lazy imports for heavy packages ---
lazy_imports_done = False
def lazy_imports():
    global lazy_imports_done, genai, Image, PyPDF2, gTTS, DDGS
    if not lazy_imports_done:
        import google.generativeai as genai
        from PIL import Image
        import PyPDF2
        from gtts import gTTS
        from duckduckgo_search import DDGS
        lazy_imports_done = True

# --- 1. Page Config ---
st.set_page_config(page_title="DEV", page_icon="🤖", layout="centered")

# --- 2. Theme ---
if "theme" not in st.session_state:
    st.session_state.theme = False

def toggle_theme():
    st.session_state.theme = not st.session_state.theme

def get_theme_colors():
    if st.session_state.theme:
        return "#0E1117", "#FFFFFF", "#00C6FF"  # night
    else:
        return "#FFFFFF", "#000000", "#00008B"  # day

main_bg, text_color, title_color = get_theme_colors()

# --- 3. CSS Styling ---
st.markdown(f"""
<style>
.stApp {{ background-color: {main_bg} !important; color: {text_color} !important; }}
div[data-testid="stStatusWidget"], div[data-testid="stToolbar"], div[data-testid="stDecoration"], header, footer, #MainMenu {{ visibility: hidden; display: none; }}
h1 {{ font-family: 'Orbitron', sans-serif !important; color: {title_color} !important; text-align:center; font-size:3rem !important; margin-top:10px; }}
.block-container {{ padding-top: 2rem !important; padding-bottom: 140px !important; }}
textarea, input[type="text"] {{ background-color: {main_bg} !important; color: {text_color} !important; border: 1px solid {text_color} !important; border-radius:8px; padding:6px; }}
button[data-testid="stChatInputSubmitButton"] {{ background-color: {title_color} !important; color:{text_color} !important; border-radius:8px; border:none !important; }}
</style>
""", unsafe_allow_html=True)

# --- 4. Header ---
st.markdown(f"""
<h1 style='display:flex; align-items:center; justify-content:center; gap:15px;'>
<img src="https://cdn-icons-png.flaticon.com/512/2040/2040946.png" width="50" height="50">
DEV
</h1>
<div style='text-align:center; color:{text_color}; font-size:13px; margin-bottom:10px; opacity:0.9;'>
Developed by <b>Devendra Ramanuj</b> | 📱 9276505035
</div>
""", unsafe_allow_html=True)
st.write("---")

# --- 5. Settings / Files ---
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

# --- 6. Chat state ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role":"assistant","content":"જયશ્રી કૃષ્ણ! 🙏 હું DEV છું, આપના પરિવારનો સભ્ય."}]

for message in st.session_state.messages:
    avatar = "🤖" if message["role"]=="assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
        if "audio_bytes" in message:
            st.audio(message["audio_bytes"], format="audio/mp3")

# --- 7. Input & live typing ---
typing_preview = st.empty()
user_input = st.text_area("Type your message here...", height=80)
if user_input:
    typing_preview.markdown(f"<div style='background-color:#f0f0f0; padding:8px; border-radius:6px; margin-bottom:5px; color:{text_color};'><b>Typing:</b> {user_input}</div>", unsafe_allow_html=True)
else:
    typing_preview.empty()

# --- 8. Submit processing ---
if st.button("Send") and user_input.strip():
    lazy_imports()  # heavy packages load only now

    # detect language
    try: user_lang = detect(user_input)
    except: user_lang='en'
    prompt_with_lang = f"તમે નીચેના પ્રશ્નનો જવાબ **ગુજરાતીમાં** આપો:\n{user_input}" if user_lang=='gu' else f"Answer the following question in **English**:\n{user_input}"

    # add user message
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
    st.session_state.messages.append({"role":"user","content":user_input})
    typing_preview.empty()
    user_input=""

    # assistant response
    try:
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("વિચારી રહ્યો છું..."):
                # configure model
                try:
                    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
                    genai.configure(api_key=GOOGLE_API_KEY)
                    sys_prompt = """તમારું નામ DEV છે. વપરાશકર્તાની ભાષા અનુસાર જવાબ આપો. """
                    model = genai.GenerativeModel('gemini-2.0-flash', system_instruction=sys_prompt)
                except:
                    st.error("Check API Key")
                    st.stop()

                # generate response
                chat_history = []
                for m in st.session_state.messages:
                    if m["role"]!="system" and "audio_bytes" not in m:
                        role = "model" if m["role"]=="assistant" else "user"
                        chat_history.append({"role":role,"parts":[m["content"]]})
                chat_history.append({"role":"user","parts":[prompt_with_lang]})
                response = model.generate_content(chat_history)
                response_text = response.text
                st.markdown(response_text)

                # TTS
                try:
                    clean_text = re.sub(r'[*#_`~]', '', response_text).strip()
                    if clean_text:
                        tts = gTTS(text=clean_text, lang='gu' if user_lang=='gu' else 'en')
                        audio_bytes = io.BytesIO()
                        tts.write_to_fp(audio_bytes)
                        audio_bytes.seek(0)
                        st.audio(audio_bytes, format="audio/mp3")
                        st.session_state.messages.append({"role":"assistant","content":response_text,"audio_bytes":audio_bytes})
                    else:
                        st.session_state.messages.append({"role":"assistant","content":response_text})
                except:
                    st.session_state.messages.append({"role":"assistant","content":response_text})

    except Exception as e:
        st.error(f"Error: {e}")
