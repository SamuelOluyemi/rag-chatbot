import os
from pypdf import PdfReader
from openai import OpenAI
import numpy as np
from tqdm import tqdm

# Load API key from environment (REQUIRED)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) #it's this way because it's not being impoorted a variable from config.py

EMBED_MODEL = "text-embedding-3-small"
BATCH_SIZE = 50  # safe batch size

def extract_text_from_pdf(path):
    reader = PdfReader(path)
    text = ""
    for p in reader.pages:
        text += p.extract_text() or ""
    return text


def chunk_text(text, chunk_size=300, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def get_embeddings(texts):
    embeddings = []

    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i:i + BATCH_SIZE]

        response = client.embeddings.create(
            model=EMBED_MODEL,
            input=batch
        )

        batch_embeddings = [
            np.array(e.embedding, dtype=np.float32)
            for e in response.data
        ]

        embeddings.extend(batch_embeddings)

    return embeddings


def ingest_file(file_path):
    print("📄 Extracting text...")
    text = extract_text_from_pdf(file_path)

    print("✂️ Chunking...")
    chunks = chunk_text(text)

    print(f"🧠 Generating embeddings ({len(chunks)} chunks)...")
    embeddings = get_embeddings(chunks)

    print("✅ Done!")

    return chunks, embeddings