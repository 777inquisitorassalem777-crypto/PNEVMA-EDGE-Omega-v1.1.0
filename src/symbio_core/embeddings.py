
"""Embedding adapters: optional sentence-transformers local model or deterministic offline hash vector."""
import hashlib, math
class HashEmbedding:
    """Reproducible baseline for tests only; not a semantic-quality embedding model."""
    def __init__(self, dimensions=384): self.dimensions = dimensions
    def encode(self, text):
        vector = [0.0] * self.dimensions
        for token in text.lower().split():
            digest = hashlib.sha256(token.encode()).digest()
            idx = int.from_bytes(digest[:4], "big") % self.dimensions
            vector[idx] += 1.0 if digest[4] % 2 else -1.0
        norm = math.sqrt(sum(x*x for x in vector)) or 1.0
        return [x/norm for x in vector]

class SentenceTransformerEmbedding:
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        try: from sentence_transformers import SentenceTransformer
        except ImportError as exc: raise RuntimeError("Install optional dependencies: pip install '.[embeddings]'") from exc
        self.model = SentenceTransformer(model_name)
        self.dimensions = self.model.get_sentence_embedding_dimension()
    def encode(self, text): return self.model.encode(text, normalize_embeddings=True).tolist()
