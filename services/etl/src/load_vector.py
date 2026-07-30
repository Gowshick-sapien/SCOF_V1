import json
import logging
from typing import Any, Dict, List
import psycopg
from services.etl.src.config import config

logger = logging.getLogger(__name__)

class VectorLoader:
    """
    High-performance Vector Loader executing batch executemany() SQL statements
    to populate decision_records, evidence_snippets, and embeddings tables.
    """

    def __init__(self, db_url: str = config.postgres_connection_string):
        self.db_url = db_url

    def _get_connection(self) -> psycopg.Connection:
        return psycopg.connect(self.db_url, autocommit=True, connect_timeout=3)

    def load_decisions(self, decisions: List[Dict[str, Any]]) -> None:
        if not decisions:
            return
        sql = """
        INSERT INTO scof.decision_records (
            id, scenario_id, run_id, disruption_id, decision_type, recommendation,
            confidence, priority, impact_summary, created_by, simulation_tick, outcome, status
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        ) ON CONFLICT (id) DO UPDATE SET
            recommendation = EXCLUDED.recommendation,
            confidence = EXCLUDED.confidence,
            priority = EXCLUDED.priority,
            impact_summary = EXCLUDED.impact_summary,
            outcome = EXCLUDED.outcome,
            status = EXCLUDED.status;
        """
        params = [
            (
                d["id"], d.get("scenario_id"), d.get("run_id"), d.get("disruption_id"),
                d["decision_type"], d["recommendation"], d["confidence"], d["priority"],
                d.get("impact_summary"), d.get("created_by", "SYSTEM"), d.get("simulation_tick", 0),
                d.get("outcome", "APPROVED"), d.get("status", "ACTIVE")
            )
            for d in decisions
        ]
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.executemany(sql, params)

    def load_evidence_snippets(self, snippets: List[Dict[str, Any]]) -> None:
        if not snippets:
            return
        sql = """
        INSERT INTO scof.evidence_snippets (
            id, decision_id, source_type, source_id, snippet_text, metadata_json
        ) VALUES (
            %s, %s, %s, %s, %s, %s
        ) ON CONFLICT (id) DO UPDATE SET
            snippet_text = EXCLUDED.snippet_text,
            metadata_json = EXCLUDED.metadata_json;
        """
        params = [
            (
                s["id"], s["decision_id"], s["source_type"], s["source_id"],
                s["snippet_text"], json.dumps(s.get("metadata_json", {}))
            )
            for s in snippets
        ]
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.executemany(sql, params)

    def load_embeddings(self, embedding_items: List[Dict[str, Any]]) -> None:
        if not embedding_items:
            return
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
        params = []
        for item in embedding_items:
            vector_str = f"[{','.join(str(x) for x in item['embedding'])}]"
            params.append((
                item["id"],
                item["entity_type"],
                item["entity_id"],
                item["content_text"],
                item.get("embedding_model", config.embedding_model),
                item.get("embedding_version", config.embedding_version),
                item.get("embedding_dimension", config.embedding_dimension),
                vector_str,
                json.dumps(item.get("metadata_json", {}))
            ))
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.executemany(sql, params)

    def load_all(self, payload: Dict[str, List[Dict[str, Any]]]) -> None:
        try:
            logger.info("Loading PostgreSQL Decision Records...")
            self.load_decisions(payload.get("decisions", []))
            logger.info("Loading PostgreSQL Evidence Snippets...")
            self.load_evidence_snippets(payload.get("evidence_snippets", []))
            logger.info("Loading PostgreSQL Vector Embeddings...")
            self.load_embeddings(payload.get("embedding_items", []))
            logger.info("PostgreSQL Vector Store Ingestion Complete.")
        except Exception as e:
            logger.warning("PostgreSQL database connection unavailable (%s). Skipped PostgreSQL write.", e)
