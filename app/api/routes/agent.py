"""Agentic chat endpoint backed by the LangGraph workflow (Phase 3).

This sits alongside the existing ``/api/chat`` routes. It streams the graph's
progress as Server-Sent Events and, as the final ``data:`` line, the structured
answer payload so the existing frontend streaming contract still works.

Conversation state is checkpointed by LangGraph keyed on ``thread_id`` (the
session id), so the workflow can resume/accumulate state across turns within the
same session.
"""

import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.agents.checkpointer import get_checkpointer
from app.agents.graph import build_agent_graph
from app.core.security import get_current_user
from app.db.database import get_db
from app.models.request_model import QueryRequest
from app.models.user import User
from app.observability.langsmith import runnable_config
from app.services import session_service

router = APIRouter(tags=["agent"], prefix="/api/agent")


def _resolve_session(db: Session, user: User, session_id):
    if session_id:
        existing = session_service.get_session(db, user, session_id)
        if existing is not None:
            return existing
    return session_service.create_session(db, user)


@router.post("/chat")
async def agent_chat(
    request: QueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = _resolve_session(db, current_user, request.session_id)
    thread_id = str(session.id)

    graph = build_agent_graph(
        db=db,
        user_id=current_user.id,
        checkpointer=get_checkpointer(),
    )

    config = runnable_config(
        run_name="agent.graph_request",
        tags=["phase10", "agent", "graph"],
        metadata={
            "route": "/api/agent/chat",
            "thread_id": thread_id,
            "user_id": current_user.id,
        },
        base={"configurable": {"thread_id": thread_id}},
    )
    input_state = {
        "user_id": current_user.id,
        "session_id": thread_id,
        "query": request.query,
        "messages": [],
    }

    def event_stream():
        final_response = None
        try:
            for update in graph.stream(
                input_state, config=config, stream_mode="updates"
            ):
                for node_name, delta in update.items():
                    progress = {"event": "progress", "node": node_name}
                    if delta and delta.get("intent") is not None:
                        progress["intent"] = delta["intent"]
                        progress["confidence"] = delta.get("intent_confidence")
                    if delta and delta.get("safety_level") is not None:
                        progress["safety_level"] = delta["safety_level"]
                        progress["safety_flags"] = delta.get("safety_flags") or []
                    yield f"data: {json.dumps(progress)}\n\n"
                    if delta and delta.get("final_response"):
                        final_response = delta["final_response"]
        except Exception as exc:
            yield f"data: [ERROR] {str(exc)}\n\n"
            return

        if final_response is None:
            final_response = {
                "answer": "No response generated.",
                "productsSuggestions": [],
            }
        final_response["session_id"] = thread_id
        yield f"data: {json.dumps(final_response)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"X-Session-Id": thread_id},
    )
