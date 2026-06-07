import uuid

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Uuid,
    func,
)
from sqlalchemy.orm import relationship

from app.db.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # pending | confirmed | shipped | delivered | cancelled
    status = Column(String, nullable=False, default="confirmed")
    # mock_paid | unpaid | refunded (real gateways arrive later)
    payment_status = Column(String, nullable=False, default="mock_paid")
    total_amount = Column(Float, nullable=False, default=0.0)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    order_id = Column(
        Uuid,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    medicine_id = Column(
        Integer, ForeignKey("medicines.id"), nullable=False
    )
    sku = Column(String, nullable=True)
    title = Column(String, nullable=True)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Float, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    order = relationship("Order", back_populates="items")
    medicine = relationship("Medicine")
