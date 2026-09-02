from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import Optional
import uuid
import datetime
import json
import os
import psycopg

from ..events.topics import TOPIC_DISRUPTIONS_TRIGGERED


def get_event_bus(request: Request):
    return request.app.state.event_bus


def get_redis(request: Request):
    return request.app.state.redis_client


router = APIRouter(prefix="/scenarios", tags=["scenarios"])


class TriggerRequest(BaseModel):
    scenario_id: str
    disruption_type: Optional[str] = None
    target_entity_id: Optional[str] = None
    severity: Optional[int] = None


class ReplayRequest(BaseModel):
    event_id: str


def get_db_connection():
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "scof")
    user = os.getenv("POSTGRES_USER", "scof")
    password = os.getenv("POSTGRES_PASSWORD", "changeme")

    return psycopg.connect(
        host=host,
        port=port,
        dbname=db,
        user=user,
        password=password,
    )


@router.get("")
async def list_scenarios():
    """List persisted SCOF scenarios with their disruption context from PostgreSQL."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    s.scenario_id,
                    s.run_id,
                    s.name,
                    s.description,
                    s.random_seed,
                    s.created_at,
                    d.disruption_type,
                    d.target_entity_id,
                    d.severity
                FROM scof.scenarios s
                LEFT JOIN LATERAL (
                    SELECT disruption_type, target_entity_id, severity
                    FROM scof.disruption_events de
                    WHERE de.scenario_id = s.scenario_id
                    ORDER BY de.created_at, de.id
                    LIMIT 1
                ) d ON true
                ORDER BY s.created_at, s.scenario_id
                """
            )

            rows = cur.fetchall()

    return {
        "scenarios": [
            {
                "scenario_id": row[0],
                "run_id": row[1],
                "name": row[2],
                "description": row[3],
                "random_seed": row[4],
                "created_at": row[5].isoformat() if row[5] else None,
                "disruption_type": row[6] or "none",
                "target_entity": row[7] or "global",
                "severity": row[8] or 1,
            }
            for row in rows
        ]
    }


@router.post("/trigger")
async def trigger_scenario(
    req: TriggerRequest,
    request: Request,
    bus=Depends(get_event_bus),
):
    """
    Trigger a persisted scenario using its real database context.

    For scenarios with disruption events, the first persisted disruption
    is used to construct the ScenarioContext expected by the Coordinator.
    """

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    scenario_id,
                    run_id,
                    name,
                    description,
                    random_seed
                FROM scof.scenarios
                WHERE scenario_id = %s
                """,
                (req.scenario_id,),
            )

            scenario = cur.fetchone()

            if not scenario:
                raise HTTPException(
                    status_code=404,
                    detail=f"Scenario '{req.scenario_id}' not found",
                )

            scenario_id, run_id, name, description, random_seed = scenario

            cur.execute(
                """
                SELECT
                    id,
                    disruption_type,
                    target_entity_type,
                    target_entity_id,
                    severity,
                    start_date,
                    end_date
                FROM scof.disruption_events
                WHERE scenario_id = %s
                ORDER BY created_at, id
                LIMIT 1
                """,
                (scenario_id,),
            )

            disruption = cur.fetchone()

    # Construct the exact ScenarioContext expected by the Coordinator.
    if disruption:
        (
            disruption_id,
            disruption_type,
            target_entity_type,
            target_entity_id,
            severity,
            start_date,
            end_date,
        ) = disruption

        context = {
            "scenario_id": scenario_id,
            "run_id": run_id,
            "disruption_id": disruption_id,
            "disruption_type": req.disruption_type or disruption_type,
            "target_entity_type": target_entity_type,
            "target_entity_id": req.target_entity_id or target_entity_id,
            "severity": req.severity or severity,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
        }
    else:
        # Baseline scenarios legitimately have no disruption event.
        context = {
            "scenario_id": scenario_id,
            "run_id": run_id,
            "disruption_type": req.disruption_type or "none",
            "target_entity_type": "global",
            "target_entity_id": req.target_entity_id or "global",
            "severity": req.severity or 1,
        }

    trace_id = request.state.trace_id
    event_id = f"evt-{uuid.uuid4().hex}"

    envelope = {
        "event_id": event_id,
        "event_type": "disruption.triggered",
        "schema_version": "1.0.0",
        "producer": "scof-api",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "correlation": {
            "trace_id": trace_id,
            "scenario_id": scenario_id,
            "profile_version": "1.0.0",
            "request_id": request.state.request_id,
        },
        "payload": {
            "scenario_context": context
        },
    }

    redis_client = get_redis(request)

    await redis_client.setex(
        f"published_events:{event_id}",
        604800,
        json.dumps(envelope),
    )

    await bus.publish(
        TOPIC_DISRUPTIONS_TRIGGERED,
        key=scenario_id,
        envelope=envelope,
    )

    return {
        "event_id": event_id,
        "trace_id": trace_id,
        "status": "TRIGGERED",
        "scenario_id": scenario_id,
    }


@router.post("/replay")
async def replay_scenario(
    req: ReplayRequest,
    request: Request,
    bus=Depends(get_event_bus),
    redis_client=Depends(get_redis),
):
    original_event_str = await redis_client.get(
        f"published_events:{req.event_id}"
    )

    if not original_event_str:
        raise HTTPException(
            status_code=404,
            detail="Original event not found or expired",
        )

    original_event = json.loads(original_event_str)

    new_event_id = f"evt-{uuid.uuid4().hex}"
    new_trace_id = request.state.trace_id

    new_envelope = {
        "event_id": new_event_id,
        "original_event_id": req.event_id,
        "event_type": original_event.get(
            "event_type",
            "disruption.triggered",
        ),
        "schema_version": "1.0.0",
        "producer": "scof-api",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "correlation": {
            "trace_id": new_trace_id,
            "scenario_id": original_event.get(
                "correlation",
                {},
            ).get("scenario_id", ""),
            "profile_version": original_event.get(
                "correlation",
                {},
            ).get("profile_version", "1.0.0"),
            "request_id": request.state.request_id,
        },
        "payload": original_event.get("payload", {}),
    }

    await redis_client.setex(
        f"published_events:{new_event_id}",
        604800,
        json.dumps(new_envelope),
    )

    key = new_envelope["correlation"]["scenario_id"]

    await bus.publish(
        TOPIC_DISRUPTIONS_TRIGGERED,
        key=key,
        envelope=new_envelope,
    )

    return {
        "event_id": new_event_id,
        "trace_id": new_trace_id,
        "status": "REPLAY_TRIGGERED",
    }