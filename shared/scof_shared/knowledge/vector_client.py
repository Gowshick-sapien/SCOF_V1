import logging
import os
from typing import Any, Dict, List, Optional
from scof_shared.knowledge.semantic_memory_store import (
    SemanticMemoryStore,
    SemanticDocumentInput,
    SemanticSearchResult,
)

logger = logging.getLogger(__name__)

class PgVectorClient:
    """
    Backward-compatibility adapter wrapping SemanticMemoryStore.
    Preserves V1 method signatures while routing storage and retrieval
    through the authoritative D02 Semantic Memory Substrate.
    """

    def __init__(self, db_url: Optional[str] = None):
        self.store = SemanticMemoryStore(db_url=db_url)

    def search_similar_embeddings(
        self,
        query_vector: List[float],
        entity_type: str = "decision",
        model_name: str = "all-MiniLM-L6-v2",
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        # Forward directly to SemanticMemoryStore exact search
        query_str = f"[{','.join(str(x) for x in query_vector)}]"
        sql = """
        SELECT 
            d.semantic_document_id AS id,
            d.source_entity_type AS entity_type,
            d.source_entity_id AS entity_id,
            d.content AS content_text,
            e.model_id AS embedding_model,
            384 AS embedding_dimension,
            d.metadata_json,
            1 - (e.embedding <=> %(query_vec)s::vector) AS similarity_score
        FROM scof.semantic_embedding e
        JOIN scof.semantic_document d ON d.semantic_document_id = e.semantic_document_id
        WHERE e.is_current = TRUE
        ORDER BY e.embedding <=> %(query_vec)s::vector
        LIMIT %(limit_k)s;
        """
        results = []
        with self.store._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, {"query_vec": query_str, "limit_k": limit})
                for row in cur.fetchall():
                    results.append({
                        "id": row[0],
                        "entity_type": row[1],
                        "entity_id": row[2],
                        "content_text": row[3],
                        "embedding_model": row[4],
                        "embedding_dimension": row[5],
                        "metadata_json": row[6],
                        "similarity_score": float(row[7])
                    })
        return results

    def get_decision_with_evidence(self, decision_id: str) -> Optional[Dict[str, Any]]:
        sql = """
        SELECT 
            semantic_document_id, title, content, source_entity_type,
            source_entity_id, scenario_id, run_id, agent_id, metadata_json, created_at
        FROM scof.semantic_document
        WHERE semantic_document_id = %(id)s;
        """
        with self.store._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, {"id": decision_id})
                row = cur.fetchone()
                if not row:
                    return None
                return {
                    "id": row[0],
                    "title": row[1],
                    "content": row[2],
                    "source_entity_type": row[3],
                    "source_entity_id": row[4],
                    "scenario_id": row[5],
                    "run_id": row[6],
                    "agent_id": row[7],
                    "metadata_json": row[8],
                    "created_at": row[9]
                }
