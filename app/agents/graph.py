"""LangGraph agent workflow skeleton (Phase 3 foundation).

The graph wires up the node architecture that later phases flesh out:

    load_memory -> safety_screen -> supervisor -> general_rag
                -> synthesize_response -> persist_memory

Failures in the answering path are routed to ``error_handler`` which returns a
safe user-facing message. For now the supervisor always routes to a single
``general_rag`` node that reuses the existing RAG pipeline; Phase 4 adds real
intent detection and Phase 5 adds specialist agents.

The graph is rebuilt per request so node closures can capture the request-scoped
``db`` session and ``user_id`` without pushing non-serialisable objects through
the (checkpointed) state. The expensive parts — the checkpointer and the RAG
service — are process-wide singletons.
"""

from __future__ import annotations

import uuid

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, START, StateGraph
from loguru import logger
from sqlalchemy.orm import Session

from app.agents.state import GraphState
from app.memory import context_builder, history_service, summarization_service
from app.services.rag_service import get_rag_service

SAFE_FALLBACK_MESSAGE = (
    "Sorry, I ran into a problem while processing your request. "
    "Please try again in a moment."
)


def _coerce_session_id(session_id):
    """State carries the session id as a string; DB helpers expect a UUID."""
    if isinstance(session_id, uuid.UUID):
        return session_id
    return uuid.UUID(str(session_id))


def _products_to_list(products) -> list:
    serialized = []
    for product in products or []:
        if hasattr(product, "model_dump"):
            serialized.append(product.model_dump(mode="json"))
        else:
            serialized.append(product)
    return serialized


def build_agent_graph(db: Session, user_id: int, checkpointer=None):
    """Compile the agent graph with request-scoped dependencies bound in."""

    def load_memory(state: GraphState) -> dict:
        """Hydrate conversational context and persist the incoming user turn."""
        session_id = _coerce_session_id(state["session_id"])
        query = state["query"]

        summary_text, recent = context_builder.build_context(db, session_id)
        history_text = context_builder.format_history(recent)

        # Persist the user message *after* building context so the current turn
        # is not duplicated into the history we just assembled.
        history_service.add_message(db, session_id, "user", query)

        return {
            "memory_summary": summary_text,
            "history_text": history_text,
            "messages": [HumanMessage(content=query)],
        }

    def safety_screen(state: GraphState) -> dict:
        """Placeholder safety gate (real risk detection arrives in Phase 8)."""
        return {"safety_flags": []}

    def supervisor(state: GraphState) -> dict:
        """Placeholder intent router (real intent detection arrives in Phase 4)."""
        return {"intent": "general", "intent_confidence": 1.0}

    def general_rag(state: GraphState) -> dict:
        """Answer using the existing RAG pipeline."""
        try:
            rag = get_rag_service()
            result = rag.ask(
                state["query"],
                history_text=state.get("history_text"),
                summary_text=state.get("memory_summary"),
            )
            answer = result.get("answer", "")
            products = _products_to_list(result.get("productsSuggestions", []))
            return {
                "final_response": {
                    "answer": answer,
                    "productsSuggestions": products,
                },
                "messages": [AIMessage(content=answer)],
            }
        except Exception as exc:  # node-level error transition
            logger.exception(f"general_rag node failed: {exc}")
            return {"error": str(exc)}

    def synthesize_response(state: GraphState) -> dict:
        """Finalise the response payload (compression/merging lands in Phase 6)."""
        final = state.get("final_response")
        if not final:
            return {
                "final_response": {
                    "answer": SAFE_FALLBACK_MESSAGE,
                    "productsSuggestions": [],
                }
            }
        return {}

    def persist_memory(state: GraphState) -> dict:
        """Persist the assistant turn and trigger rolling summarisation."""
        session_id = _coerce_session_id(state["session_id"])
        final = state.get("final_response") or {}
        answer = final.get("answer", "")
        products = final.get("productsSuggestions", [])
        try:
            history_service.add_message(
                db,
                session_id,
                "assistant",
                answer,
                metadata={"products": products},
            )
            summarization_service.maybe_summarize(db, session_id)
        except Exception as exc:  # persistence must not break the response
            logger.warning(f"persist_memory node failed: {exc}")
        return {}

    def error_handler(state: GraphState) -> dict:
        """Convert any upstream error into a safe user-facing response."""
        logger.error(f"Agent error handled: {state.get('error')}")
        return {
            "final_response": {
                "answer": SAFE_FALLBACK_MESSAGE,
                "productsSuggestions": [],
            }
        }

    def route_after_generate(state: GraphState) -> str:
        return "error_handler" if state.get("error") else "synthesize_response"

    builder = StateGraph(GraphState)
    builder.add_node("load_memory", load_memory)
    builder.add_node("safety_screen", safety_screen)
    builder.add_node("supervisor", supervisor)
    builder.add_node("general_rag", general_rag)
    builder.add_node("synthesize_response", synthesize_response)
    builder.add_node("persist_memory", persist_memory)
    builder.add_node("error_handler", error_handler)

    builder.add_edge(START, "load_memory")
    builder.add_edge("load_memory", "safety_screen")
    builder.add_edge("safety_screen", "supervisor")
    # Phase 4 replaces this static edge with intent-based conditional routing.
    builder.add_edge("supervisor", "general_rag")
    builder.add_conditional_edges(
        "general_rag",
        route_after_generate,
        {
            "synthesize_response": "synthesize_response",
            "error_handler": "error_handler",
        },
    )
    builder.add_edge("synthesize_response", "persist_memory")
    builder.add_edge("persist_memory", END)
    builder.add_edge("error_handler", END)

    return builder.compile(checkpointer=checkpointer)
