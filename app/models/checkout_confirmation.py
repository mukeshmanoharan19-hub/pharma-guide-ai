import uuid

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Uuid,
    func,
)

from app.db.database import Base


class CheckoutConfirmation(Base):
    """Server-side checkout review token for human-in-the-loop confirmation."""

    __tablename__ = "checkout_confirmations"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    cart_id = Column(
        Uuid,
        ForeignKey("carts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    items_snapshot = Column(JSON, nullable=False)
    total_amount = Column(Float, nullable=False, default=0.0)
    cart_version_hash = Column(String, nullable=False, index=True)
    # pending | confirmed | expired | cancelled
    status = Column(String, nullable=False, default="pending", index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    # Reserved for future prescription/payment checks.
    requires_manual_review = Column(Boolean, nullable=False, default=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
