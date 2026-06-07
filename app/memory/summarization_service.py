"""Conversation summarization for long-term memory.

When a session's accumulated message tokens exceed the configured threshold,
the oldest messages (those outside the recent window) are folded into a rolling
summary stored in ``conversation_summaries``. The recent window stays verbatim.
"""

from __future__ import annotations

from typing import List, Optional

from loguru import logger
from sqlalchemy.orm import Session

from app.core.config import settings
from app.memory.tokens import estimate_tokens
from app.models.chat_message import ChatMessage
from app.models.conversation_summary import ConversationSummary

_llm = None


def _get_llm():
    """Lazily build a small LLM client for summarization."""
    global _llm
    if _llm is None:
        from langchain_openai import ChatOpenAI

        _llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model=settings.MODEL_NAME,
            temperature=0,
        )
    return _llm


def get_latest_summary(db: Session, session_id) -> Optional[ConversationSummary]:
    return (
        db.query(ConversationSummary)
        .filter(ConversationSummary.session_id == session_id)
        .order_by(ConversationSummary.created_at.desc())
        .first()
    )


def _format_messages(messages: List[ChatMessage]) -> str:
    lines = []
    for message in messages:
        role = message.role.capitalize()
        lines.append(f"{role}: {message.content}")
    return "\n".join(lines)


def _summarize(previous_summary: Optional[str], messages: List[ChatMessage]) -> str:
    prompt = (
        "You are maintaining a running summary of a conversation between a user "
        "and a pharmacy assistant. Update the summary so it captures the user's "
        "goals, mentioned medicines/symptoms, and any decisions, while staying "
        "concise (a few sentences).\n\n"
        f"Existing summary:\n{previous_summary or 'None'}\n\n"
        f"New messages to fold in:\n{_format_messages(messages)}\n\n"
        "Updated summary:"
    )
    response = _get_llm().invoke(prompt)
    return response.content if hasattr(response, "content") else str(response)


def maybe_summarize(db: Session, session_id) -> Optional[ConversationSummary]:
    """Summarize old messages if the token budget is exceeded.

    Returns the newly created summary row, or ``None`` if nothing was done.
    Failures are swallowed (non-fatal) so chat continues to work.
    """
    try:
        # Step 1: Get all messages for the session
        messages = (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
            .all()
        )

        # Step 2: Calculate the total token count
        total_tokens = sum(m.token_count or 0 for m in messages)

        # Step 3: If the total token count is less than the summary threshold, return None
        if total_tokens < settings.SUMMARY_THRESHOLD_TOKENS:
            return None

        window = settings.RECENT_MESSAGE_WINDOW
        if len(messages) <= window:
            return None

        # Everything older than the recent window is a candidate for folding in.
        older = messages[:-window]

        # Step 4: Get the latest summary for the session
        previous = get_latest_summary(db, session_id)
        
        # Step 5: Get the messages that are already covered by the summary
        already_covered = set(
            (previous.covers_message_ids or []) if previous else []
        )

        new_messages = [m for m in older if str(m.id) not in already_covered]
        if not new_messages:
            return None

        # Step 6: Summarize the new messages
        summary_text = _summarize(
            previous.summary_text if previous else None, new_messages
        )

        covered_ids = list(
            already_covered.union(str(m.id) for m in older)
        )

        row = ConversationSummary(
            session_id=session_id,
            summary_text=summary_text,
            covers_message_ids=covered_ids,
            token_count=estimate_tokens(summary_text),
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        logger.info(
            f"Summarized {len(new_messages)} messages for session {session_id}"
        )
        return row
    except Exception as e:  # pragma: no cover - non-fatal path
        logger.warning(f"Summarization skipped for session {session_id}: {e}")
        db.rollback()
        return None
