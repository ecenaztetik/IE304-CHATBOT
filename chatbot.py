import streamlit as st
import google.generativeai as genai
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

st.set_page_config(page_title="METU-IE SP Bot", page_icon="🎓")

#API
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    st.error("API key bulunamadı")

#LOAD DATA
@st.cache_data
def load_text():
    with open("data.txt", "r", encoding="utf-8") as f:
        return f.read()

#CHUNKING
def chunk_text(text, size=300):
    words = text.split()
    return [" ".join(words[i:i+size]) for i in range(0, len(words), size)]

#EMBEDDING
@st.cache_resource
def load_embedder():
    return SentenceTransformer("all-MiniLM-L6-v2")

@st.cache_resource
def build_index(chunks):
    model = load_embedder()
    embeddings = model.encode(chunks)

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings))

    return index, embeddings

#RETRIEVE
def retrieve(query, chunks, index, k=3):
    model = load_embedder()
    q_emb = model.encode([query])

    _, idx = index.search(np.array(q_emb), k)
    return [chunks[i] for i in idx[0]]

#MODEL
system_prompt = """
You are a METU Industrial Engineering Summer Practice assistant.

Rules:
- Answer ONLY using given context
- If not in context, say:
  "Your question is out of scope of METU-IE Summer Practice procedures."
- Be clear and helpful
- Answer in English
"""

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash-lite",
    system_instruction=system_prompt,
    generation_config={
        "max_output_tokens": 250,
        "temperature": 0.2
    }
)

#INIT
text = load_text()
chunks = chunk_text(text)
index, _ = build_index(chunks)

if "messages" not in st.session_state:
    st.session_state.messages = []

#UI-
st.title("METU-IE Summer Practice Chatbot")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

#CHAT
if prompt := st.chat_input("Ask your question..."):

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.write(prompt)

    #RAG
    top_chunks = retrieve(prompt, chunks, index)
    context = "\n\n".join(top_chunks)

    #SHORT MEMORY DUE TO NOT EXCEEDING QUOTA
    history = st.session_state.messages[-3:]

    #PROMPT
    final_prompt = f"""
Context:
{context}

Conversation:
{history}

Question:
{prompt}
"""

    #MODEL
    with st.chat_message("assistant"):
        try:
            response = model.generate_content(final_prompt)
            answer = response.text

            st.write(answer)

            st.session_state.messages.append(
                {"role": "assistant", "content": answer}
            )

        except Exception as e:
            st.error("Error occurred")
