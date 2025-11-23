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

# --- 3. CSS Styling (Mobile Menu Fix) ---
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
        margin-top: 10px;
    }}

    /* ----------------------------------------------------------- */
    /* 🛑 MOBILE MENU FIX (Invisible Header Strategy)            */
    /* ----------------------------------------------------------- */
    
    /* 1. હેડરને ગાયબ કરવાને બદલે પારદર્શક (Transparent) બનાવો */
    header[data-testid="stHeader"] {{
        background-color: transparent !important;
        z-index: 1 !important; /* કન્ટેન્ટની પાછળ */
    }}
    
    /* 2. પણ હેડરની અંદર રહેલા 3 ટપકાં (Toolbar) ને છુપાવો */
    [data-testid="stToolbar"] {{
        display: none !important;
    }}
    
    /* 3. Manage App બટનને છુપાવો */
    div[data-testid="stStatusWidget"] {{
        display: none !important;
    }}

    /* 4. ઉપરની રંગીન લાઈન છુપાવો */
    [data-testid="stDecoration"] {{
        display: none !important;
    }}

    /* 5. મેનુ બટન (Hamburger) ને ખાસ કલર અને પાવર આપો */
    [data-testid="stSidebarCollapsedControl"] {{
        display: block !important;
        visibility: visible !important;
        color: {text_color} !important; /* કાળો/સફેદ કલર */
        background-color: rgba(128, 128, 128, 0.1); /* આછું બેકગ્રાઉન્ડ */
        border-radius: 10px;
        padding: 5px;
        z-index: 999999 !important; /* સૌથી ઉપર */
    }}
    
    /* ફુટર ગાયબ */
    footer {{
        display: none !important;
    }}

    /* કન્ટેન્ટને થોડું નીચે લો */
    .block-container {{
        padding-top: 4rem !important;
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
            st.info("📄 PDF Detected")
            with st.spinner("Processing..."):
                extracted_text = get_pdf_text(uploaded_file)
                st.success("Loaded!")
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
                    prompt = f"PDF: {extracted_text}\n\nQ: {user_input}"
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
