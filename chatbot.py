import streamlit as st
import google.generativeai as genai


st.set_page_config(page_title="METU-IE SP Bot", page_icon="🎓")

try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=API_KEY)
except:
    st.error("API Key not found in Secrets!")

def load_data():
    try:
        with open("data.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        st.error("Knowledge base file (data.txt) not found on Desktop!")
        return ""

context = load_data()

#UI ELEMENTS
st.title("METU-IE Summer Practice Consultant")
st.markdown("Providing reliable information based on official procedures.")

#CHAT HISTORY
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

#CHAT LOGIC
if prompt := st.chat_input("Ask about IE 300/400 requirements..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            available_models = [m.name for m in genai.list_models() 
                               if 'generateContent' in m.supported_generation_methods]
            
            selected_model = 'gemini-2.5-flash-lite' if 'gemini-2.5-flash-lite' in available_models else available_models[0]
            
            model = genai.GenerativeModel(selected_model)
            
            system_instruction = f"""
            You are a professional METU Industrial Engineering Virtual Consultant. 
            Answer the question ONLY using the context provided below:
            ---
            {context}
            ---
            Rules:
            1. If the answer is not in context, say: 'Your promt is out of the scope of current SP procedures. I can only provide information based on official METU-IE procedures.'
            2. Answer in English. 
            3. Strictly decline out-of-scope questions.
            4. Be user friendly.
            """
            
            response = model.generate_content(f"{system_instruction}\n\nQuestion: {prompt}")
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})

                except Exception as e:
            if "quota" in str(e).lower() or "limit" in str(e).lower():
                st.error("You have reached the API quota limit. Please try again later.")
            else:
                st.error(f"Model Selection Error: {e}")
