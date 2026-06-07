"""Chat history retrieval and persistence.

Reads prefer the Redis hot cache and fall back to PostgreSQL, re-hydrating the
cache on a miss. Writes persist to PostgreSQL (source of truth) and update the
cache.
"""

from __future__ import annotations

from typing import List, Optional

from loguru import logger
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.memory import redis_client
from app.memory.tokens import estimate_tokens
from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession


def _to_dict(message: ChatMessage) -> dict:
    return {
        "id": str(message.id),
        "role": message.role,
        "content": message.content,
        "token_count": message.token_count,
        "metadata": message.message_metadata,
        "created_at": message.created_at.isoformat()
        if message.created_at
        else None,
    }


def add_message(
    db: Session,
    session_id,
    role: str,
    content: str,
    metadata: Optional[dict] = None,
) -> ChatMessage:
    """Persist a message and update the hot cache."""
    message = ChatMessage(
        session_id=session_id,
        role=role,
        content=content,
        message_metadata=metadata,
        token_count=estimate_tokens(content),
    )
    db.add(message)

    # Touch the parent session so ordering by recency stays correct.
    db.query(ChatSession).filter(ChatSession.id == session_id).update(
        {"updated_at": func.now()}
    )

    db.commit()
    db.refresh(message)

    redis_client.push_message(str(session_id), _to_dict(message))
    logger.debug(f"Persisted {role} message to session {session_id}")
    return message


def get_recent(db: Session, session_id, limit: int) -> List[dict]:
    """Return the most recent ``limit`` messages (oldest first)."""
    cached = redis_client.get_recent_messages(str(session_id), limit)
    if cached is not None:
        return cached

    rows = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    messages = [_to_dict(row) for row in rows]

    if messages:
        redis_client.hydrate(str(session_id), messages)

    return messages[-limit:]


def get_all(db: Session, session_id) -> List[ChatMessage]:
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
