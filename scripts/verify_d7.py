#!/usr/bin/env python3
"""
Verification script for Deliverable D07: Observability & Explainability Backend.
Executes an end-to-end orchestration flow, triggers consensus, and verifies persistence.
"""

import asyncio
import httpx
import logging
import uuid
import time
import sys
from pathlib import Path
from typing import Dict, Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "shared"))

from scof_shared.schemas.scenario_context import ScenarioContext

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify_d7")

async def verify_d7_observability():
    logger.info("Starting D7 Observability Verification...")

    scenario_id = "scen-01"
    trace_id = f"TRACE-{uuid.uuid4().hex[:6].upper()}"
    bundle_id = f"BUNDLE-{uuid.uuid4().hex[:6].upper()}"

    context = ScenarioContext(
        scenario_id=scenario_id,
        trigger_event="SUPPLIER_DELAY",
        affected_entities=["SUPP_ALPHA"],
        priority="HIGH",
        timestamp=time.time(),
        metadata={}
    )

    # We assume Docker Compose is running with coordinator on 8010, observability on 8030
    async with httpx.AsyncClient() as client:
        # 1. Trigger Orchestration (D5 -> D6 -> D7)
        logger.info(f"Triggering Orchestration (Trace: {trace_id})...")
        try:
            resp = await client.post(
                "http://localhost:8010/orchestrate",
                json=context.model_dump(),
                headers={
                    "X-Trace-ID": trace_id,
                    "X-Bundle-ID": bundle_id
                },
                timeout=30.0
            )
            resp.raise_for_status()
            bundle = resp.json()
            decision_id = bundle.get("consensus_decision_id")
            logger.info(f"Orchestration returned ClaimBundle '{bundle.get('bundle_id')}'")
        except Exception as e:
            logger.error(f"Failed to orchestrate: {e}")
            return False

        # Wait a moment for async persistence (though it should be sync, it's safe to sleep)
        await asyncio.sleep(1)

        # 2. Verify D7 Persistence by Scenario ID
        logger.info(f"Verifying decisions for scenario '{scenario_id}' in D7...")
        try:
            resp = await client.get(
                f"http://localhost:8030/scenarios/{scenario_id}/decisions",
                timeout=5.0
            )
            resp.raise_for_status()
            decisions = resp.json()
            if not decisions:
                logger.error("No decisions found in D7 for the scenario.")
                return False
                
            persisted_decision = decisions[0]
            logger.info(f"Found Persisted Decision: {persisted_decision['decision_id']} "
                        f"(Tier: {persisted_decision['escalation_tier']}, "
                        f"Confidence: {persisted_decision['confidence']})")
        except Exception as e:
            logger.error(f"Failed to fetch decisions from D7: {e}")
            return False

        # 3. Verify Full Trace Retrieval
        logger.info(f"Verifying full decision trace retrieval...")
        try:
            resp = await client.get(
                f"http://localhost:8030/decisions/{persisted_decision['decision_id']}",
                timeout=5.0
            )
            resp.raise_for_status()
            trace = resp.json()
            if trace.get("trace_id") != trace_id:
                logger.error(f"Trace ID mismatch: expected {trace_id}, got {trace.get('trace_id')}")
                return False
            logger.info(f"Decision Trace fetched successfully. Reasoning steps: {len(trace.get('reasoning_trail', []))}")
        except Exception as e:
            logger.error(f"Failed to fetch decision trace from D7: {e}")
            return False

        # 4. Verify Semantic Search
        logger.info(f"Verifying semantic search...")
        try:
            query = "inventory shortage optimization"
            resp = await client.post(
                "http://localhost:8030/decisions/search",
                json={"query_text": query, "limit": 3},
                timeout=5.0
            )
            resp.raise_for_status()
            search_results = resp.json()
            logger.info(f"Semantic search for '{query}' returned {len(search_results)} results:")
            for idx, res in enumerate(search_results):
                logger.info(f"  {idx+1}. Score: {res.get('similarity_score', 0):.4f} | Tier: {res.get('escalation_tier', 'UNKNOWN')}")
        except Exception as e:
            logger.error(f"Failed to perform semantic search: {e}")
            return False

    logger.info("D7 Observability Verification Successful! ")
    return True

if __name__ == "__main__":
    success = asyncio.run(verify_d7_observability())
    if not success:
        exit(1)
