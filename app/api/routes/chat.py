import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.memory import context_builder, history_service, summarization_service
from app.models.request_model import QueryRequest
from app.models.user import User
from app.services import session_service
from app.services.rag_service import RAGService

router = APIRouter(tags=["chat"], prefix="/api/chat")

rag_service = RAGService()


def _resolve_session(db: Session, user: User, session_id):
    """Return the requested session or create a fresh one for the user."""
    if session_id:
        existing = session_service.get_session(db, user, session_id)
        if existing is not None:
            return existing
    return session_service.create_session(db, user)


def _products_to_metadata(products) -> list:
    serialized = []
    for product in products or []:
        if hasattr(product, "model_dump"):
            serialized.append(product.model_dump(mode="json"))
        else:
            serialized.append(product)
    return serialized


@router.post("/ask")
async def ask_question(
    request: QueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = _resolve_session(db, current_user, request.session_id)

    summary_text, recent = context_builder.build_context(db, session.id)
    history_text = context_builder.format_history(recent)

    history_service.add_message(db, session.id, "user", request.query)

    result = rag_service.ask(
        request.query,
        history_text=history_text,
        summary_text=summary_text,
    )

    answer = result.get("answer", "")
    products = result.get("productsSuggestions", [])
    history_service.add_message(
        db,
        session.id,
        "assistant",
        answer,
        metadata={"products": _products_to_metadata(products)},
    )

    summarization_service.maybe_summarize(db, session.id)

    result["session_id"] = str(session.id)
    return result


@router.post("/ask/stream")
async def ask_question_stream(
    request: QueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Stream the RAG response token by token within a persisted session."""
    session = _resolve_session(db, current_user, request.session_id)

    summary_text, recent = context_builder.build_context(db, session.id)
    history_text = context_builder.format_history(recent)

    history_service.add_message(db, session.id, "user", request.query)

    def stream_generator():
        last_chunk = None
        try:
            for chunk in rag_service.ask_stream(
                request.query,
                history_text=history_text,
                summary_text=summary_text,
            ):
                last_chunk = chunk
                yield f"data: {chunk}\n\n"
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"
            return

        # Persist the assistant turn once streaming has completed.
        try:
            if last_chunk:
                parsed = json.loads(last_chunk)
                history_service.add_message(
                    db,
                    session.id,
                    "assistant",
                    parsed.get("answer", ""),
                    metadata={"products": parsed.get("productsSuggestions", [])},
                )
                summarization_service.maybe_summarize(db, session.id)
        except Exception:
            pass

    return StreamingResponse(
        stream_generator(),
        media_type="text/event-stream",
        headers={"X-Session-Id": str(session.id)},
    )
