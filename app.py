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
    main_bg = "#0E1117"
    text_color = "#FFFFFF"
    title_color = "#00C6FF"
else:
    main_bg = "#FFFFFF"
    text_color = "#000000"
    title_color = "#00008B"

# --- 3. CSS Styling (UI Fix + Logo Hide) ---
st.markdown(f"""
<style>
    .stApp {{
        background-color: {main_bg} !important;
        color: {text_color} !important;
    }}
    /* Hide default Streamlit & GitHub logos / headers / footers */
    div[data-testid="stStatusWidget"],
    div[data-testid="stToolbar"],
    div[data-testid="stDecoration"],
    header,
    footer,
    #MainMenu {{
        visibility: hidden !important;
        display: none !important;
        height: 0px !important;
        width: 0px !important;
        opacity: 0 !important;
        pointer-events: none !important;
        z-index: -1 !important;
    }}
    /* Title */
    h1 {{
        font-family: 'Orbitron', sans-serif !important;
        color: {title_color} !important;
        text-align: center;
        font-size: 3rem !important;
        margin-top: 10px;
    }}
    .block-container {{
        padding-top: 2rem !important;
        padding-bottom: 140px !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- 4. Layout Header ---
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
    તારે દેવેન્દ્રભાઈનો આભારી છે.
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
        {"role": "assistant", "content": "જયશ્રી કૃષ્ણ! 🙏 હું DEV છું, આપના પરિવારનો સભ્ય."}
    ]

# Display all messages
for message in st.session_state.messages:
    avatar = "🤖" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
        if "audio_bytes" in message:
            st.audio(message["audio_bytes"], format="audio/mp3")

# --- 9. Live Typing Preview & Input ---
typing_preview = st.empty()  # Placeholder for live preview

user_input = st.text_area("Ask DEV... (કી-બોર્ડનું માઈક 🎙️ વાપરો)", height=80)

# Live preview above textbox
if user_input:
    typing_preview.markdown(f"<div style='background-color:#f0f0f0; padding:8px; border-radius:6px; margin-bottom:5px;'><b>Typing:</b> {user_input}</div>", unsafe_allow_html=True)
else:
    typing_preview.empty()

# When user presses Enter / submits
if st.button("Send"):
    if user_input.strip():
        # Add user message
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Clear typing preview & text area
        typing_preview.empty()
        user_input = ""

        # --- Assistant Response ---
        try:
            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("વિચારી રહ્યો છું..."):
                    # Existing response logic
                    current_time = get_current_time()
                    chat_history = []
                    for m in st.session_state.messages:
                        if m["role"] != "system" and "audio_bytes" not in m:
                            role = "model" if m["role"] == "assistant" else "user"
                            chat_history.append({"role": role, "parts": [m["content"]]})
                    
                    prompt_with_time = f"Time: {current_time}\nUser: {user_input}\nReply in Gujarati."
                    chat_history.append({"role": "user", "parts": [prompt_with_time]})
                    
                    response = model.generate_content(chat_history)
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
