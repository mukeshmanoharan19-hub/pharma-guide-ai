"""Isolation tests for the Phase 2 tool layer.

Runs against an in-memory SQLite database so no external services are needed.
Executable directly (``python -m tests.test_tools``) or via pytest.
"""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.models.medicine import Medicine
from app.models.user import User

# Import all models so metadata is complete before create_all.
import app.models.chat_session  # noqa: F401
import app.models.chat_message  # noqa: F401
import app.models.conversation_summary  # noqa: F401
import app.models.cart  # noqa: F401
import app.models.order  # noqa: F401

from app.tools.base import ToolException
from app.tools import commerce_tools, medicine_tools, user_tools


def _make_session():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def _seed(db):
    user = User(email="a@b.com", password="x", full_name="Tester")
    db.add(user)
    db.add_all([
        Medicine(
            id=1,
            title="Paracetamol 500mg",
            sku="PARA-500",
            compositions="Paracetamol",
            salt_type="paracetamol",
            composition_key="paracetamol-500",
            final_price=25.0,
            is_active=True,
            prescription_req=False,
            min_order_quantity=1,
            max_order_quantity=5,
        ),
        Medicine(
            id=2,
            title="Dolo 500mg",
            sku="DOLO-500",
            compositions="Paracetamol",
            salt_type="paracetamol",
            composition_key="paracetamol-500",
            final_price=30.0,
            is_active=True,
            prescription_req=False,
        ),
        Medicine(
            id=3,
            title="Out Of Stock Med",
            sku="OOS-1",
            final_price=10.0,
            is_active=True,
            stock_quantity=0,
        ),
    ])
    db.commit()
    return user


def test_medicine_tools():
    db = _make_session()
    _seed(db)

    found = medicine_tools.search_medicine(db, "paracetamol", 5)
    assert found.count >= 2, "search should find paracetamol products"

    # invalid input
    try:
        medicine_tools.search_medicine(db, "   ")
        raise AssertionError("empty query should raise")
    except ToolException:
        pass

    details = medicine_tools.product_details(db, "PARA-500")
    assert details.title == "Paracetamol 500mg"

    try:
        medicine_tools.product_details(db, "NOPE")
        raise AssertionError("missing sku should raise")
    except ToolException:
        pass

    alts = medicine_tools.alternative_medicine(db, "PARA-500")
    assert any(a.sku == "DOLO-500" for a in alts.alternatives)

    stock = medicine_tools.stock_availability(db, "OOS-1")
    assert stock.in_stock is False
    print("medicine tools OK")


def test_commerce_tools():
    db = _make_session()
    user = _seed(db)
    uid = user.id

    cart = commerce_tools.add_to_cart(db, uid, "PARA-500", 2)
    assert cart.item_count == 2
    assert cart.total == 50.0

    # max order quantity is 5; adding 4 more (total 6) must fail
    try:
        commerce_tools.add_to_cart(db, uid, "PARA-500", 4)
        raise AssertionError("exceeding max qty should raise")
    except ToolException:
        pass

    # out of stock cannot be added
    try:
        commerce_tools.add_to_cart(db, uid, "OOS-1", 1)
        raise AssertionError("oos add should raise")
    except ToolException:
        pass

    cart = commerce_tools.update_cart(db, uid, "PARA-500", 3)
    assert cart.items[0].quantity == 3

    view = commerce_tools.view_cart(db, uid)
    assert view.total == 75.0

    order = commerce_tools.create_order(db, uid)
    assert order.payment_status == "mock_paid"
    assert order.total_amount == 75.0

    # cart should now be empty (converted)
    assert commerce_tools.view_cart(db, uid).item_count == 0

    # empty cart cannot create an order
    try:
        commerce_tools.create_order(db, uid)
        raise AssertionError("empty cart order should raise")
    except ToolException:
        pass

    status = commerce_tools.order_status(db, uid, order.order_id)
    assert status.order_id == order.order_id
    print("commerce tools OK")


def test_user_tools():
    db = _make_session()
    user = _seed(db)
    profile = user_tools.user_profile(db, user.id)
    assert profile.email == "a@b.com"
    history = user_tools.purchase_history(db, user.id)
    assert history.count == 0
    print("user tools OK")


def test_registry_envelopes():
    from app.tools.registry import build_all_tools, get_tool_map

    db = _make_session()
    user = _seed(db)
    tools = build_all_tools(db, user.id)
    assert len(tools) == 12

    tool_map = get_tool_map(db, user.id)
    # StructuredTool returns the safe envelope dict
    result = tool_map["search_medicine"].invoke({"query": "paracetamol"})
    assert result["success"] is True
    bad = tool_map["product_details"].invoke({"sku": "NOPE"})
    assert bad["success"] is False
    print("registry/envelope OK")


if __name__ == "__main__":
    test_medicine_tools()
    test_commerce_tools()
    test_user_tools()
    test_registry_envelopes()
    print("ALL TOOL TESTS PASSED")
