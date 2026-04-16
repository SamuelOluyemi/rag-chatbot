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

class VectorStore:
    def __init__(self, dim=384, index_path="faiss.index", meta_path="meta.pkl"):
        self.dim = dim
        self.index_path = index_path
        self.meta_path = meta_path

        if os.path.exists(index_path):
            self.index = faiss.read_index(index_path)
            
            if os.path.exists(meta_path):
                with open(meta_path, "rb") as f:
                    self.texts = pickle.load(f) # assign to self.texts directly
            else:
                self.texts = []
                print("⚠️ meta.pkl missing, resetting texts")
                
        else:
            self.index = faiss.IndexFlatL2(dim)
            self.texts = []
            print("⚠️ faiss.index missing, starting fresh")

        # # Always keep texts synced for search
        # self.texts = [m["text"] for m in self.metadata] if self.metadata else []
        self.texts = []

    def add(self, embedding, text, source):
        # Ensure 2D float32
        embedding = np.array(embedding).reshape(1, -1).astype(np.float32)

        # # Force correct shape
        # if len(embedding.shape) == 1:
        #     embedding = embedding.reshape(1, -1)

        # ⚠️ FAISS (Dimension) safety check
        if embedding.shape[1] != self.dim:
            raise ValueError(
                f"Embedding dimension mismatch: got {embedding.shape[1]}, expected {self.dim}"
            )

        self.index.add(embedding)
        self.texts.append({"text": text, "source": source})
        # self.metadata.append({"text": text, "source": "uploaded"})

        self._save()
        print("Added embedding shape:", embedding.shape)

    def search(self, query_vector, k=4):
        if len(self.texts) == 0:
            print("No texts in store, returning empty results.")
            return []
        query_vector = np.array(query_vector).reshape(1, -1).astype(np.float32)

        # # Force 2D
        # if len(query_vector.shape) == 1:
        #     query_vector = query_vector.reshape(1, -1)

        print("FAISS INPUT SHAPE:", query_vector.shape)

        D, I = self.index.search(query_vector, k)

        results = []
        # for production
        for idx, dist in zip(I[0], D[0]):
            # if idx < len(self.texts):
            #     results.append((self.texts[idx], float(dist)))
            if idx == -1 or idx >= len(self.texts):
                continue
            
            results.append({
                "text": self.texts[idx]["text"],
                "source": self.texts[idx]["source"],
                "score": float(dist)
            })
            
        return results
        # # before production
        # for idx in I[0]:
        #     if idx < len(self.texts):
        #         results.append((self.texts[idx], D[0][0]))
        # return results

    def _save(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "wb") as f:
            pickle.dump(self.texts, f)