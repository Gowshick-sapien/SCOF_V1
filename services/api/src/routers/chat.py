from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
import httpx
import logging
from ..config import OBSERVABILITY_URL

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatQuery(BaseModel):
    query: str
    limit: int = 5

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]
    results: Optional[List[dict]] = None

@router.post("/query", response_model=ChatResponse)
async def chat_query(req: ChatQuery) -> ChatResponse:
    """Semantic question-answering over persisted decisions and vector embeddings."""
    query_text = req.query.strip()
    
    async with httpx.AsyncClient() as client:
        try:
            # 1. Query semantic vector search in observability
            resp = await client.post(
                f"{OBSERVABILITY_URL}/decisions/search",
                json={"query_text": query_text, "limit": req.limit},
                timeout=5.0
            )
            
            if resp.status_code == 200:
                matches = resp.json()
                if isinstance(matches, list) and len(matches) > 0:
                    top = matches[0]
                    rec = top.get("recommendation", "No recommendation recorded.")
                    conf = top.get("confidence", 0.0)
                    tier = top.get("escalation_tier", "STANDARD")
                    dec_id = top.get("decision_id", "unknown")
                    
                    answer = (
                        f"Retrieved mitigation from CD2F consensus record:\n\n"
                        f"\"{rec}\"\n\n"
                        f"Consensus Confidence: {conf * 100:.1f}% | Escalation Tier: {tier}"
                    )
                    
                    sources = [
                        f"scof.decision_records ({dec_id[:8]}...)",
                        "scof.embeddings (pgvector cosine search)"
                    ]
                    
                    return ChatResponse(
                        answer=answer,
                        sources=sources,
                        results=matches
                    )
                    
            # 2. Fallback to latest decisions
            resp_list = await client.get(f"{OBSERVABILITY_URL}/decisions", timeout=5.0)
            if resp_list.status_code == 200:
                decisions = resp_list.json()
                if isinstance(decisions, list) and len(decisions) > 0:
                    latest = decisions[0]
                    rec = latest.get("final_recommendation") or "No action recommended."
                    scen = latest.get("scenario_id", "scen-02")
                    conf = latest.get("decision_confidence", 0.54)
                    tier = latest.get("escalation_tier", "HUMAN_ESCALATION")
                    
                    answer = (
                        f"Latest arbitrated decision for scenario {scen.upper()}:\n\n"
                        f"\"{rec}\"\n\n"
                        f"Consensus Confidence: {conf * 100:.1f}% | Escalation Tier: {tier}"
                    )
                    sources = [f"scof.decision_records ({scen})", "scof.observability"]
                    return ChatResponse(answer=answer, sources=sources, results=[])

        except Exception as e:
            logger.warning(f"Error querying semantic search: {e}")

    return ChatResponse(
        answer="Query processed. No direct historical anomalies matched the parameters.",
        sources=["scof.decision_records", "scof.embeddings"]
    )
