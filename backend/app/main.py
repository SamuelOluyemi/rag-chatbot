# Using LLMs to answer questions based on uploaded PDFs. FastAPI backend.

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Body
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from openai import OpenAI

from app.ingest import extract_text_from_pdf, chunk_text, get_embeddings, ingest_file
from app.embeddings_store import VectorStore
from app.config import LLM_MODEL, OPENAI_API_KEY, TOP_K

load_dotenv()

app = FastAPI()
client = OpenAI(api_key=os.getenv(OPENAI_API_KEY))  # API key is read from config.py

# Enable CORS (frontend fix)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize vector store
vs = VectorStore(dim=384)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def root():
    return {"message": "RAG backend running 🚀"}

# # Debug endpoint to check if API key is loaded correctly
# @app.get("/test-key")
# def test_key():
#     return {"key": os.getenv("OPENAI_API_KEY")}

# 📄 Upload PDF
@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # # Extract + chunk
    # text = extract_text_from_pdf(file_path)
    # chunks = chunk_text(text)

    # # Embed + store
    # embeddings = get_embeddings(chunks)
    
    chunks, embeddings = ingest_file(file_path)
    for emb, chunk in zip(embeddings, chunks):
        vs.add(emb, chunk, source=file.filename)
    print("TOTAL STORED:", len(vs.texts))

    return {"message": f"{len(chunks)} chunks stored successfully"}
    


# ❓ Ask question
@app.post("/ask")
async def ask(data: dict = Body(...)):
    query = data.get("query")

    if not query:
        return {"error": "No query provided", "sources": []}
    
    try:
        # Embed query (LOCAL)
        q_emb = get_embeddings([query])[0]
        
        # Retrieve context
        # 2️⃣ Search vector store
        results = vs.search(q_emb, k=3)
        
        if not results:
            return {
                "answer": "No relevant context found. Upload a document first.",
                "sources": []
            }

        # 3️⃣ Build context
        context_text = "\n\n".join([r["text"] for r in results])
        # sources = [r[1] for r in results]
        
        # 4️⃣ Call LLM
        prompt = f"""
You are an AI assistant.
Use ONLY the context below to answer the question.

If the answer is not in the context, say:
"I don't know based on the provided document."

Context:
{context_text}

Question:
{query}
If the answer is not in the context, say "I don't know based on the provided information."
"""
        
        # Call OpenAI LLM
        response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": query}],
        temperature=0.2
    )
        
        if not response.choices or not response.choices[0].message:
            return {
                "answer": "No response from model.",
                "sources": [r[0] for r in results]
            }
        
        answer = response.choices[0].message.content

        return {
            "answer": answer,
            # "sources": [r[0] for r in results]
            "sources": list(set([r["source"] for r in results]))
        }
        
    except Exception as e:
        print("Error in /ask:", str(e))
        
        return {"error": "An error occurred while processing your request.",
                "sources": [],
                "error_details": str(e)}


# # Using custom response format before integrating LLM, to isolate issues.
# # app/main.py
# import os
# from fastapi import FastAPI, UploadFile, File, Body
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# import numpy as np
# from openai import OpenAI
# from dotenv import load_dotenv

# from app.ingest import ingest_file, chunk_text, extract_text_from_pdf, get_embeddings
# from app.embeddings_store import VectorStore
# from app.config import LLM_MODEL, OPENAI_API_KEY, TOP_K, EMBED_DIM

# load_dotenv()
# # OPENAI_API_KEY = os.getenv(OPENAI_API_KEY)

# client = OpenAI(api_key=OPENAI_API_KEY)

# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # allow all origins for dev
#     allow_credentials=True,
#     allow_methods=["*"],   # allow GET, POST, etc.
#     allow_headers=["*"],   # allow all headers
# )

# vs = VectorStore(dim=384)

# class AskRequest(BaseModel):
#     question: str
#     k: int = 4

# @app.get("/")
# def root():
#     return {"message": "RAG Chatbot API running"}

# @app.post("/upload")
# async def upload(file: UploadFile = File(...)):
#     print("Received file:", file.filename)
#     contents = await file.read()
#     tmp = f"/tmp/{file.filename}"
#     with open(tmp, "wb") as f:
#         f.write(contents)
    
#     # reuse ingest logic but simpler
#     # commented out because ingest_file() returns list of (embedding, chunk) pairs, but we want to add them one by one to vs
#     # text = extract_text_from_pdf(tmp)
#     # chunks = chunk_text(text)
#     # vectors = []
#     # metas = []
#     # for chunk in chunks:
#     #     emb = get_embeddings([chunk])[0]
#     #     vectors.append(emb)
#     #     metas.append({"text": chunk, "source": file.filename})
#     # vs.add(np.vstack(vectors), metas)
#     # vs.add(emb, chunk)
#     pairs = ingest_file(tmp)
#     for emb, chunk in pairs:
#         vs.add(emb, chunk)
#     return {"status": "ok", "chunks_ingested": len(pairs)}

# # @app.post("/ask")
# # async def ask(req: AskRequest):
# #     query = req.question
# #     # q_emb = client.embeddings.create(
# #     #     model="text-embedding-3-small",
# #     #     input=[query]
# #     #     ).data[0].embedding
# #     q_emb = np.random.rand(1536).astype(np.float32)
# #     # results = vs.search(np.array(q_emb, dtype=np.float32), k=req.k)
# #     results = vs.search(np.array([q_emb]).astype(np.float32))
# #     # build context from results
# #     context_chunks = [r[0] for r in results]
# #     context = "\n\n".join([r["text"] for r in results])
# #     system = "You are an assistant. Answer based only on the context. If answer not in context, say you don't know."
# #     messages = [
# #         {"role":"system", "content": system},
# #         {"role":"user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
# #     ]
# #     resp = client.chat.completions.create(model=LLM_MODEL, messages=messages, temperature=0.0)
# #     # answer = resp.choices[0].message.content
# #     # return {"answer": answer, "sources": [r["source"] for r in results]}
# #     answer = f"Based on your document:\n\n{context[:500]}..."

# #     return {
# #         "answer": answer,
# #         "context_used": len(context_chunks)
# #     }
# @app.post("/ask")
# async def ask(data: dict = Body(...)):
#     try: 
#         query = data.get("query")
        
#         if not query:
#             return {"error": "No query provided"}

#         # 🔹 Step 1: Create query embedding (TEMP - random)
#         # q_emb = np.random.rand(1536).astype(np.float32)
#         q_emb = get_embeddings([query])[0]
#         # ✅ Convert embedding properly to NumPy array before reshaping
#         q_emb = np.array(q_emb, dtype=np.float32).reshape(1, -1)
#         print("DEBUG SHAPE:", q_emb.shape)

#         # 🔹 Step 2: Search vector store (THIS is where your line goes)
#         results = vs.search(q_emb)
        
#         if not results:
#             return {
#                 "answer": "No relevant context found. Upload a document first.",
#                 "sources": []
#             }

#         # 🔹 Step 3: Extract context
#         context_chunks = [r[0] for r in results if len(r) > 0]  # assuming (text, score)
        
#         if not context_chunks:
#             return {
#                 "answer": "No usable context found.",
#                 "sources": []
#             }
#         context = "\n".join(context_chunks)

#         # 🔹 Step 4: Generate response (TEMP simple response)
#         answer = f"Based on your document:\n\n{context[:500]}..."

#         return {
#             "answer": answer,
#             "context_used": len(context_chunks)
#         }
#     except Exception as e:
#         print("Error in /ask:", str(e))
#         return {
#             "error": str(e),
#             "sources": []
#         }