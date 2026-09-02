from fastapi import APIRouter, HTTPException
import httpx
from ..config import OBSERVABILITY_URL

router = APIRouter(prefix="/decisions", tags=["decisions"])

@router.get("")
async def list_decisions():
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{OBSERVABILITY_URL}/decisions")
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return []
            raise HTTPException(status_code=502, detail="Upstream observability error")
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Observability unreachable: {e}")

@router.get("/{decision_id}/log")
async def get_decision_log(decision_id: str):
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{OBSERVABILITY_URL}/decisions/{decision_id}")
            resp.raise_for_status()
            decision = resp.json()
            entries = decision.get("meeting_log_entries", [])
            return {
                "meeting_log": entries,
                "meeting_log_entries": entries
            }
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise HTTPException(status_code=404, detail="Decision not found")
            raise HTTPException(status_code=502, detail="Upstream observability error")
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Observability unreachable: {e}")

@router.get("/{decision_id}/confidence")
async def get_decision_confidence(decision_id: str):
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{OBSERVABILITY_URL}/decisions/{decision_id}")
            resp.raise_for_status()
            decision = resp.json()
            return {
                "decision_confidence": decision.get("decision_confidence", 0.0),
                "weighted_consensus_stability": decision.get("weighted_consensus_stability", 0.0),
                "agent_weights": decision.get("agent_weights", {}),
                "recommendation_tallies": decision.get("recommendation_tallies", {})
            }
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise HTTPException(status_code=404, detail="Decision not found")
            raise HTTPException(status_code=502, detail="Upstream observability error")
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Observability unreachable: {e}")

@router.get("/{decision_id}/trace")
async def get_decision_trace(decision_id: str):
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{OBSERVABILITY_URL}/decisions/{decision_id}")
            resp.raise_for_status()
            decision = resp.json()
            return {"reasoning_trail": decision.get("reasoning_trail", [])}
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise HTTPException(status_code=404, detail="Decision not found")
            raise HTTPException(status_code=502, detail="Upstream observability error")
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Observability unreachable: {e}")
