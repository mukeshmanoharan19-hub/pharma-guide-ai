"""Commerce tools: cart operations and order placement (mock payments).

Core functions are bound to a DB session and the acting ``user_id`` via
``build_commerce_tools`` so the LLM only controls business arguments (sku,
quantity, order_id), never identity.
"""

from __future__ import annotations

from typing import List

from langchain_core.tools import StructuredTool
from sqlalchemy.orm import Session

from app.models.cart import Cart
from app.models.order import Order
from app.services import cart_service, order_service
from app.services.cart_service import CartError
from app.services.order_service import OrderError
from app.tools.base import ToolException, safe_call, with_tool_handling
from app.tools.schemas import (
    AddToCartInput,
    CartItemOut,
    CartOut,
    CreateOrderInput,
    OrderItemOut,
    OrderOut,
    OrderStatusInput,
    RemoveFromCartInput,
    UpdateCartInput,
    ViewCartInput,
)


def _cart_to_out(cart: Cart) -> CartOut:
    items = [
        CartItemOut(
            sku=item.sku,
            title=item.medicine.title if item.medicine else None,
            quantity=item.quantity,
            unit_price=item.unit_price,
            line_total=round((item.unit_price or 0.0) * item.quantity, 2),
        )
        for item in cart.items
    ]
    return CartOut(
        cart_id=str(cart.id),
        items=items,
        item_count=sum(i.quantity for i in items),
        total=cart_service.cart_total(cart),
    )


def _order_to_out(order: Order) -> OrderOut:
    items = [
        OrderItemOut(
            sku=item.sku,
            title=item.title,
            quantity=item.quantity,
            unit_price=item.unit_price,
            line_total=round((item.unit_price or 0.0) * item.quantity, 2),
        )
        for item in order.items
    ]
    return OrderOut(
        order_id=str(order.id),
        status=order.status,
        payment_status=order.payment_status,
        total_amount=order.total_amount,
        items=items,
        created_at=order.created_at.isoformat() if order.created_at else None,
    )


@with_tool_handling("add_to_cart")
def add_to_cart(db: Session, user_id: int, sku: str, quantity: int = 1) -> CartOut:
    try:
        cart = cart_service.add_item(db, user_id, sku, quantity)
    except CartError as e:
        raise ToolException(str(e))
    return _cart_to_out(cart)


@with_tool_handling("remove_from_cart")
def remove_from_cart(db: Session, user_id: int, sku: str) -> CartOut:
    try:
        cart = cart_service.remove_item(db, user_id, sku)
    except CartError as e:
        raise ToolException(str(e))
    return _cart_to_out(cart)


@with_tool_handling("update_cart")
def update_cart(db: Session, user_id: int, sku: str, quantity: int) -> CartOut:
    try:
        cart = cart_service.update_item(db, user_id, sku, quantity)
    except CartError as e:
        raise ToolException(str(e))
    return _cart_to_out(cart)


@with_tool_handling("view_cart")
def view_cart(db: Session, user_id: int) -> CartOut:
    cart = cart_service.get_cart(db, user_id)
    return _cart_to_out(cart)


@with_tool_handling("create_order")
def create_order(db: Session, user_id: int) -> OrderOut:
    try:
        order = order_service.create_order_from_cart(db, user_id)
    except OrderError as e:
        raise ToolException(str(e))
    return _order_to_out(order)


@with_tool_handling("order_status")
def order_status(db: Session, user_id: int, order_id: str) -> OrderOut:
    order = order_service.get_order(db, user_id, order_id)
    if order is None:
        raise ToolException(f"No order found with id '{order_id}'.")
    return _order_to_out(order)


def build_commerce_tools(db: Session, user_id: int) -> List[StructuredTool]:
    """Return commerce tools bound to a DB session and user."""
    return [
        StructuredTool.from_function(
            name="add_to_cart",
            description="Add a quantity of a medicine SKU to the user's cart.",
            args_schema=AddToCartInput,
            func=lambda sku, quantity=1: safe_call(
                add_to_cart, db=db, user_id=user_id, sku=sku, quantity=quantity
            ),
        ),
        StructuredTool.from_function(
            name="remove_from_cart",
            description="Remove a medicine SKU from the user's cart.",
            args_schema=RemoveFromCartInput,
            func=lambda sku: safe_call(
                remove_from_cart, db=db, user_id=user_id, sku=sku
            ),
        ),
        StructuredTool.from_function(
            name="update_cart",
            description=(
                "Set the quantity of a cart line (0 removes it). Respects "
                "min/max order quantity limits."
            ),
            args_schema=UpdateCartInput,
            func=lambda sku, quantity: safe_call(
                update_cart, db=db, user_id=user_id, sku=sku, quantity=quantity
            ),
        ),
        StructuredTool.from_function(
            name="view_cart",
            description="View the current contents and total of the user's cart.",
            args_schema=ViewCartInput,
            func=lambda: safe_call(view_cart, db=db, user_id=user_id),
        ),
        StructuredTool.from_function(
            name="create_order",
            description=(
                "Place an order from the user's active cart. Uses mock payment "
                "(auto-confirmed). Requires a non-empty cart."
            ),
            args_schema=CreateOrderInput,
            func=lambda: safe_call(create_order, db=db, user_id=user_id),
        ),
        StructuredTool.from_function(
            name="order_status",
            description="Get the status and items of one of the user's orders.",
            args_schema=OrderStatusInput,
            func=lambda order_id: safe_call(
                order_status, db=db, user_id=user_id, order_id=order_id
            ),
        ),
    ]
