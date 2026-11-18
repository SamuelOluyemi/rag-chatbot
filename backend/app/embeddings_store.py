# # For simplicity, this is an in-memory vector store using FAISS. In production, consider a more robust solution like Pinecone or Weaviate.

# import faiss
# import numpy as np

# class VectorStore:
#     def __init__(self, dim=384):
#         self.dim = dim
#         self.index = faiss.IndexFlatL2(dim)
#         self.texts = []

#     def add(self, embedding, text):
#         embedding = np.array(embedding).reshape(1, -1).astype(np.float32)

#         if embedding.shape[1] != self.dim:
#             raise ValueError(
#                 f"Embedding dimension mismatch: got {embedding.shape[1]}, expected {self.dim}"
#             )

#         self.index.add(embedding)
#         self.texts.append(text)

#     def search(self, query_vector, k=3):
#         query_vector = np.array(query_vector).reshape(1, -1).astype(np.float32)

#         D, I = self.index.search(query_vector, k)

#         results = []
#         for idx in I[0]:
#             if idx == -1:  # No more results
#                 continue
#             if idx < len(self.texts):
#                 # results.append((self.texts[idx], float(D[0][I[0].tolist().index(idx)])))
#                 results.append((self.texts[idx], float(D[0][0])))

#         return results

# With RAG 

import faiss
import numpy as np
import os
import pickle

import tempfile
 
from google.cloud import storage as gcs
 
# GCS config — set these in your environment / Cloud Run env vars
GCS_BUCKET = os.getenv("GCS_BUCKET_NAME")  # e.g. "my-rag-chatbot-store"
FAISS_BLOB  = "faiss.index"
META_BLOB   = "meta.pkl"
 
# Local temp paths (ephemeral on Cloud Run, only used as a staging area)
TMP_DIR        = tempfile.gettempdir()
LOCAL_INDEX    = os.path.join(TMP_DIR, "faiss.index")
LOCAL_META     = os.path.join(TMP_DIR, "meta.pkl")
 
 
# ---------------------------------------------------------------------------
# GCS helpers
# ---------------------------------------------------------------------------
 
def _gcs_client():
    """Return a GCS client. Works locally (ADC) and on Cloud Run (service account)."""
    return gcs.Client()
 
 
def _blob_exists(bucket_name: str, blob_name: str) -> bool:
    client = _gcs_client()
    bucket = client.bucket(bucket_name)
    return bucket.blob(blob_name).exists()
 
 
def _upload(local_path: str, blob_name: str):
    """Upload a local file to GCS."""
    client = _gcs_client()
    bucket = client.bucket(GCS_BUCKET)
    bucket.blob(blob_name).upload_from_filename(local_path)
    print(f"✅ Uploaded {blob_name} to gs://{GCS_BUCKET}/")
 
 
def _download(blob_name: str, local_path: str) -> bool:
    """Download a GCS blob to a local path. Returns True if it existed."""
    if not GCS_BUCKET:
        return False
    try:
        client = _gcs_client()
        bucket = client.bucket(GCS_BUCKET)
        blob = bucket.blob(blob_name)
        if not blob.exists():
            return False
        blob.download_to_filename(local_path)
        print(f"⬇️  Downloaded gs://{GCS_BUCKET}/{blob_name}")
        return True
    except Exception as e:
        print(f"⚠️  GCS download failed for {blob_name}: {e}")
        return False

class VectorStore:
    def __init__(self, dim: int = 1536):
        self.dim   = dim
        self.texts = []      # list of {"text": str, "source": str}
        self.index = None
 
        self._load()
 
    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
 
    def add(self, embedding, text: str, source: str):
        embedding = np.array(embedding, dtype=np.float32).reshape(1, -1)
 
        if embedding.shape[1] != self.dim:
            raise ValueError(
                f"Embedding dimension mismatch: got {embedding.shape[1]}, expected {self.dim}"
            )
 
        self.index.add(embedding)
        self.texts.append({"text": text, "source": source})
        self._save()
        print(f"➕ Added chunk (total: {len(self.texts)})")
 
    def add_batch(self, embeddings, chunks: list[str], source: str):
        """More efficient than calling add() in a loop — saves to GCS once."""
        matrix = np.array(embeddings, dtype=np.float32)
        if matrix.ndim == 1:
            matrix = matrix.reshape(1, -1)
 
        if matrix.shape[1] != self.dim:
            raise ValueError(
                f"Embedding dimension mismatch: got {matrix.shape[1]}, expected {self.dim}"
            )
 
        self.index.add(matrix)
        self.texts.extend({"text": c, "source": source} for c in chunks)
        self._save()
        print(f"➕ Added {len(chunks)} chunks (total: {len(self.texts)})")
 
    def search(self, query_vector, k: int = 4) -> list[dict]:
        if len(self.texts) == 0:
            print("⚠️  Vector store is empty.")
            return []
 
        query_vector = np.array(query_vector, dtype=np.float32).reshape(1, -1)
        D, I = self.index.search(query_vector, k)
 
        results = []
        for idx, dist in zip(I[0], D[0]):
            if idx == -1 or idx >= len(self.texts):
                continue
            results.append({
                "text":   self.texts[idx]["text"],
                "source": self.texts[idx]["source"],
                "score":  float(dist),
            })
        return results
 
    # ------------------------------------------------------------------
    # Internal persistence
    # ------------------------------------------------------------------
 
    def _load(self):
        """Try GCS first, fall back to a fresh index."""
        index_loaded = _download(FAISS_BLOB, LOCAL_INDEX)
        meta_loaded  = _download(META_BLOB,  LOCAL_META)
 
        if index_loaded and os.path.exists(LOCAL_INDEX):
            self.index = faiss.read_index(LOCAL_INDEX)
            print("📂 Loaded FAISS index from GCS")
        else:
            self.index = faiss.IndexFlatL2(self.dim)
            print("🆕 Created fresh FAISS index")
 
        if meta_loaded and os.path.exists(LOCAL_META):
            with open(LOCAL_META, "rb") as f:
                self.texts = pickle.load(f)
            print(f"📂 Loaded {len(self.texts)} chunks from GCS")
        else:
            self.texts = []
 
    def _save(self):
        """Write index + metadata locally, then push both to GCS."""
        faiss.write_index(self.index, LOCAL_INDEX)
        with open(LOCAL_META, "wb") as f:
            pickle.dump(self.texts, f)
 
        if GCS_BUCKET:
            _upload(LOCAL_INDEX, FAISS_BLOB)
            _upload(LOCAL_META,  META_BLOB)
        else:
            print("⚠️  GCS_BUCKET_NAME not set — skipping GCS upload (local only)")