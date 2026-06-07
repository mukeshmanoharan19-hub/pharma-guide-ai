import uuid

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    Text,
    Uuid,
    func,
)
from sqlalchemy.orm import relationship

from app.db.database import Base


class ConversationSummary(Base):
    __tablename__ = "conversation_summaries"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    session_id = Column(
        Uuid,
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    summary_text = Column(Text, nullable=False)
    # ids of the messages folded into this summary (list of str)
    covers_message_ids = Column(JSON, nullable=True)
    token_count = Column(Integer, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    session = relationship("ChatSession", back_populates="summaries")
