from fastapi import APIRouter
from fastapi.responses import StreamingResponse
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


@router.post("/ask/stream")
async def ask_question_stream(request: QueryRequest):
    """Stream the RAG response token by token."""
    def stream_generator():
        try:
            for chunk in rag_service.ask_stream(request.query):
                yield f"data: {chunk}\n\n"
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"
    
    return StreamingResponse(stream_generator(), media_type="text/event-stream")
