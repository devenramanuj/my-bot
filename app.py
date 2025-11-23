import streamlit as st
import google.generativeai as genai

st.title("🛠️ બોટ રિપેરિંગ ટૂલ (Tester)")

# 1. API Key ચેક કરો
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
    st.success("✅ API Key મળી ગઈ છે! (Connection OK)")
except:
    st.error("❌ API Key નથી મળી. Secrets ચેક કરો.")
    st.stop()

# 2. કયા મોડેલ ચાલે છે તે શોધો
st.write("🔍 તમારા એકાઉન્ટ માટે કયા મોડેલ ઉપલબ્ધ છે તે તપાસી રહ્યો છું...")

try:
    available_models = []
    # લિસ્ટ મેળવો
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            available_models.append(m.name)

    if available_models:
        st.success(f"✅ અભિનંદન! કુલ {len(available_models)} મોડેલ મળ્યા છે.")
        st.code(available_models) # લિસ્ટ બતાવશે
        
        # સૌથી પહેલું મોડેલ ટેસ્ટ કરો
        test_model = available_models[0]
        st.write(f"🧪 ટેસ્ટિંગ: {test_model}...")
        
        model = genai.GenerativeModel(test_model)
        response = model.generate_content("Hello AI")
        
        st.balloons()
        st.success(f"🎉 કામ થઈ ગયું! આ મોડેલ ચાલે છે: {test_model}")
        st.info("AI નો જવાબ: " + response.text)
        
    else:
        st.error("❌ વિચિત્ર! API Key સાચી છે પણ કોઈ મોડેલ દેખાતા નથી.")

except Exception as e:
    st.error(f"❌ ટેસ્ટિંગમાં ભૂલ આવી: {e}")
