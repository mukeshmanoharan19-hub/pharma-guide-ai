"""Cart REST API (Phase 7).

Thin HTTP layer over ``cart_service`` — the same logic the commerce agent drives
through its tools. All endpoints are scoped to the authenticated user; the cart
is resolved server-side (the client never supplies a cart id).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.commerce import AddItemRequest, CartResponse, UpdateItemRequest
from app.schemas.commerce import serialize_cart
from app.services import cart_service
from app.services.cart_service import CartError

router = APIRouter(tags=["cart"], prefix="/api/cart")


@router.get("", response_model=CartResponse)
def view_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cart = cart_service.get_cart(db, current_user.id)
    return serialize_cart(cart)


@router.post("/items", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
def add_item(
    body: AddItemRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        cart = cart_service.add_item(db, current_user.id, body.sku, body.quantity)
    except CartError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return serialize_cart(cart)


@router.patch("/items/{sku}", response_model=CartResponse)
def update_item(
    sku: str,
    body: UpdateItemRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        cart = cart_service.update_item(db, current_user.id, sku, body.quantity)
    except CartError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return serialize_cart(cart)


@router.delete("/items/{sku}", response_model=CartResponse)
def remove_item(
    sku: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        cart = cart_service.remove_item(db, current_user.id, sku)
    except CartError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return serialize_cart(cart)
