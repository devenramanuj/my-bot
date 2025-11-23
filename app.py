import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io

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
    popover_bg = "#1E1E1E"
else:
    main_bg = "#FFFFFF"
    text_color = "#000000"
    title_color = "#00008B"
    popover_bg = "#F0F2F6"

# --- 3. CSS Styling ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap');
    .stApp {{ background-color: {main_bg} !important; color: {text_color} !important; }}
    
    p, div, span, li, label, h1, h2, h3, h4, h5, h6 {{ color: {text_color} !important; }}
    
    [data-testid="stPopoverBody"] {{ background-color: {popover_bg} !important; border: 1px solid {text_color}; }}
    
    h1 {{
        font-family: 'Orbitron', sans-serif !important;
        color: {title_color} !important;
        text-align: center;
        font-size: 3rem !important;
        margin-top: 10px;
    }}
    
    /* ઓડિયો ઈનપુટ ફિક્સ */
    .stAudioInput {{
        position: fixed;
        bottom: 80px;
        z-index: 9999;
        width: 100%;
    }}

    /* બધું છુપાવો */
    [data-testid="stSidebar"], [data-testid="stToolbar"], footer, header {{ display: none !important; }}
    .block-container {{ padding-top: 2rem !important; padding-bottom: 8rem !important; }}
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

# Settings Menu (Only)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    with st.popover("⚙️ સેટિંગ્સ (Settings)", use_container_width=True):
        st.toggle("🌗 Mode", value=st.session_state.theme, on_change=toggle_theme)
        if st.button("🗑️ Reset Chat"):
            st.session_state.messages = []
            st.rerun()

# --- 5. API Setup ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
except:
    st.error("Error: Please check API Key.")
    st.stop()

# --- 6. Chat Logic ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "જયશ્રી કૃષ્ણ! 🙏 હું DEV છું. નીચે માઈક બટન દબાવીને સીધું બોલો!"}
    ]

for message in st.session_state.messages:
    avatar = "🤖" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        # જો યુઝરનો ઓડિયો હોય તો પ્લેયર બતાવો
        if "user_audio" in message:
            st.audio(message["user_audio"], format="audio/wav")
        elif message["content"]:
            st.markdown(message["content"])
            
        # AI નો ઓડિયો
        if "ai_audio" in message:
            st.audio(message["ai_audio"], format="audio/mp3")

# --- 7. NEW NATIVE AUDIO INPUT (The Fix) ---
# આ નવું ફીચર છે જે 100% ચાલે છે
audio_value = st.audio_input("Record a voice note")

# --- 8. Processing Logic ---
final_input = None
is_audio_msg = False

# કેસ 1: ઓડિયો રેકોર્ડ કર્યો
if audio_value:
    final_input = audio_value
    is_audio_msg = True

# કેસ 2: ટાઈપ કર્યું
elif chat_input := st.chat_input("Type a message..."):
    final_input = chat_input
    is_audio_msg = False

if final_input:
    # User Message Show
    with st.chat_message("user", avatar="👤"):
        if is_audio_msg:
            st.audio(final_input, format="audio/wav")
            # મેમરીમાં ઓડિયો સેવ કરો
            st.session_state.messages.append({"role": "user", "content": "", "user_audio": final_input})
        else:
            st.markdown(final_input)
            st.session_state.messages.append({"role": "user", "content": final_input})

    # AI Response
    try:
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("સાંભળી રહ્યો છું..."):
                
                # ઓડિયો સીધો જ મોડેલને મોકલો (Gemini સાંભળી શકે છે!)
                if is_audio_msg:
                    # ઓડિયો બાઈટ્સ વાંચો
                    audio_bytes = final_input.getvalue()
                    prompt_parts = [
                        "Listen to this audio and reply in Gujarati only. Be helpful and kind.",
                        {"mime_type": "audio/wav", "data": audio_bytes}
                    ]
                    response = model.generate_content(prompt_parts)
                else:
                    response = model.generate_content(final_input)
                
                response_text = response.text
                st.markdown(response_text)
                
                # Voice Output (AI બોલે છે)
                try:
                    tts = gTTS(text=response_text, lang='gu') 
                    ai_audio_bytes = io.BytesIO()
                    tts.write_to_fp(ai_audio_bytes)
                    ai_audio_bytes.seek(0)
                    st.audio(ai_audio_bytes, format="audio/mp3")
                    
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": response_text, 
                        "ai_audio": ai_audio_bytes
                    })
                except:
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                    
    except Exception as e:
        st.error(f"Error: {e}")
