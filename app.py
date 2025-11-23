import streamlit as st
import google.generativeai as genai
from PIL import Image
import PyPDF2

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

# --- 3. CSS Styling (Menu Fix) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap');

    .stApp {{
        background-color: {main_bg} !important;
        color: {text_color} !important;
    }}

    p, div, span, li, .stMarkdown, .stCaption, h3 {{
        color: {text_color} !important;
    }}
    
    h1 {{
        font-family: 'Orbitron', sans-serif !important;
        color: {title_color} !important;
        text-align: center;
        font-size: 3rem !important;
        letter-spacing: 3px;
        margin-top: 10px; /* થોડી જગ્યા આપી જેથી મેનુ બટન નડે નહીં */
    }}

    /* -------------------------------------------------- */
    /* 🛑 MENU BUTTON FIX (આ મહત્વનું છે)               */
    /* -------------------------------------------------- */
    [data-testid="stSidebarCollapsedControl"] {{
        display: block !important;
        visibility: visible !important;
        position: fixed !important; /* આને ફિક્સ કરી દીધું */
        top: 15px !important;
        left: 15px !important;
        z-index: 1000000 !important; /* સૌથી ઉપર */
        color: {text_color} !important;
        background-color: rgba(128, 128, 128, 0.2); /* થોડું બેકગ્રાઉન્ડ */
        padding: 5px;
        border-radius: 5px;
    }}
    
    /* Hide Streamlit Elements */
    [data-testid="stToolbar"], [data-testid="stDecoration"], footer, header {{
        visibility: hidden !important;
        display: none !important;
    }}

    .block-container {{
        padding-top: 3rem !important; /* ટાઈટલ અને મેનુ માટે જગ્યા */
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
    <div style='text-align: center; color: {text_color}; font-size: 13px; margin-bottom: 5px; opacity: 0.9;'>
        Developed by <b>Devendra Ramanuj</b> | 📱 9276505035
    </div>
    """, unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    mode = st.toggle("🌗 Day / Night Mode", value=st.session_state.theme, on_change=toggle_theme)

# --- 5. Logic Functions ---
def get_pdf_text(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# --- 6. Sidebar ---
with st.sidebar:
    st.title("Settings")
    st.markdown("### 📂 Upload File")
    uploaded_file = st.file_uploader("Upload Image or PDF", type=["jpg", "png", "jpeg", "pdf"])
    
    file_type = ""
    extracted_text = ""
    
    if uploaded_file is not None:
        if uploaded_file.name.endswith(".pdf"):
            file_type = "pdf"
            st.info("📄 PDF File Detected")
            with st.spinner("Reading PDF..."):
                extracted_text = get_pdf_text(uploaded_file)
                st.success("PDF Loaded!")
        else:
            file_type = "image"
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_container_width=True)

    st.divider()
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- 7. API Setup ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
except:
    st.error("Error: Please check API Key.")
    st.stop()

# --- 8. Chat Logic ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "જયશ્રી કૃષ્ણ! 🙏 હું DEV છું. (Image & PDF supported)."}
    ]

for message in st.session_state.messages:
    avatar = "🤖" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# --- 9. Input & Processing ---
if user_input := st.chat_input("Ask DEV..."):
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking..."):
                response_text = ""
                if uploaded_file is not None and file_type == "image":
                    image = Image.open(uploaded_file)
                    response = model.generate_content([user_input, image])
                    response_text = response.text
                elif uploaded_file is not None and file_type == "pdf":
                    prompt = f"PDF Content:\n{extracted_text}\n\nQuestion: {user_input}"
                    response = model.generate_content(prompt)
                    response_text = response.text
                else:
                    chat_history = []
                    for m in st.session_state.messages:
                        if m["role"] != "system":
                            role = "model" if m["role"] == "assistant" else "user"
                            chat_history.append({"role": role, "parts": [m["content"]]})
                    response = model.generate_content(chat_history)
                    response_text = response.text

                st.markdown(response_text)
                
        st.session_state.messages.append({"role": "assistant", "content": response_text})

    except Exception as e:
        st.error(f"Error: {e}")
