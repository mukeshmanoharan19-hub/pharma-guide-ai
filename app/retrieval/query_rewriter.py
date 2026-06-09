"""Conversation-aware query rewriting (Phase 6).

Turns the user's latest (often elliptical) message into a self-contained search
query by resolving references against the conversation summary and recent
history. Always degrades gracefully to the original query.
"""

from __future__ import annotations

from typing import Optional

from loguru import logger

from app.core.config import settings
from app.core.prompts import QUERY_REWRITE_PROMPT


def rewrite_query(
    query: str,
    history_text: Optional[str] = None,
    summary_text: Optional[str] = None,
) -> str:
    """Return a standalone search query (falls back to ``query`` on any issue)."""
    if not settings.ENABLE_QUERY_REWRITE:
        return query

    # Nothing to resolve against — the query is already standalone.
    if not history_text and not summary_text:
        return query

    # Imported lazily to avoid import-time LLM/env requirements.
    from app.retrieval.query_expansion import llm

    prompt = QUERY_REWRITE_PROMPT.format(
        summary=summary_text or "None.",
        history=history_text or "None.",
        question=query,
    )

    try:
        response = llm.invoke(prompt)
        rewritten = (response.content or "").strip()
    except Exception as exc:
        logger.warning(f"Query rewrite failed, using original query: {exc}")
        return query

    if not rewritten:
        return query

    # Guard against the model returning something degenerate.
    if len(rewritten) > 500:
        rewritten = rewritten[:500]

    if rewritten != query:
        logger.info(f"Rewrote query: {query!r} -> {rewritten!r}")
    return rewritten
