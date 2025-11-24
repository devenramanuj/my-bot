import streamlit as st
import google.generativeai as genai
from PIL import Image
import PyPDF2
from gtts import gTTS
import io
from duckduckgo_search import DDGS
from datetime import datetime
import pytz # સમય માટે

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

# --- 3. CSS Styling (Color Fix) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap');

    .stApp {{
        background-color: {main_bg} !important;
        color: {text_color} !important;
    }}
    
    /* સામાન્ય ટેક્સ્ટ */
    p, div, span, li, label, h1, h2, h3, h4, h5, h6, .stMarkdown {{
        color: {text_color} !important;
    }}
    
    /* 🛑 SETTINGS MENU FIX (Expander) */
    /* સેટિંગ્સ બોક્સ હંમેશા સફેદ અને અક્ષરો કાળા */
    .streamlit-expanderContent {{
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #000000;
        border-radius: 10px;
    }}
    
    /* મેનુની અંદરના બધા લેબલ અને લખાણ કાળા */
    .streamlit-expanderContent label, 
    .streamlit-expanderContent p, 
    .streamlit-expanderContent span, 
    .streamlit-expanderContent div {{
        color: #000000 !important;
    }}

    /* Title Font */
    h1 {{
        font-family: 'Orbitron', sans-serif !important;
        color: {title_color} !important;
        text-align: center;
        font-size: 3rem !important;
        margin-top: 10px;
    }}

    /* Hide Elements */
    [data-testid="stSidebar"], [data-testid="stToolbar"], footer, header {{ display: none !important; }}
    .block-container {{ padding-top: 2rem !important; padding-bottom: 5rem !important; }}
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

# --- 5. Settings Menu (Only Symbol ⚙️) ---
web_search = False

# અહીં નામ બદલીને માત્ર આઈકન રાખ્યું છે
with st.expander("⚙️"):
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("###### 🎨 Theme")
        st.toggle("🌗 Mode", value=st.session_state.theme, on_change=toggle_theme)
    with col_b:
        st.write("###### 🌍 Internet")
        web_search = st.toggle("Live Search") # આ ચાલુ કરશો તો જ ભાવ બતાવશે
    
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
    model = genai.GenerativeModel('gemini-2.0-flash')
except:
    st.error("Error: Please check API Key.")
    st.stop()

# --- 7. Functions (Internet & Time) ---

# સમય મેળવવાનું ફંક્શન
def get_current_time():
    IST = pytz.timezone('Asia/Kolkata')
    now = datetime.now(IST)
    return now.strftime("%Y-%m-%d %H:%M:%S %p")

# ઇન્ટરનેટ સર્ચ ફંક્શન
def search_internet(query):
    try:
        # DDGS સીધું કોલ કરીએ
        results = DDGS().text(query, max_results=3)
        if results:
            return "\n".join([f"- {r['body']}" for r in results])
        return "No results found on internet."
    except Exception as e:
        return f"Search Error: {e}"

# --- 8. Chat Logic ---
if "messages" not in st.session_state.messages:
    st.session_state.messages = [
        {"role": "assistant", "content": "જયશ્રી કૃષ્ણ! 🙏 હું DEV છું. બોલો!"}
    ]

for message in st.session_state.messages:
    avatar = "🤖" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
        if "audio" in message:
            st.audio(message["audio"], format="audio/mp3")

# --- 9. Input Processing ---
if user_input := st.chat_input("Ask DEV... (કી-બોર્ડનું માઈક 🎙️ વાપરો)"):
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("તપાસ કરી રહ્યો છું..."):
                response_text = ""
                
                # 1. Internet Search Logic (જો સ્વિચ ચાલુ હોય)
                if web_search:
                    current_time = get_current_time() # અત્યારનો સમય
                    st.toast(f"Searching Live... 🌍 ({current_time})")
                    
                    search_results = search_internet(user_input)
                    
                    # AI ને સમય અને સર્ચ રિઝલ્ટ બંને આપો
                    prompt = f"""
                    Current Date & Time in India: {current_time}
                    
                    Internet Search Results:
                    {search_results}
                    
                    User Question: {user_input}
                    
                    Answer in Gujarati. If asking for price/news, use the search results.
                    """
                    response = model.generate_content(prompt)
                    response_text = response.text

                # 2. Image Logic
                elif uploaded_file is not None and uploaded_file.name.endswith(('.jpg', '.png', '.jpeg')):
                    image = Image.open(uploaded_file)
                    response = model.generate_content([user_input, image])
                    response_text = response.text
                
                # 3. PDF Logic
                elif uploaded_file is not None and uploaded_file.name.endswith('.pdf'):
                    pdf_reader = PyPDF2.PdfReader(uploaded_file)
                    pdf_text = ""
                    for page in pdf_reader.pages:
                        pdf_text += page.extract_text()
                    prompt = f"PDF Context:\n{pdf_text}\n\nQuestion: {user_input}"
                    response = model.generate_content(prompt)
                    response_text = response.text
                
                # 4. Normal Chat
                else:
                    # સામાન્ય વાતમાં પણ સમયની ખબર હોવી જોઈએ
                    current_time = get_current_time()
                    prompt = f"Current Time: {current_time}\nUser: {user_input}\nReply in Gujarati."
                    
                    # હિસ્ટ્રી સાથે મોકલો
                    chat_history = []
                    for m in st.session_state.messages:
                        if m["role"] != "system" and "audio" not in m:
                            role = "model" if m["role"] == "assistant" else "user"
                            chat_history.append({"role": role, "parts": [m["content"]]})
                    
                    # છેલ્લે નવો પ્રોમ્પ્ટ ઉમેરો
                    chat_history.append({"role": "user", "parts": [prompt]})
                    
                    response = model.generate_content(chat_history)
                    response_text = response.text

                st.markdown(response_text)
                
                # Voice Output
                try:
                    tts = gTTS(text=response_text, lang='gu') 
                    audio_bytes = io.BytesIO()
                    tts.write_to_fp(audio_bytes)
                    audio_bytes.seek(0)
                    st.audio(audio_bytes, format="audio/mp3")
                    st.session_state.messages.append({"role": "assistant", "content": response_text, "audio": audio_bytes})
                except:
                    st.session_state.messages.append({"role": "assistant", "content": response_text})

    except Exception as e:
        st.error(f"Error: {e}")
