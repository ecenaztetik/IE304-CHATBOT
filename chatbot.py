import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="METU-IE SP Bot", page_icon="🎓")

try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=API_KEY)
except:
    st.error("Google API Key bulunamadı! Secrets kısmını kontrol et.")
def load_data():
    try:
        with open("data.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        st.error("data.txt dosyası bulunamadı!")
        return ""

context = load_data()

st.title("METU-IE Summer Practice Consultant")
st.markdown("Providing reliable information based on official procedures.")

system_prompt = f"""
You are a professional METU Industrial Engineering Virtual Consultant. 
Answer the question ONLY using the context provided below:
---
{context}
---
Rules:
1. If the answer is not in context, say: 'Your prompt is out of the scope of current SP procedures. I can only provide information based on official METU-IE procedures.'
2. Answer in English. 
3. Strictly decline out-of-scope questions.
4. Be user friendly.
"""
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash-lite",
    system_instruction=system_prompt
)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about IE 300/400 requirements..."):

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)


    with st.chat_message("assistant"):
        try:
            response = st.session_state.chat_session.send_message(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")
