import uuid

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Uuid,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from app.db.database import Base


class Cart(Base):
    __tablename__ = "carts"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # active | converted
    status = Column(String, nullable=False, default="active")
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
        "CartItem",
        back_populates="cart",
        cascade="all, delete-orphan",
    )


class CartItem(Base):
    __tablename__ = "cart_items"
    __table_args__ = (
        UniqueConstraint("cart_id", "medicine_id", name="uq_cart_item"),
    )

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    cart_id = Column(
        Uuid,
        ForeignKey("carts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    medicine_id = Column(
        Integer, ForeignKey("medicines.id"), nullable=False
    )
    sku = Column(String, nullable=True)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Float, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    cart = relationship("Cart", back_populates="items")
    medicine = relationship("Medicine")
