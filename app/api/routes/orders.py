"""Order REST API (Phase 7).

Exposes order creation (with a mock, auto-confirmed payment), order history, and
order tracking over ``order_service``. Order creation requires explicit
confirmation and validates the cart server-side (transaction validation).
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.commerce import (
    CreateOrderRequest,
    OrderResponse,
    OrderSummaryResponse,
    serialize_order,
    serialize_order_summary,
)
from app.services import order_service
from app.services.order_service import OrderError

router = APIRouter(tags=["orders"], prefix="/api/orders")


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    body: CreateOrderRequest = CreateOrderRequest(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Place an order from the active cart (mock payment, auto-confirmed)."""
    if not body.confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order not confirmed. Set confirm=true to place the order.",
        )
    try:
        order = order_service.create_order_from_cart(db, current_user.id)
    except OrderError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return serialize_order(order)


@router.get("", response_model=List[OrderSummaryResponse])
def list_orders(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Order history for the authenticated user (most recent first)."""
    orders = order_service.list_orders(db, current_user.id, limit)
    return [serialize_order_summary(o) for o in orders]


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Track a single order by id."""
    order = order_service.get_order(db, current_user.id, order_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No order found with id '{order_id}'.",
        )
    return serialize_order(order)
