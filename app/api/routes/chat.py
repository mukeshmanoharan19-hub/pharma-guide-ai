from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.models.request_model import QueryRequest
from app.models.user import User
from app.core.security import get_current_user
from app.services.rag_service import RAGService

router = APIRouter(tags=["chat"], prefix="/api/chat")

rag_service = RAGService()


@router.post("/ask")
async def ask_question(
    request: QueryRequest,
    current_user: User = Depends(get_current_user),
):
    return rag_service.ask(
        request.query
    )


@router.post("/ask/stream")
async def ask_question_stream(
    request: QueryRequest,
    current_user: User = Depends(get_current_user),
):
    """Stream the RAG response token by token."""
    def stream_generator():
        try:
            for chunk in rag_service.ask_stream(request.query):
                yield f"data: {chunk}\n\n"
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"

    return StreamingResponse(stream_generator(), media_type="text/event-stream")
