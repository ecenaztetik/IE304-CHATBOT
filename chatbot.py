import streamlit as st
import google.generativeai as genai
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from sentence_transformers import SentenceTransformer
#PAGE
st.set_page_config(page_title="METU-IE SP Bot", page_icon="🎓")

#API
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    st.error("API key bulunamadı. Lütfen Secrets ayarlarını kontrol edin.")

#LOAD DATA
@st.cache_data
def load_text():
    try:
        with open("data.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        st.error("'data.txt' dosyası bulunamadı!")
        return ""

#CHUNKING
def chunk_text(text, size=300):
    words = text.split()
    return [" ".join(words[i:i+size]) for i in range(0, len(words), size)]

#EMBEDDING
@st.cache_resource
def load_embedder():
    return SentenceTransformer("all-MiniLM-L6-v2")

@st.cache_resource
def build_vector_space(chunks):
    model = load_embedder()
    embeddings = model.encode(chunks)
    return embeddings

#RETRIEVE
def retrieve(query, chunks, embeddings, k=3):
    model = load_embedder()
    q_emb = model.encode([query])
    
    #Similarity
    similarities = cosine_similarity(q_emb, embeddings)[0]
    
    #Best similar case
    top_indices = sorted(range(len(similarities)), key=lambda i: similarities[i], reverse=True)[:k]
    
    return [chunks[i] for i in top_indices]

#MODEL
system_prompt = """
You are a professional METU Industrial Engineering Summer Practice assistant.

Rules:
- Answer using the given context.
- If the answer is not in the context, say:
  "Your question is out of scope of METU-IE Summer Practice procedures. I can only provide information based on official documents."
- Be user-friendly and kind.
- Answer in English.
"""

#DEFINE MODEL
try:
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash-lite", # İstediğin model korundu
        system_instruction=system_prompt,
        generation_config={
            "max_output_tokens": 500,
            "temperature": 0.2
        }
    )
except Exception as e:
    st.error(f"Model yükleme hatası: {e}")

#START THE SYSTEM
text = load_text()
if text:
    chunks = chunk_text(text)
    embeddings = build_vector_space(chunks)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # UI BAŞLIK
    st.title("METU-IE Summer Practice Chatbot")
    st.info("Ask me anything about IE 300/400 procedures.")

    # MESAJ GEÇMİŞİNİ GÖSTER
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    #CHAT LOGIC
    if prompt := st.chat_input("Ask your question..."):
        # Kullanıcı mesajını ekle
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        #RAG 
        top_chunks = retrieve(prompt, chunks, embeddings)
        context = "\n\n".join(top_chunks)

        #USE SHORT MEMORY TO NOT EXCEEDING QUOTA
        history = st.session_state.messages[-3:]

        #PROMPT
        final_prompt = f"""
Context from official documents:
{context}

Recent conversation history:
{history}

User Question:
{prompt}
"""

        #MODEL ANSWERS
        with st.chat_message("assistant"):
            try:
                response = model.generate_content(final_prompt)
                answer = response.text

                st.write(answer)

                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )

            except Exception as e:
                st.error(f"Response Error: {e}")
else:
    st.warning("Please make sure 'data.txt' is in your GitHub repository.")
