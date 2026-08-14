import hashlib
from typing import List
import numpy as np

class EmbeddingClient:
    """
    Standalone embedding generation service.
    Reuses the deterministic synthetic embedding generation logic from D2.
    Guarantees 100% deterministic reproducibility across runs without needing heavy ML dependencies.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", dimension: int = 384):
        self.model_name = model_name
        self.dimension = dimension

    def generate_embedding(self, text: str) -> List[float]:
        if not text:
            text = "empty_text"

        hash_digest = hashlib.sha256(text.encode("utf-8")).digest()
        seed = int.from_bytes(hash_digest[:4], "big")
        rng = np.random.RandomState(seed)
        raw_vector = rng.randn(self.dimension)
        norm = float(np.linalg.norm(raw_vector))
        if norm == 0.0:
            norm = 1.0
        normalized = (raw_vector / norm).tolist()
        return [round(float(x), 6) for x in normalized]

    def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        return [self.generate_embedding(t) for t in texts]
