from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatQuery(BaseModel):
    query: str
    limit: int = 5

@router.post("/query")
async def chat_query(req: ChatQuery):
    # Mock for MVP
    return {
        "results": [
            {
                "text": f"Found result for: {req.query}",
                "method": "semantic_retrieval",
                "score": 0.99
            }
        ]
    }
