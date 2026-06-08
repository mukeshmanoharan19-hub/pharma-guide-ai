"""Shared LangGraph state for the agent workflow.

Fields are populated incrementally as the request flows through the graph
nodes. ``total=False`` lets nodes return partial updates.
"""

from __future__ import annotations

from typing import Annotated, Any, List, Optional, TypedDict

from langgraph.graph.message import add_messages


class GraphState(TypedDict, total=False):
    # Request context
    user_id: int
    session_id: str
    query: str

    # Conversational message channel (LangChain messages, reduced/appended)
    messages: Annotated[list, add_messages]

    # Supervisor / routing (populated in Phase 4)
    intent: Optional[str]
    intent_confidence: float

    # Memory (populated in Phase 1 memory layer via load_memory)
    memory_summary: Optional[str]
    history_text: Optional[str]

    # Retrieval + tools (fleshed out in Phases 5-6)
    retrieved_docs: List[Any]
    tool_outputs: List[Any]

    # Safety (populated in Phase 8)
    safety_flags: List[str]

    # Output
    final_response: Optional[dict]
    error: Optional[str]
