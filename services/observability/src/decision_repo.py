import json
import logging
from typing import List, Dict, Any, Optional
import psycopg
from scof_shared.schemas.decision_record import DecisionRecord

from .embedding_client import EmbeddingClient
from .database import get_db_url

logger = logging.getLogger(__name__)

class DecisionRepository:
    def __init__(self, db_conn: psycopg.AsyncConnection):
        self.conn = db_conn
        self.embed_client = EmbeddingClient()

    async def save_decision(self, decision: DecisionRecord, trace_id: str) -> None:
        decision_sql = """
            INSERT INTO scof.decision_records (
                id, scenario_id, consensus_bundle_id, source_bundle_id, trace_id,
                decision_type, recommendation, confidence, priority, created_by,
                outcome, status, wcs, escalation_tier, decision_method,
                reasoning_trail, meeting_log_entries, created_at
            )
            VALUES (
                %s, %s, %s, %s, %s,
                'CONSENSUS', %s, %s, 'HIGH', 'CD2F_ENGINE',
                'COMPLETED', 'ACTIVE', %s, %s, %s,
                %s, %s, %s
            )
            ON CONFLICT (id) DO NOTHING;
        """
        
        reasoning_trail_json = json.dumps([step.model_dump(mode="json") for step in decision.reasoning_trail])
        meeting_log_json = json.dumps([log.model_dump(mode="json") for log in decision.meeting_log_entries])
        
        await self.conn.execute(
            decision_sql,
            (
                decision.decision_id,
                decision.scenario_id,
                decision.consensus_bundle_id,
                decision.source_bundle_id,
                trace_id,
                decision.final_recommendation or "No recommendation",
                decision.decision_confidence,
                decision.weighted_consensus_stability,
                decision.escalation_tier,
                decision.decision_method,
                reasoning_trail_json,
                meeting_log_json,
                decision.timestamp
            )
        )
        
        if decision.final_recommendation:
            embedding = self.embed_client.generate_embedding(decision.final_recommendation)
            vector_str = f"[{','.join(str(x) for x in embedding)}]"
            
            embedding_sql = """
                INSERT INTO scof.embeddings (
                    id, entity_type, entity_id, content_text, embedding_model,
                    embedding_dimension, embedding, metadata_json
                )
                VALUES (
                    gen_random_uuid()::varchar, 'decision', %s, %s, %s,
                    %s, %s::vector, %s
                )
                ON CONFLICT (entity_type, entity_id, content_text) 
                DO UPDATE SET embedding = EXCLUDED.embedding;
            """
            metadata_json = json.dumps({
                "scenario_id": decision.scenario_id,
                "escalation_tier": decision.escalation_tier
            })
            await self.conn.execute(
                embedding_sql,
                (
                    decision.decision_id,
                    decision.final_recommendation,
                    self.embed_client.model_name,
                    self.embed_client.dimension,
                    vector_str,
                    metadata_json
                )
            )

    async def get_decision(self, decision_id: str) -> Optional[Dict[str, Any]]:
        sql = """
            SELECT id, scenario_id, consensus_bundle_id, source_bundle_id, trace_id,
                   decision_type, recommendation, confidence, priority,
                   outcome, status, wcs, escalation_tier, decision_method,
                   reasoning_trail, meeting_log_entries, created_at
            FROM scof.decision_records
            WHERE id = %s
        """
        async with self.conn.cursor() as cur:
            await cur.execute(sql, (decision_id,))
            row = await cur.fetchone()
            
        if not row:
            return None
            
        return {
            "decision_id": row[0],
            "scenario_id": row[1],
            "consensus_bundle_id": row[2],
            "source_bundle_id": row[3],
            "trace_id": row[4],
            "decision_type": row[5],
            "final_recommendation": row[6],
            "decision_confidence": float(row[7]),
            "priority": row[8],
            "outcome": row[9],
            "status": row[10],
            "weighted_consensus_stability": float(row[11]) if row[11] is not None else None,
            "escalation_tier": row[12],
            "decision_method": row[13],
            "reasoning_trail": row[14],
            "meeting_log_entries": row[15],
            "timestamp": row[16]
        }
        
    async def get_decisions_by_scenario(self, scenario_id: str) -> List[Dict[str, Any]]:
        sql = """
            SELECT id, escalation_tier, recommendation, confidence, created_at
            FROM scof.decision_records
            WHERE scenario_id = %s
            ORDER BY created_at DESC
        """
        results = []
        async with self.conn.cursor() as cur:
            await cur.execute(sql, (scenario_id,))
            rows = await cur.fetchall()
            for row in rows:
                results.append({
                    "decision_id": row[0],
                    "escalation_tier": row[1],
                    "recommendation": row[2],
                    "confidence": float(row[3]),
                    "timestamp": row[4]
                })
        return results

    async def search_similar_decisions(self, query_text: str, limit: int = 5) -> List[Dict[str, Any]]:
        embedding = self.embed_client.generate_embedding(query_text)
        vector_str = f"[{','.join(str(x) for x in embedding)}]"
        
        sql = """
            SELECT 
                e.entity_id as decision_id,
                e.content_text as recommendation,
                1 - (e.embedding <=> %s::vector) AS similarity_score,
                d.escalation_tier,
                d.confidence
            FROM scof.embeddings e
            JOIN scof.decision_records d ON e.entity_id = d.id
            WHERE e.entity_type = 'decision'
            ORDER BY e.embedding <=> %s::vector
            LIMIT %s;
        """
        
        results = []
        async with self.conn.cursor() as cur:
            await cur.execute(sql, (vector_str, vector_str, limit))
            rows = await cur.fetchall()
            for row in rows:
                results.append({
                    "decision_id": row[0],
                    "recommendation": row[1],
                    "similarity_score": float(row[2]),
                    "escalation_tier": row[3],
                    "confidence": float(row[4])
                })
        return results
