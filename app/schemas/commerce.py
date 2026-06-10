"""API request/response schemas + serializers for cart & order endpoints."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.cart import Cart
from app.models.checkout_confirmation import CheckoutConfirmation
from app.models.order import Order
from app.services import cart_service


# --------------------------------------------------------------------------- #
# Requests
# --------------------------------------------------------------------------- #
class AddItemRequest(BaseModel):
    sku: str = Field(..., description="SKU of the medicine to add.")
    quantity: int = Field(1, ge=1, description="Units to add.")


class UpdateItemRequest(BaseModel):
    quantity: int = Field(..., ge=0, description="New quantity (0 removes the line).")


class CreateOrderRequest(BaseModel):
    # Token returned by POST /api/orders/prepare, used for human-in-the-loop
    # confirmation before placing the order.
    confirmation_id: str | None = Field(
        default=None,
        description="Checkout confirmation id from /api/orders/prepare.",
    )


# --------------------------------------------------------------------------- #
# Responses
# --------------------------------------------------------------------------- #
class CartItemResponse(BaseModel):
    sku: Optional[str] = None
    title: Optional[str] = None
    quantity: int
    unit_price: Optional[float] = None
    line_total: float


class CartResponse(BaseModel):
    cart_id: str
    items: List[CartItemResponse]
    item_count: int
    total: float


class OrderItemResponse(BaseModel):
    sku: Optional[str] = None
    title: Optional[str] = None
    quantity: int
    unit_price: Optional[float] = None
    line_total: float


class OrderResponse(BaseModel):
    order_id: str
    status: str
    payment_status: str
    total_amount: float
    items: List[OrderItemResponse]
    created_at: Optional[str] = None


class OrderConfirmationResponse(BaseModel):
    confirmation_id: str
    items: List[CartItemResponse]
    item_count: int
    total: float
    status: str
    expires_at: str


class OrderSummaryResponse(BaseModel):
    order_id: str
    status: str
    payment_status: str
    total_amount: float
    item_count: int
    created_at: Optional[str] = None


# --------------------------------------------------------------------------- #
# Serializers
# --------------------------------------------------------------------------- #
def serialize_cart(cart: Cart) -> CartResponse:
    items = [
        CartItemResponse(
            sku=item.sku,
            title=item.medicine.title if item.medicine else None,
            quantity=item.quantity,
            unit_price=item.unit_price,
            line_total=round((item.unit_price or 0.0) * item.quantity, 2),
        )
        for item in cart.items
    ]
    return CartResponse(
        cart_id=str(cart.id),
        items=items,
        item_count=sum(i.quantity for i in items),
        total=cart_service.cart_total(cart),
    )


def serialize_order(order: Order) -> OrderResponse:
    items = [
        OrderItemResponse(
            sku=item.sku,
            title=item.title,
            quantity=item.quantity,
            unit_price=item.unit_price,
            line_total=round((item.unit_price or 0.0) * item.quantity, 2),
        )
        for item in order.items
    ]
    return OrderResponse(
        order_id=str(order.id),
        status=order.status,
        payment_status=order.payment_status,
        total_amount=order.total_amount,
        items=items,
        created_at=order.created_at.isoformat() if order.created_at else None,
    )


def serialize_order_summary(order: Order) -> OrderSummaryResponse:
    return OrderSummaryResponse(
        order_id=str(order.id),
        status=order.status,
        payment_status=order.payment_status,
        total_amount=order.total_amount,
        item_count=sum(i.quantity for i in order.items),
        created_at=order.created_at.isoformat() if order.created_at else None,
    )


def serialize_checkout_confirmation(
    confirmation: CheckoutConfirmation,
) -> OrderConfirmationResponse:
    snapshot = confirmation.items_snapshot or []
    items = [CartItemResponse(**row) for row in snapshot]
    return OrderConfirmationResponse(
        confirmation_id=str(confirmation.id),
        items=items,
        item_count=sum(i.quantity for i in items),
        total=confirmation.total_amount,
        status=confirmation.status,
        expires_at=confirmation.expires_at.isoformat(),
    )
