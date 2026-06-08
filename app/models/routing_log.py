import uuid

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    Uuid,
    func,
)

from app.db.database import Base


class RoutingLog(Base):
    """One row per supervisor routing decision (Phase 4 routing analytics)."""

    __tablename__ = "routing_logs"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    session_id = Column(
        Uuid,
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    query = Column(Text, nullable=False)
    intent = Column(String, nullable=False, index=True)
    confidence = Column(Float, nullable=True)
    secondary_intents = Column(JSON, nullable=True)
    route = Column(String, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
