"""User-context tools: profile and purchase history."""

from __future__ import annotations

from typing import List

from langchain_core.tools import StructuredTool
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.user import User
from app.services import order_service
from app.tools.base import ToolException, safe_call, with_tool_handling
from app.tools.schemas import (
    OrderSummary,
    PurchaseHistoryInput,
    PurchaseHistoryOutput,
    UserProfileInput,
    UserProfileOutput,
)


@with_tool_handling("user_profile")
def user_profile(db: Session, user_id: int) -> UserProfileOutput:
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise ToolException("User not found.")
    total_orders = (
        db.query(Order).filter(Order.user_id == user_id).count()
    )
    return UserProfileOutput(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        total_orders=total_orders,
    )


@with_tool_handling("purchase_history")
def purchase_history(
    db: Session, user_id: int, limit: int = 10
) -> PurchaseHistoryOutput:
    orders: List[Order] = order_service.list_orders(db, user_id, limit)
    summaries = [
        OrderSummary(
            order_id=str(order.id),
            status=order.status,
            payment_status=order.payment_status,
            total_amount=order.total_amount,
            created_at=order.created_at.isoformat()
            if order.created_at
            else None,
        )
        for order in orders
    ]
    return PurchaseHistoryOutput(orders=summaries, count=len(summaries))


def build_user_tools(db: Session, user_id: int) -> List[StructuredTool]:
    return [
        StructuredTool.from_function(
            name="user_profile",
            description="Get the current user's profile and order count.",
            args_schema=UserProfileInput,
            func=lambda: safe_call(user_profile, db=db, user_id=user_id),
        ),
        StructuredTool.from_function(
            name="purchase_history",
            description="List the current user's recent orders.",
            args_schema=PurchaseHistoryInput,
            func=lambda limit=10: safe_call(
                purchase_history, db=db, user_id=user_id, limit=limit
            ),
        ),
    ]
