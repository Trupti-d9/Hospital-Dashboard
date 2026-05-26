from fastapi import APIRouter
from pydantic import BaseModel
from rag.query_engine import query_rag

router = APIRouter()

class ChatPayload(BaseModel):
    message: str
    user: str = "CEO"

@router.post("/chat")
def chat_with_concierge(payload: ChatPayload):
    """
    RAG-powered AI concierge endpoint using OpenRouter.
    """
    try:
        response = query_rag(payload.message)
        return {"reply": response}
    except Exception as e:
        return {"reply": "Sorry, I am currently unable to reach the knowledge base.", "error": str(e)}
