"""LangGraph agent workflow (Phase 8: + medical safety layer).

Flow:

    load_memory -> safety_screen
        --(emergency / prompt injection)--> synthesize_response (short-circuit)
        --(otherwise)--> supervisor
            --(intent-based conditional routing)-->
                medicine_agent | symptom_agent | commerce_agent
                | support_agent | general_chat
        -> synthesize_response -> persist_memory

``safety_screen`` runs rule-based risk detection + input guardrails. Emergencies
and prompt-injection attempts short-circuit with a canned response; caution flags
(pregnancy/pediatric/restricted advice) attach a doctor-consult disclaimer that
``synthesize_response`` appends to the answer.

The supervisor classifies the user's intent (six intents from the roadmap),
records routing analytics, and routes to the matching specialist node. Low
confidence or an unrecognised intent falls back to ``general_chat``.

Specialist nodes (Phase 5):
- medicine_agent / symptom_agent / commerce_agent / support_agent are
  tool-calling agents bound to the relevant Phase 2 tools (catalog search,
  cart/order operations, order tracking).
- general_chat stays on the plain RAG pipeline (no tools) for small talk and
  policy/FAQ questions (the RAG knowledge base holds only policies & FAQs).

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

from app.agents import intents
from app.agents.specialists import (
    COMMERCE_AGENT_SPEC,
    MEDICINE_AGENT_SPEC,
    SUPPORT_AGENT_SPEC,
    SYMPTOM_AGENT_SPEC,
)
from app.agents.state import GraphState
from app.agents.supervisor import classify_intent, resolve_route
from app.agents.tool_agent import run_tool_agent
from app.core.config import settings
from app.memory import context_builder, history_service, summarization_service
from app.safety import assess_safety
from app.services import routing_log_service
from app.services.rag_service import get_rag_service, llm
from app.tools.registry import build_tools_by_names

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

    # Build each specialist's tool set once, bound to this request's db/user.
    specialist_tools = {
        spec.node: build_tools_by_names(db, user_id, spec.tool_names)
        for spec in (
            MEDICINE_AGENT_SPEC,
            SYMPTOM_AGENT_SPEC,
            COMMERCE_AGENT_SPEC,
            SUPPORT_AGENT_SPEC,
        )
    }

    def _run_specialist(state: GraphState, spec) -> dict:
        """Run a tool-calling specialist agent and shape the response."""
        try:
            result = run_tool_agent(
                llm=llm,
                tools=specialist_tools[spec.node],
                system_prompt=spec.system_prompt,
                query=state["query"],
                history_text=state.get("history_text"),
                summary_text=state.get("memory_summary"),
            )
            return {
                "final_response": {
                    "answer": result["answer"],
                    "productsSuggestions": result["products"],
                },
                "tool_outputs": result["tool_outputs"],
                "messages": [AIMessage(content=result["answer"])],
            }
        except Exception as exc:  # node-level error transition
            logger.exception(f"specialist '{spec.node}' failed: {exc}")
            return {"error": str(exc)}

    def _answer_with_rag(state: GraphState) -> dict:
        """Shared RAG answer used by the information-seeking specialist nodes."""
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
            logger.exception(f"RAG answer failed: {exc}")
            return {"error": str(exc)}

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
        """Medical safety gate (Phase 8): risk detection + input guardrails.

        Emergencies and prompt-injection attempts short-circuit the graph with a
        canned response. Caution flags (pregnancy/pediatric/restricted advice)
        let the turn proceed but attach a doctor-consult disclaimer that
        ``synthesize_response`` appends to the final answer.
        """
        if not settings.ENABLE_SAFETY_LAYER:
            return {"safety_flags": [], "safety_blocked": False}

        assessment = assess_safety(state["query"])
        update: dict = {
            "safety_flags": assessment.flags,
            "safety_level": assessment.level,
            "safety_disclaimer": assessment.disclaimer,
            "safety_blocked": assessment.blocked,
        }
        if assessment.flags:
            logger.info(
                "[safety] level={} blocked={} flags={}",
                assessment.level,
                assessment.blocked,
                assessment.flags,
            )
        if assessment.blocked:
            update["safety_message"] = assessment.message
            update["final_response"] = {
                "answer": assessment.message,
                "productsSuggestions": [],
            }
        return update

    def supervisor(state: GraphState) -> dict:
        """Detect intent, resolve the route, and record routing analytics."""
        classification = classify_intent(
            state["query"],
            history_text=state.get("history_text"),
            summary_text=state.get("memory_summary"),
        )
        route, effective_intent = resolve_route(classification)

        logger.info(
            "[supervisor] intent={} confidence={:.2f} route={} secondary={}",
            effective_intent,
            classification.confidence,
            route,
            classification.secondary_intents,
        )

        routing_log_service.record_decision(
            db,
            user_id=user_id,
            session_id=state.get("session_id"),
            query=state["query"],
            intent=effective_intent,
            confidence=classification.confidence,
            secondary_intents=classification.secondary_intents,
            route=route,
        )

        return {
            "intent": effective_intent,
            "intent_confidence": classification.confidence,
            "secondary_intents": classification.secondary_intents,
            "route": route,
        }

    def medicine_agent(state: GraphState) -> dict:
        return _run_specialist(state, MEDICINE_AGENT_SPEC)

    def symptom_agent(state: GraphState) -> dict:
        return _run_specialist(state, SYMPTOM_AGENT_SPEC)

    def commerce_agent(state: GraphState) -> dict:
        return _run_specialist(state, COMMERCE_AGENT_SPEC)

    def support_agent(state: GraphState) -> dict:
        return _run_specialist(state, SUPPORT_AGENT_SPEC)

    def general_chat(state: GraphState) -> dict:
        # General conversation + policy/FAQ questions use the RAG pipeline,
        # whose knowledge base contains only company policies and FAQs.
        return _answer_with_rag(state)

    def synthesize_response(state: GraphState) -> dict:
        """Finalise the response payload and append any safety disclaimer."""
        final = state.get("final_response")
        if not final:
            final = {
                "answer": SAFE_FALLBACK_MESSAGE,
                "productsSuggestions": [],
            }

        # Append the doctor-consult disclaimer for non-blocking caution flags.
        disclaimer = state.get("safety_disclaimer")
        if disclaimer and not state.get("safety_blocked"):
            answer = final.get("answer", "") or ""
            if disclaimer not in answer:
                final = {**final, "answer": f"{answer}\n\n{disclaimer}".strip()}

        return {"final_response": final}

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
                metadata={
                    "products": products,
                    "intent": state.get("intent"),
                    "safety_level": state.get("safety_level"),
                    "safety_flags": state.get("safety_flags") or [],
                },
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

    def route_after_safety(state: GraphState) -> str:
        """Short-circuit to the response tail when safety blocked the turn."""
        return "synthesize_response" if state.get("safety_blocked") else "supervisor"

    def route_from_supervisor(state: GraphState) -> str:
        """Return the specialist node chosen by the supervisor (with fallback)."""
        route = state.get("route")
        if route in intents.ALL_ROUTES:
            return route
        return intents.FALLBACK_ROUTE

    def route_after_agent(state: GraphState) -> str:
        return "error_handler" if state.get("error") else "synthesize_response"

    builder = StateGraph(GraphState)
    builder.add_node("load_memory", load_memory)
    builder.add_node("safety_screen", safety_screen)
    builder.add_node("supervisor", supervisor)
    builder.add_node(intents.MEDICINE_AGENT, medicine_agent)
    builder.add_node(intents.SYMPTOM_AGENT, symptom_agent)
    builder.add_node(intents.COMMERCE_AGENT, commerce_agent)
    builder.add_node(intents.SUPPORT_AGENT, support_agent)
    builder.add_node(intents.GENERAL_CHAT, general_chat)
    builder.add_node("synthesize_response", synthesize_response)
    builder.add_node("persist_memory", persist_memory)
    builder.add_node("error_handler", error_handler)

    builder.add_edge(START, "load_memory")
    builder.add_edge("load_memory", "safety_screen")

    # Safety can short-circuit straight to the response tail (emergency /
    # prompt injection) or hand off to the supervisor for normal routing.
    builder.add_conditional_edges(
        "safety_screen",
        route_after_safety,
        {
            "supervisor": "supervisor",
            "synthesize_response": "synthesize_response",
        },
    )

    # Intent-based routing from the supervisor to a specialist agent.
    builder.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {route: route for route in intents.ALL_ROUTES},
    )

    # Every specialist node either succeeds (-> synthesize) or errors (-> handler).
    after_agent_map = {
        "synthesize_response": "synthesize_response",
        "error_handler": "error_handler",
    }
    for agent_node in intents.ALL_ROUTES:
        builder.add_conditional_edges(
            agent_node, route_after_agent, after_agent_map
        )

    builder.add_edge("synthesize_response", "persist_memory")
    builder.add_edge("persist_memory", END)
    builder.add_edge("error_handler", END)

    return builder.compile(checkpointer=checkpointer)
