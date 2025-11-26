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

# ---------------------------------------------------------------
# 1. PAGE CONFIG
# ---------------------------------------------------------------
st.set_page_config(page_title="DEV", page_icon="🤖", layout="centered")

# ---------------------------------------------------------------
# 2. THEME STATE
# ---------------------------------------------------------------
if "theme" not in st.session_state:
    st.session_state.theme = False

def toggle_theme():
    st.session_state.theme = not st.session_state.theme

if st.session_state.theme:
    main_bg = "#0E1117"
    text_color = "#FFFFFF"
    title_color = "#00C6FF"
else:
    main_bg = "#FFFFFF"
    text_color = "#000000"
    title_color = "#00008B"

# ---------------------------------------------------------------
# 3. CSS (LOGO + MENU + FOOTER REMOVE + UI CLEAN)
# ---------------------------------------------------------------
st.markdown(f"""
<style>
/* Background + Text */
.stApp {{
    background-color: {main_bg} !important;
    color: {text_color} !important;
}}
p, div, span, li, label, h1, h2, h3, h4, h5, h6 {{
    color: {text_color} !important;
}}

/* STREAMLIT LOGO + GITHUB ICON REMOVE */
a[data-testid="stAppGithubIcon"] {{ display: none !important; }}
img[alt="Streamlit"] {{ display: none !important; }}
#MainMenu {{ visibility: hidden; }}
header {{ visibility: hidden; }}
footer {{ visibility: hidden; }}

/* Bottom Chat Box */
[data-testid="stBottom"] {{
    background-color: {main_bg} !important;
    padding-top: 15px !important;
    padding-bottom: 15px !important;
    z-index: 99999 !important;
}}

.stChatInput {{
    background: transparent !important;
    border-top: 1px solid {text_color} !important;
}}

button[data-testid="stChatInputSubmitButton"] {{
    background: transparent !important;
    border: none !important;
    z-index: 999999 !important;
}}

/* Title */
h1 {{
    font-family: Arial Black !important;
    color: {title_color} !important;
    text-align: center;
    font-size: 3rem !important;
}}

/* Page spacing */
.block-container {{
    padding-bottom: 120px !important;
}}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------
# 4. HEADER
# ---------------------------------------------------------------
st.markdown(f"""
<h1>DEV</h1>
<div style='text-align:center; font-size:13px; opacity:0.9;'>
Developed by <b>Devendra Ramanuj</b> | 9276505035
</div>
""", unsafe_allow_html=True)

st.write("---")

# ---------------------------------------------------------------
# 5. SETTINGS MENU
# ---------------------------------------------------------------
web_search = False

with st.expander("⚙️"):
    col1, col2 = st.columns(2)
    with col1:
        st.write("###### Theme")
        st.toggle("Dark Mode", value=st.session_state.theme, on_change=toggle_theme)

    with col2:
        st.write("###### Internet")
        web_search = st.toggle("Live Search")

    st.divider()
    uploaded_file = st.file_uploader("Upload File", type=["jpg", "png", "pdf"])
    st.divider()

    if st.button("🗑 Reset Chat"):
        st.session_state.messages = []
        st.rerun()

# ---------------------------------------------------------------
# 6. API KEY
# ---------------------------------------------------------------
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)

    sys_prompt = """
    તારું નામ DEV છે.
    તારે હંમેશા ગુજરાતીમાં જ વાત કરવી.
    """
    model = genai.GenerativeModel('gemini-2.0-flash', system_instruction=sys_prompt)

except:
    st.error("Error: API Key Missing.")
    st.stop()

# ---------------------------------------------------------------
# 7. SMALL FUNCTIONS
# ---------------------------------------------------------------
def get_current_time():
    IST = pytz.timezone('Asia/Kolkata')
    return datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S %p")

def search_internet(query):
    try:
        results = DDGS().text(query, max_results=3)
        return "\n".join([f"- {r['body']}" for r in results])
    except:
        return "No results found."

def clean_text(text):
    return re.sub(r'[*#_`~]', '', text).strip()

# ---------------------------------------------------------------
# 8. INITIAL MESSAGE
# ---------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "જયશ્રી કૃષ્ણ! હું DEV છું."}
    ]

# ---------------------------------------------------------------
# 9. LOAD CHAT HISTORY
# ---------------------------------------------------------------
for m in st.session_state.messages:
    avatar = "🤖" if m["role"] == "assistant" else "👤"
    with st.chat_message(m["role"], avatar=avatar):
        st.markdown(m["content"])
        if "audio" in m:
            st.audio(m["audio"], format="audio/mp3")

# ---------------------------------------------------------------
# 10. CHAT INPUT
# ---------------------------------------------------------------
if user_input := st.chat_input("Ask DEV..."):
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("વિચારી રહ્યો છું..."):

            response_text = ""

            # Internet
            if web_search:
                info = search_internet(user_input)
                prompt = f"Time: {get_current_time()}\nInfo:\n{info}\nUser: {user_input}"
                response_text = model.generate_content(prompt).text

            # Image
            elif uploaded_file and uploaded_file.name.endswith(('.jpg', '.png')):
                img = Image.open(uploaded_file)
                response_text = model.generate_content([user_input, img]).text

            # PDF
            elif uploaded_file and uploaded_file.name.endswith('.pdf'):
                pdf = PyPDF2.PdfReader(uploaded_file)
                pdf_text = "".join([p.extract_text() for p in pdf.pages])
                response_text = model.generate_content(f"PDF: {pdf_text}\nQ: {user_input}").text

            # Normal chat
            else:
                prompt = f"Time: {get_current_time()}\nUser: {user_input}"
                response_text = model.generate_content(prompt).text

            st.markdown(response_text)

            # Voice Output
            try:
                tts = gTTS(text=clean_text(response_text), lang="gu")
                audio_bytes = io.BytesIO()
                tts.write_to_fp(audio_bytes)
                audio_bytes.seek(0)
                st.audio(audio_bytes)
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
