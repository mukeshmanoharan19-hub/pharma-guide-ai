"""Assemble conversational context for the LLM.

Combines the latest rolling summary with the recent verbatim message window,
respecting the configured token budget.
"""

from __future__ import annotations

from typing import List, Tuple

from sqlalchemy.orm import Session

from app.core.config import settings
from app.memory import history_service, summarization_service
from app.memory.tokens import estimate_tokens

_ROLE_LABELS = {
    "user": "User",
    "assistant": "Assistant",
    "system": "System",
    "tool": "Tool",
}


def format_history(messages: List[dict]) -> str:
    """Render recent messages as a simple transcript string."""
    lines = []
    for message in messages:
        label = _ROLE_LABELS.get(message.get("role", ""), message.get("role", ""))
        lines.append(f"{label}: {message.get('content', '')}")
    return "\n".join(lines)


def build_context(db: Session, session_id) -> Tuple[str, List[dict]]:
    """Return ``(summary_text, recent_messages)`` for a session.

    Recent messages are capped to the configured window and trimmed further if
    the running token total would exceed ``MAX_CONTEXT_TOKENS``.
    """
    summary_row = summarization_service.get_latest_summary(db, session_id)
    summary_text = summary_row.summary_text if summary_row else ""

    recent = history_service.get_recent(
        db, session_id, settings.RECENT_MESSAGE_WINDOW
    )

    budget = settings.MAX_CONTEXT_TOKENS - estimate_tokens(summary_text)
    trimmed: List[dict] = []
    running = 0
    # Walk newest -> oldest so we keep the most relevant turns under budget.
    for message in reversed(recent):
        cost = message.get("token_count") or estimate_tokens(
            message.get("content", "")
        )
        if running + cost > budget and trimmed:
            break
        trimmed.append(message)
        running += cost

    trimmed.reverse()
    return summary_text, trimmed
