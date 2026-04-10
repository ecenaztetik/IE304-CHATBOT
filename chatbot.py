import streamlit as st
from openai import OpenAI

# 1. PAGE SETTINGS
st.set_page_config(page_title="METU-IE SP Bot", page_icon="🎓")

# 2. DEEPSEEK CONFIGURATION
try:
    # DeepSeek API'yi OpenAI kütüphanesi üzerinden client (istemci) olarak kuruyoruz
    client = OpenAI(
        api_key=st.secrets["DEEPSEEK_API"], 
        base_url="https://api.deepseek.com"
    )
except Exception as e:
    st.error(f"API Key not found or Configuration Error: {e}")

# 3. KNOWLEDGE BASE LOADING
def load_data():
    try:
        # GitHub'da çalışması için dosya yolunu sadeleştirdik
        with open("data.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        st.error("Knowledge base file (data.txt) not found!")
        return ""

context = load_data()

# 4. UI ELEMENTS
st.title("🤖 METU-IE Summer Practice Consultant")
st.markdown("Providing reliable information based on official procedures.")

# 5. CHAT HISTORY
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. CHAT LOGIC
if prompt := st.chat_input("Ask about IE 300/400 requirements..."):
    # Add user message to session state
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # System instructions for DeepSeek
            system_instruction = f"""
            You are a professional METU Industrial Engineering Virtual Consultant. 
            Answer the question ONLY using the context provided below:
            ---
            {context}
            ---
            Rules:
            1. If the answer is not in context, say: 'Your prompt is out of the scope of current SP procedures. I can only provide information based on official METU-IE procedures.'
            2. Answer in English. 
            3. Strictly decline out-of-scope questions (hobbies, generic knowledge, etc.).
            4. Be user-friendly.
            """
            
            # DeepSeek Chat Completion Call
            response = client.chat.completions.create(
                model="deepseek-chat", # DeepSeek'in standart sohbet modeli
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt},
                ],
                stream=False
            )
            
            full_response = response.choices[0].message.content
            st.markdown(full_response)
            
            # Save assistant response to history
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"DeepSeek API Error: {e}")
