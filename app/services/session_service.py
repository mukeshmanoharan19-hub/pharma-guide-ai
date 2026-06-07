"""CRUD operations for chat sessions and their messages."""

from __future__ import annotations

import uuid
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession
from app.models.user import User


def _coerce_uuid(session_id) -> Optional[uuid.UUID]:
    if isinstance(session_id, uuid.UUID):
        return session_id
    try:
        return uuid.UUID(str(session_id))
    except (ValueError, TypeError):
        return None


def create_session(
    db: Session, user: User, title: Optional[str] = None
) -> ChatSession:
    session = ChatSession(user_id=user.id, title=title or "New conversation")
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def list_sessions(db: Session, user: User) -> List[ChatSession]:
    return (
        db.query(ChatSession)
        .filter(
            ChatSession.user_id == user.id,
            ChatSession.is_active.is_(True),
        )
        .order_by(ChatSession.updated_at.desc())
        .all()
    )


def get_session(db: Session, user: User, session_id) -> Optional[ChatSession]:
    parsed = _coerce_uuid(session_id)
    if parsed is None:
        return None
    return (
        db.query(ChatSession)
        .filter(
            ChatSession.id == parsed,
            ChatSession.user_id == user.id,
            ChatSession.is_active.is_(True),
        )
        .first()
    )


def soft_delete_session(
    db: Session, user: User, session_id
) -> Optional[ChatSession]:
    session = get_session(db, user, session_id)
    if session is None:
        return None
    session.is_active = False
    db.commit()
    return session


def get_messages(
    db: Session, user: User, session_id
) -> Optional[List[ChatMessage]]:
    session = get_session(db, user, session_id)
    if session is None:
        return None
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session.id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
