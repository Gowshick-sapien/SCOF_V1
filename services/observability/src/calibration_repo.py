import json
import logging
import uuid
from typing import List, Dict, Any, Optional
import psycopg
from .models import CalibrationMetricsPayload

logger = logging.getLogger(__name__)

class CalibrationRepository:
    def __init__(self, db_conn: psycopg.AsyncConnection):
        self.conn = db_conn

    async def save_calibration(self, payload: CalibrationMetricsPayload) -> None:
        sql = """
            INSERT INTO scof.calibration_metrics (
                id, timestamp, recommendation_kappa, escalation_tier_kappa,
                sample_size, pass_status, report_data
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING;
        """
        
        report_data_json = json.dumps({
            "exact_match_rate": payload.exact_match_rate,
            "confusion_breakdown": payload.confusion_breakdown,
            "warnings": payload.warnings
        })
        
        await self.conn.execute(
            sql,
            (
                payload.id,
                payload.timestamp,
                payload.recommendation_kappa,
                payload.escalation_tier_kappa,
                payload.sample_size,
                payload.pass_status,
                report_data_json
            )
        )

    async def get_calibration_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        sql = """
            SELECT id, timestamp, recommendation_kappa, escalation_tier_kappa,
                   sample_size, pass_status, report_data
            FROM scof.calibration_metrics
            ORDER BY timestamp DESC
            LIMIT %s
        """
        
        results = []
        async with self.conn.cursor() as cur:
            await cur.execute(sql, (limit,))
            rows = await cur.fetchall()
            for row in rows:
                report_data = row[6] if isinstance(row[6], dict) else {}
                results.append({
                    "id": row[0],
                    "timestamp": row[1],
                    "recommendation_kappa": float(row[2]) if row[2] is not None else None,
                    "escalation_tier_kappa": float(row[3]) if row[3] is not None else None,
                    "sample_size": row[4],
                    "pass_status": row[5],
                    "exact_match_rate": float(report_data.get("exact_match_rate", 0.0)),
                    "confusion_breakdown": report_data.get("confusion_breakdown", {}),
                    "warnings": report_data.get("warnings", [])
                })
        return results
