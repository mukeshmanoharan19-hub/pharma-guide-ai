"""Order REST API (Phase 7).

Exposes order creation (with a mock, auto-confirmed payment), order history, and
order tracking over ``order_service``. Order creation requires explicit
confirmation and validates the cart server-side (transaction validation).
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.commerce import (
    CreateOrderRequest,
    OrderConfirmationResponse,
    OrderResponse,
    OrderSummaryResponse,
    serialize_checkout_confirmation,
    serialize_order,
    serialize_order_summary,
)
from app.services import checkout_confirmation_service, order_service
from app.services.checkout_confirmation_service import CheckoutError
from app.services.order_service import OrderError

router = APIRouter(tags=["orders"], prefix="/api/orders")


@router.post(
    "/prepare",
    response_model=OrderConfirmationResponse,
    status_code=status.HTTP_201_CREATED,
)
def prepare_order(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a server-side checkout review token for HITL confirmation."""
    try:
        confirmation = checkout_confirmation_service.prepare_checkout(
            db, current_user.id
        )
    except CheckoutError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return serialize_checkout_confirmation(confirmation)


@router.delete(
    "/prepare/{confirmation_id}", status_code=status.HTTP_204_NO_CONTENT
)
def cancel_prepare(
    confirmation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cancel a pending checkout review token."""
    try:
        checkout_confirmation_service.cancel_checkout(
            db, current_user.id, confirmation_id
        )
    except CheckoutError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    body: CreateOrderRequest = CreateOrderRequest(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Place an order from the active cart after explicit checkout confirmation."""
    if settings.REQUIRE_ORDER_CONFIRMATION and not body.confirmation_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="confirmation_id is required. Call /api/orders/prepare first.",
        )
    try:
        if settings.REQUIRE_ORDER_CONFIRMATION:
            order = checkout_confirmation_service.confirm_checkout(
                db, current_user.id, body.confirmation_id
            )
        else:
            order = order_service.create_order_from_cart(db, current_user.id)
    except CheckoutError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
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
