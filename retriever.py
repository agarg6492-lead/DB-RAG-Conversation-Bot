from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

print("Loading retriever.py")

class Retriever:
    def __init__(self, records, index):
        self.records = records
        self.index = index
        # Load embedding model once
        self.model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2",
            token=""
        )

    def get_relevant(self, query, k=3):
        # Step 1: Convert query string into embedding vector
        query_vec = self.model.encode(
            [query],
            convert_to_numpy=True
        ).astype("float32")  # shape (1, d)
        print("Query:", query)
        print("Query vector shape:", query_vec.shape)

        # Step 2: Search FAISS index
        D, I = self.index.search(query_vec, k)
        print("Distances:", D)
        print("Indices:", I)

        # Step 3: Collect results
        results = []
        for dist, idx in zip(D[0], I[0]):
            rec = self.records[idx]
            results.append({
                "text": rec["text"],
                "source": rec.get("source", ""),
                "score": float(dist)
            })
        print("Results:", results)
        return results
