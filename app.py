import streamlit as st
import google.generativeai as genai
from PIL import Image
import PyPDF2
from gtts import gTTS # અવાજ માટે
import io

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
    main_bg = "#0E1117"
    text_color = "#FFFFFF"
    title_color = "#00C6FF"
else:
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

    p, div, span, li, .stMarkdown, .stCaption, h3, label {{
        color: {text_color} !important;
    }}
    
    h1 {{
        font-family: 'Orbitron', sans-serif !important;
        color: {title_color} !important;
        text-align: center;
        font-size: 3rem !important;
        letter-spacing: 3px;
        margin-top: -10px;
    }}

    /* Hide Elements */
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
    <div style='text-align: center; color: {text_color}; font-size: 13px; margin-bottom: 15px; opacity: 0.9;'>
        Developed by <b>Devendra Ramanuj</b> | 📱 9276505035
    </div>
    """, unsafe_allow_html=True)

# --- 5. MENU (Settings) ---
with st.expander("⚙️ સેટિંગ્સ (Settings)", expanded=False):
    st.write("###### 🎨 Theme")
    st.toggle("🌗 Day / Night Mode", value=st.session_state.theme, on_change=toggle_theme)
    
    st.divider()
    
    st.write("###### 📂 Upload File (Image / PDF)")
    uploaded_file = st.file_uploader("Choose file", type=["jpg", "png", "jpeg", "pdf"], label_visibility="collapsed")
    
    file_type = ""
    extracted_text = ""
    
    def get_pdf_text(pdf_file):
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text

    if uploaded_file is not None:
        if uploaded_file.name.endswith(".pdf"):
            file_type = "pdf"
            st.info("📄 PDF Detected")
            extracted_text = get_pdf_text(uploaded_file)
        else:
            file_type = "image"
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_container_width=True)

    st.divider()
    if st.button("🗑️ Clear Chat", use_container_width=True):
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
        {"role": "assistant", "content": "જયશ્રી કૃષ્ણ! 🙏 હું DEV છું. હવે હું બોલી પણ શકું છું!"}
    ]

for message in st.session_state.messages:
    avatar = "🤖" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
        
        # જો મેસેજમાં ઓડિયો હોય તો બતાવો
        if "audio" in message:
            st.audio(message["audio"], format="audio/mp3")

# --- 8. Input & Response ---
if user_input := st.chat_input("Ask DEV..."):
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("વિચારી રહ્યો છું..."):
                
                # AI જવાબ મેળવે છે
                response_text = ""
                if uploaded_file is not None and file_type == "image":
                    image = Image.open(uploaded_file)
                    response = model.generate_content([user_input, image])
                    response_text = response.text
                elif uploaded_file is not None and file_type == "pdf":
                    prompt = f"PDF: {extracted_text}\n\nQ: {user_input}"
                    response = model.generate_content(prompt)
                    response_text = response.text
                else:
                    chat_history = []
                    for m in st.session_state.messages:
                        if m["role"] != "system" and "audio" not in m: # ઓડિયો ડેટા ન મોકલાય
                            role = "model" if m["role"] == "assistant" else "user"
                            chat_history.append({"role": role, "parts": [m["content"]]})
                    response = model.generate_content(chat_history)
                    response_text = response.text

                # ટેક્સ્ટ બતાવો
                st.markdown(response_text)
                
                # --- VOICE GENERATION (અહીં અવાજ બને છે) ---
                # ગુજરાતી ભાષામાં બોલવા માટે 'gu'
                try:
                    tts = gTTS(text=response_text, lang='gu') 
                    audio_bytes = io.BytesIO()
                    tts.write_to_fp(audio_bytes)
                    audio_bytes.seek(0)
                    
                    st.audio(audio_bytes, format="audio/mp3")
                    
                    # મેસેજ સેવ કરો (ઓડિયો સાથે)
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": response_text,
                        "audio": audio_bytes # ઓડિયો સેવ કર્યો
                    })
                except:
                    # જો અવાજ ન બને તો માત્ર ટેક્સ્ટ સેવ કરો
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": response_text
                    })

    except Exception as e:
        st.error(f"Error: {e}")
