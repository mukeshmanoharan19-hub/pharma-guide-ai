from fastapi import APIRouter
from app.models.request_model import QueryRequest
from app.services.rag_service import RAGService

router = APIRouter(tags=["chat"], prefix="/api/chat")

rag_service = RAGService()

@router.post("/ask")

async def ask_question(
    request: QueryRequest
):
    return rag_service.ask(
        request.query
    )