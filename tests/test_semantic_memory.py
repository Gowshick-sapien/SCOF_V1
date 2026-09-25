"""
Unit and Integration Test Suite for Deliverable D02 Semantic Memory Substrate
-----------------------------------------------------------------------------
Validates:
  1. Text Canonicalization and Content Hashing
  2. Multi-Run Identity Collision Resistance (inclusion of run_id)
  3. Provider Dimension and Normalization Invariants (384d)
  4. Real Model Semantic Ranking and Negative Margin Separation
  5. Relational Provenance Validation against Materialized SCOF Entities
"""

import math
import os
import sys
from pathlib import Path
import unittest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT / "shared") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "shared"))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scof_shared.knowledge.embedding_config import EmbeddingSystemConfig, ModelSpec
from scof_shared.knowledge.embedding_provider import (
    MockEmbeddingProvider,
    SentenceTransformersProvider,
    create_embedding_provider
)
from scof_shared.knowledge.semantic_memory_store import (
    canonicalize_text,
    SemanticDocumentInput,
    SemanticMemoryStore
)
from services.etl.src.seed_semantic_memory import (
    CONTROLLED_SEED_CORPUS,
    validate_relational_provenance
)

class TestSemanticMemorySubstrate(unittest.TestCase):

    def test_01_text_canonicalization(self):
        raw_1 = "Supplier delay causing stockout risk."
        raw_2 = "  Supplier   delay  causing  stockout  risk.\n\n"
        raw_3 = "Supplier delay causing stockout risk.\r\n"

        hash_1 = SemanticMemoryStore.compute_content_hash(raw_1)
        hash_2 = SemanticMemoryStore.compute_content_hash(raw_2)
        hash_3 = SemanticMemoryStore.compute_content_hash(raw_3)

        self.assertEqual(hash_1, hash_2)
        self.assertEqual(hash_2, hash_3)
        self.assertEqual(len(hash_1), 64)

    def test_02_multi_run_identity_collision_resistance(self):
        doc_run_1 = SemanticDocumentInput(
            document_type="AGENT_EVIDENCE",
            content="Identical claim content",
            source_entity_type="FACILITY",
            source_entity_id="STR-001",
            scenario_id="SCEN-F3992CF4",
            run_id="RUN-20260921-01",
            agent_id="INVENTORY_AGENT",
            logical_key="stockout-alert"
        )
        doc_run_2 = SemanticDocumentInput(
            document_type="AGENT_EVIDENCE",
            content="Identical claim content",
            source_entity_type="FACILITY",
            source_entity_id="STR-001",
            scenario_id="SCEN-F3992CF4",
            run_id="RUN-20260921-02",  # Different execution run
            agent_id="INVENTORY_AGENT",
            logical_key="stockout-alert"
        )

        id_1 = SemanticMemoryStore.derive_document_id(doc_run_1)
        id_2 = SemanticMemoryStore.derive_document_id(doc_run_2)

        # Assert inclusion of run_id prevents overwriting across historical simulation runs
        self.assertNotEqual(id_1, id_2)
        self.assertTrue(id_1.startswith("SD-AGE-"))
        self.assertTrue(id_2.startswith("SD-AGE-"))

    def test_03_provider_dimension_assertion(self):
        mock_provider = MockEmbeddingProvider(model_id="mock-test-provider@1.0.0", dimension=384)
        self.assertEqual(mock_provider.dimension, 384)
        vec = mock_provider.embed_text("Supplier delay test sentence.")
        self.assertEqual(len(vec), 384)

        # Verify unit normalization: sum of squares == 1.0
        norm = math.sqrt(sum(x * x for x in vec))
        self.assertAlmostEqual(norm, 1.0, places=4)

    def test_04_sentence_transformers_dimension(self):
        spec = ModelSpec(
            provider="sentence-transformers",
            model_name="all-MiniLM-L6-v2",
            dimension=384,
            distance_metric="cosine",
            model_version="1.0.0",
            normalize_embeddings=True,
            device="cpu"
        )
        provider = SentenceTransformersProvider(spec, "sentence-transformers-minilm-l6-v2@1.0.0")
        self.assertEqual(provider.dimension, 384)

        vec = provider.embed_text("Supplier delay causing stockout risk.")
        self.assertEqual(len(vec), 384)
        norm = math.sqrt(sum(x * x for x in vec))
        self.assertAlmostEqual(norm, 1.0, places=4)

    def test_05_semantic_ranking_and_negative_separation(self):
        """
        Gate P7 Evaluation: Validates that the real embedding model retrieves
        the Target artifact at Rank 1 and exceeds hard and distant negatives.
        """
        spec = ModelSpec(
            provider="sentence-transformers",
            model_name="all-MiniLM-L6-v2",
            dimension=384,
            distance_metric="cosine",
            model_version="1.0.0",
            normalize_embeddings=True,
            device="cpu"
        )
        provider = SentenceTransformersProvider(spec, "sentence-transformers-minilm-l6-v2@1.0.0")

        query = "historical situation where supplier delay caused inventory stockout risk"
        q_vec = provider.embed_text(query)

        def cosine_similarity(v1, v2):
            return sum(a * b for a, b in zip(v1, v2))

        scores = {}
        for item in CONTROLLED_SEED_CORPUS:
            role = item["metadata_json"]["benchmark_role"]
            emb = provider.embed_text(item["content"])
            scores[role] = cosine_similarity(q_vec, emb)

        # Target verification
        target_score = scores["TARGET"]
        hard_neg_1 = scores["HARD_NEGATIVE_1"]  # Supplier delay -> rerouting
        hard_neg_2 = scores["HARD_NEGATIVE_2"]  # Stockout -> replenishment
        hard_neg_3 = scores["HARD_NEGATIVE_3"]  # Quality -> quarantine
        distant_neg = scores["DISTANT_NEGATIVE"] # Tax audit

        # 1. Target meets minimum baseline
        self.assertGreaterEqual(target_score, 0.45, f"Target similarity {target_score:.4f} < 0.45")

        # 2. Target strictly beats all hard negatives
        self.assertGreater(target_score, hard_neg_1, f"Target {target_score:.4f} did not beat hard neg 1 {hard_neg_1:.4f}")
        self.assertGreater(target_score, hard_neg_2, f"Target {target_score:.4f} did not beat hard neg 2 {hard_neg_2:.4f}")
        self.assertGreater(target_score, hard_neg_3, f"Target {target_score:.4f} did not beat hard neg 3 {hard_neg_3:.4f}")

        # 3. Target exceeds distant negative by minimum margin delta >= 0.20
        delta = target_score - distant_neg
        self.assertGreaterEqual(delta, 0.20, f"Separation delta {delta:.4f} < 0.20 over distant negative {distant_neg:.4f}")

    def test_06_relational_provenance_validation(self):
        """
        Gate P4 Validation: Validates that seed corpus entities exist in scof_relational.db.
        """
        # Test real existing entities from scof_relational.db
        self.assertTrue(validate_relational_provenance("SUPPLIER", "SUP-PR-001"))
        self.assertTrue(validate_relational_provenance("FACILITY", "STR-001"))
        self.assertTrue(validate_relational_provenance("PURCHASE_ORDER", "PO-2026-000001"))
        self.assertTrue(validate_relational_provenance("SKU", "APP-CHI-00001"))
        self.assertTrue(validate_relational_provenance("SCENARIO", "SCEN-F3992CF4"))

        # Test non-existent fictional entities are caught
        self.assertFalse(validate_relational_provenance("SUPPLIER", "SUPP-DOES-NOT-EXIST"))
        self.assertFalse(validate_relational_provenance("FACILITY", "STR-NONEXISTENT"))

if __name__ == "__main__":
    unittest.main()
