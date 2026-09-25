from abc import ABC, abstractmethod
import hashlib
import math
from typing import List
from scof_shared.knowledge.embedding_config import ModelSpec

class EmbeddingProvider(ABC):
    @property
    @abstractmethod
    def model_id(self) -> str:
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        pass

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        pass

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        pass


class MockEmbeddingProvider(EmbeddingProvider):
    """
    Deterministic pseudo-embedding provider for testing schema, persistence, and interfaces.
    Must never be used for semantic-quality evaluation (Gate P7).
    """
    def __init__(self, model_id: str = "mock-test-provider@1.0.0", dimension: int = 384):
        self._model_id = model_id
        self._dim = dimension

    @property
    def model_id(self) -> str:
        return self._model_id

    @property
    def dimension(self) -> int:
        return self._dim

    def embed_text(self, text: str) -> List[float]:
        vec = []
        for i in range(self._dim):
            seed = f"{text}_{i}".encode("utf-8")
            h = int(hashlib.md5(seed).hexdigest()[:8], 16)
            vec.append((h / 0xFFFFFFFF) * 2.0 - 1.0)
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        norm_vec = [x / norm for x in vec]
        assert len(norm_vec) == self._dim, f"Output dimension mismatch: expected {self._dim}, got {len(norm_vec)}"
        return norm_vec

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_text(t) for t in texts]


class SentenceTransformersProvider(EmbeddingProvider):
    """Authoritative local embedding provider using all-MiniLM-L6-v2."""
    def __init__(self, spec: ModelSpec, model_id: str):
        self._spec = spec
        self._model_id = model_id
        from sentence_transformers import SentenceTransformer
        self._model = SentenceTransformer(spec.model_name, device=spec.device)

    @property
    def model_id(self) -> str:
        return self._model_id

    @property
    def dimension(self) -> int:
        return self._spec.dimension

    def embed_text(self, text: str) -> List[float]:
        embedding = self._model.encode(
            text,
            normalize_embeddings=self._spec.normalize_embeddings,
            show_progress_bar=False
        )
        res = embedding.tolist()
        assert len(res) == self._spec.dimension, f"Output dimension mismatch: expected {self._spec.dimension}, got {len(res)}"
        return res

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        embeddings = self._model.encode(
            texts,
            batch_size=self._spec.batch_size,
            normalize_embeddings=self._spec.normalize_embeddings,
            show_progress_bar=False
        )
        batch_res = [e.tolist() for e in embeddings]
        for item in batch_res:
            assert len(item) == self._spec.dimension, f"Batch item dimension mismatch: expected {self._spec.dimension}, got {len(item)}"
        return batch_res


def create_embedding_provider(spec: ModelSpec, model_id: str) -> EmbeddingProvider:
    if spec.provider == "sentence-transformers":
        return SentenceTransformersProvider(spec, model_id)
    elif spec.provider == "mock":
        return MockEmbeddingProvider(model_id, spec.dimension)
    raise ValueError(
        f"Unsupported embedding provider: '{spec.provider}'. "
        "Only 'sentence-transformers' and 'mock' are supported in Deliverable D02."
    )
