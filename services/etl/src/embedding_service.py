import hashlib
import logging
from typing import List
import numpy as np
from services.etl.src.config import config

logger = logging.getLogger(__name__)

class EmbeddingService:
    """
    Standalone embedding generation service. Decouples text embedding computation
    from database loading logic to allow swapping models (MiniLM -> BGE -> OpenAI -> Voyage)
    without modifying ETL loader modules. Uses deterministic seed hashing for reproducible testing.
    """

    def __init__(self, model_name: str = config.embedding_model, dimension: int = config.embedding_dimension):
        self.model_name = model_name
        self.dimension = dimension

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generates a normalized deterministic synthetic embedding vector of size self.dimension
        from the input text SHA-256 hash. Guarantees 100% deterministic reproducibility across runs.
        """
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
