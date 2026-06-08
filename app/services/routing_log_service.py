"""Persistence for supervisor routing decisions (Phase 4 routing analytics)."""

from __future__ import annotations

import uuid
from typing import List, Optional

from loguru import logger
from sqlalchemy.orm import Session

from app.models.routing_log import RoutingLog


def _coerce_uuid(value) -> Optional[uuid.UUID]:
    if value is None or isinstance(value, uuid.UUID):
        return value
    try:
        return uuid.UUID(str(value))
    except (ValueError, TypeError):
        return None


def record_decision(
    db: Session,
    *,
    user_id: Optional[int],
    session_id,
    query: str,
    intent: str,
    confidence: Optional[float],
    secondary_intents: Optional[List[str]] = None,
    route: Optional[str] = None,
) -> Optional[RoutingLog]:
    """Best-effort persistence of a routing decision.

    Analytics must never break the request, so all errors are swallowed (after
    a rollback) and logged.
    """
    try:
        log = RoutingLog(
            user_id=user_id,
            session_id=_coerce_uuid(session_id),
            query=query,
            intent=intent,
            confidence=confidence,
            secondary_intents=secondary_intents or [],
            route=route,
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
    except Exception as exc:
        logger.warning(f"Failed to record routing decision: {exc}")
        try:
            db.rollback()
        except Exception:
            pass
        return None
