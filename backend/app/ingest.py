# # Before RAG

# from pypdf import PdfReader
# from sentence_transformers import SentenceTransformer

# # Load local embedding model
# model = SentenceTransformer("all-MiniLM-L6-v2")


# def extract_text_from_pdf(file_path):
#     reader = PdfReader(file_path)
#     text = ""

#     for page in reader.pages:
#         text += page.extract_text() or ""

#     return text


# def chunk_text(text, chunk_size=500, overlap=100):
#     chunks = []
#     start = 0

#     while start < len(text):
#         end = start + chunk_size
#         chunks.append(text[start:end])
#         start += chunk_size - overlap

#     return chunks


# def get_embeddings(texts):
#     return model.encode(texts).tolist()

# def ingest_file(file_path):
#     text = extract_text_from_pdf(file_path)
#     chunks = chunk_text(text)
#     embeddings = get_embeddings(chunks)
#     return list(zip(embeddings, chunks))


# After RAG (with VectorStore and OpenAI API)

# app/ingest.py
import os
from pypdf import PdfReader
from openai import OpenAI

from sentence_transformers import SentenceTransformer
import numpy as np
from app.embeddings_store import VectorStore
from tqdm import tqdm

# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_KEY='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'
client = OpenAI(api_key=OPENAI_API_KEY)

# choose embedding model (check OpenAI docs for model names and dims)
EMBED_MODEL = "text-embedding-3-small"   # example; check model dims (e.g., 1536)
# EMBED_DIM = 1536

model = SentenceTransformer("all-MiniLM-L6-v2")

def extract_text_from_pdf(path):
    reader = PdfReader(path)
    text = ""
    for p in reader.pages:
        text += p.extract_text() or ""
    return text

def chunk_text(text, chunk_size=800, overlap=100):
    # tokens = text.split()
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

# def get_embeddings(texts: list):
#     # OpenAI python client returns embeddings differently depending on version.
#     resp = client.embeddings.create(
#         model=EMBED_MODEL,
#         input=texts
#         )
#     return [np.array(e.embedding, dtype=np.float32) for e in resp.data]

# for testing without actual API calls

# for testing without actual API calls
def get_embeddings(texts):
    # return [np.random.rand(1536).astype(np.float32) for _ in texts]
    return model.encode(texts).tolist()


def ingest_file(file_path):
    text = extract_text_from_pdf(file_path)
    chunks = chunk_text(text)
    # vectors = []
    # metas = []
    # for chunk in tqdm(chunks, desc="Embedding chunks"):
    #     # emb = get_embeddings([chunk])[0]
    #     emb = np.random.rand(1536).astype(np.float32)
    #     vectors.append(emb)
    #     metas.append({"text": chunk, "source": source_name})
    # vs = VectorStore(dim=EMBED_DIM)
    # vs.add(np.vstack(vectors), metas)
    # print("Ingested", len(metas), "chunks.")
    # return len(chunks)
    embeddings = get_embeddings(chunks)
    return chunks, embeddings