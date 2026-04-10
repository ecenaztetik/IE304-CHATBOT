import streamlit as st
from groq import Groq


st.set_page_config(page_title="METU-IE SP Bot", page_icon="🎓")

# 1. GROQ API KEY'İ ÇEKİYORUZ
try:
    API_KEY = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=API_KEY)
except:
    st.error("API Key not found in Secrets! Lütfen GROQ_API_KEY olarak eklediğine emin ol.")

def load_data():
    try:
        with open("data.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        st.error("Knowledge base file (data.txt) not found!")
        return ""

context = load_data()

# UI ELEMENTS
st.title("🤖 METU-IE Summer Practice Consultant")
st.markdown("Providing reliable information based on official procedures.")

# CHAT HISTORY
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# CHAT LOGIC
if prompt := st.chat_input("Ask about IE 300/400 requirements..."):
    # Kullanıcı mesajını ekrana bas
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # 2. SİSTEM YÖNERGESİNİ HAZIRLIYORUZ (Groq bu formatı daha iyi anlar)
            system_instruction = f"""
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
            
            # 3. MESAJ GEÇMİŞİNİ API'YE UYGUN DİZİYORUZ
            # Groq/Llama modellerinde sistem yönergesi en başta "system" rolüyle verilir.
            api_messages = [{"role": "system", "content": system_instruction}]
            
            for m in st.session_state.messages:
                api_messages.append({"role": m["role"], "content": m["content"]})

            # 4. LLAMA MODELİNE İSTEK ATIYORUZ
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=api_messages,
                temperature=0.1 # Staj kuralları net olmalı, halüsinasyonu engellemek için düşürdük.
            )
            
            bot_reply = response.choices[0].message.content
            st.markdown(bot_reply)
            
            # 5. ASİSTANIN CEVABINI GEÇMİŞE KAYDEDİYORUZ
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})

        except Exception as e:
            st.error(f"Groq API Error: {e}")
