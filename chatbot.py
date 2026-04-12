import streamlit as st
import google.generativeai as genai


st.set_page_config(page_title="METU-IE SP Bot", page_icon="🎓") 

# --- CSS ---
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(-45deg, #ff9a9e, #fad0c4, #ffecd2, #a1c4fd, #c2e9fb, #d4fc79);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .stApp, .stMarkdown, p, li, span, h1, h2, h3, h4, h5, h6, label { 
        color: #000000 !important; 
    }

    [data-testid="stChatMessage"] {
        background-color: rgba(255, 255, 255, 0.8) !important;
        border-radius: 20px !important;
        border: 2px solid #ffdae0 !important;
    }

    [data-testid="stChatMessageContent"] * { 
        color: #000000 !important; 
    }

    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.5) !important;
        backdrop-filter: blur(15px);
    }

    [data-testid="stSidebar"] * { 
        color: #000000 !important; 
    }

    .stChatInputContainer textarea {
        color: #000000 !important;
        background-color: rgba(255, 255, 255, 0.6) !important;
    }

    .stButton>button {
        border-radius: 30px !important;
        background: linear-gradient(to right, #ff9a9e 0%, #fecfef 100%) !important;
        color: #000000 !important;
        border: 1px solid #ffb6c1 !important;
        font-weight: bold;
    }

    h1 { 
        color: #d63384 !important; 
        font-weight: 800 !important; 
    }

    a { 
        color: #0000EE !important; 
        text-decoration: underline !important; 
    }

    /* 🔝 TOP BAR */
    .topbar {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 55px;
        background: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(12px);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 18px;
        z-index: 9999;
        border-bottom: 2px solid #ffdae0;
    }

    /* 🔽 BOTTOM BAR */
    .bottombar {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 40px;
        background: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(12px);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 13px;
        z-index: 9999;
        border-top: 2px solid #ffdae0;
    }

    /* chat spacing fix */
    .block-container {
        padding-top: 70px;
        padding-bottom: 60px;
    }
</style>
""", unsafe_allow_html=True)


# --- TOP BAR ---
st.markdown("""
<div class="topbar">
🌈 METU IE SP Assistant | Gemini Powered
</div>
""", unsafe_allow_html=True)

# --- BOTTOM BAR ---
st.markdown("""
<div class="bottombar">
Built by Group 5 ❤️ 
</div>
""", unsafe_allow_html=True)


# --- API KEY ---
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


# --- UI ---
st.title("METU-IE Summer Practice Consultant")
st.markdown("Providing reliable information based on official procedures.")


# --- CHAT HISTORY ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# --- CHAT LOGIC ---
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
