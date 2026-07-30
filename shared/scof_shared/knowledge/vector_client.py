import os
import json
import logging
from typing import Any, Dict, List, Optional
import psycopg

logger = logging.getLogger(__name__)

class PgVectorClient:
    """
    Reusable pgvector Client providing vector insertion, similarity search,
    metadata tracking, and decision record access for SCOF services.
    """

    def __init__(self, db_url: Optional[str] = None):
        if db_url is None:
            user = os.getenv("POSTGRES_USER", "scof")
            pw = os.getenv("POSTGRES_PASSWORD", "changeme")
            host = os.getenv("POSTGRES_HOST", "localhost")
            port = os.getenv("POSTGRES_PORT", "5432")
            db = os.getenv("POSTGRES_DB", "scof")
            db_url = f"postgresql://{user}:{pw}@{host}:{port}/{db}"
        self.db_url = db_url

    def _get_connection(self) -> psycopg.Connection:
        return psycopg.connect(self.db_url, autocommit=True)

    def search_similar_embeddings(
        self,
        query_vector: List[float],
        entity_type: str = "decision",
        model_name: str = "all-MiniLM-L6-v2",
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        query_str = f"[{','.join(str(x) for x in query_vector)}]"
        sql = """
        SELECT 
            e.id,
            e.entity_type,
            e.entity_id,
            e.content_text,
            e.embedding_model,
            e.embedding_dimension,
            e.metadata_json,
            1 - (e.embedding <=> %s::vector) AS similarity_score
        FROM scof.embeddings e
        WHERE e.entity_type = %s
          AND e.embedding_model = %s
        ORDER BY e.embedding <=> %s::vector
        LIMIT %s;
        """
        results = []
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (query_str, entity_type, model_name, query_str, limit))
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
        sql_decision = """
        SELECT id, scenario_id, run_id, disruption_id, decision_type, recommendation,
               confidence, priority, impact_summary, created_by, simulation_tick, outcome, status, created_at
        FROM scof.decision_records
        WHERE id = %s;
        """
        sql_evidence = """
        SELECT id, source_type, source_id, snippet_text, metadata_json, created_at
        FROM scof.evidence_snippets
        WHERE decision_id = %s;
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql_decision, (decision_id,))
                dec_row = cur.fetchone()
                if not dec_row:
                    return None

                decision = {
                    "id": dec_row[0],
                    "scenario_id": dec_row[1],
                    "run_id": dec_row[2],
                    "disruption_id": dec_row[3],
                    "decision_type": dec_row[4],
                    "recommendation": dec_row[5],
                    "confidence": float(dec_row[6]),
                    "priority": dec_row[7],
                    "impact_summary": dec_row[8],
                    "created_by": dec_row[9],
                    "simulation_tick": dec_row[10],
                    "outcome": dec_row[11],
                    "status": dec_row[12],
                    "created_at": str(dec_row[13]),
                    "evidence": []
                }

                cur.execute(sql_evidence, (decision_id,))
                for ev_row in cur.fetchall():
                    decision["evidence"].append({
                        "id": ev_row[0],
                        "source_type": ev_row[1],
                        "source_id": ev_row[2],
                        "snippet_text": ev_row[3],
                        "metadata_json": ev_row[4],
                        "created_at": str(ev_row[5])
                    })

                return decision

    def insert_embedding_batch(self, batch: List[Dict[str, Any]]) -> None:
        sql = """
        INSERT INTO scof.embeddings (
            id, entity_type, entity_id, content_text, embedding_model,
            embedding_version, embedding_dimension, embedding, metadata_json
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s::vector, %s
        ) ON CONFLICT (id) DO UPDATE SET
            content_text = EXCLUDED.content_text,
            embedding = EXCLUDED.embedding,
            metadata_json = EXCLUDED.metadata_json;
        """
        params_list = []
        for item in batch:
            query_str = f"[{','.join(str(x) for x in item['embedding'])}]"
            params_list.append((
                item["id"],
                item["entity_type"],
                item["entity_id"],
                item["content_text"],
                item.get("embedding_model", "all-MiniLM-L6-v2"),
                item.get("embedding_version", "v1"),
                item.get("embedding_dimension", 384),
                query_str,
                json.dumps(item.get("metadata_json", {}))
            ))

        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.executemany(sql, params_list)
