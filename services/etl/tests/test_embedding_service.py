import pytest
from services.etl.src.embedding_service import EmbeddingService

def test_embedding_service_dimension_and_determinism():
    service = EmbeddingService(model_name="all-MiniLM-L6-v2", dimension=384)
    
    vec1 = service.generate_embedding("Test disruption text for supplier rerouting.")
    vec2 = service.generate_embedding("Test disruption text for supplier rerouting.")
    vec3 = service.generate_embedding("Different text for warehouse storage.")

    assert len(vec1) == 384
    assert len(vec2) == 384
    assert vec1 == vec2  # Determinism check
    assert vec1 != vec3  # Non-identical text produces different vector

def test_embedding_service_batch():
    service = EmbeddingService(dimension=384)
    texts = ["Text A", "Text B", "Text C"]
    batch_vecs = service.generate_batch_embeddings(texts)

    assert len(batch_vecs) == 3
    for vec in batch_vecs:
        assert len(vec) == 384
