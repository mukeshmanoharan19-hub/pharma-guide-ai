"""API tests for HITL checkout confirmation flow (Phase 8.5)."""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import get_current_user
from app.db.database import Base, get_db
from app.main import app as fastapi_app
from app.models.medicine import Medicine
from app.models.user import User

# Register all required tables before create_all.
import app.models.chat_session  # noqa: F401
import app.models.chat_message  # noqa: F401
import app.models.conversation_summary  # noqa: F401
import app.models.cart  # noqa: F401
import app.models.order  # noqa: F401
import app.models.routing_log  # noqa: F401
import app.models.checkout_confirmation  # noqa: F401


def _setup():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    user = User(email="hitl@test.com", password="x", full_name="HITL")
    db.add(user)
    db.add(
        Medicine(
            title="Paracetamol 650mg",
            sku="MED-1",
            final_price=30.0,
            dosage_form="Tablet",
            prescription_req=False,
            is_active=True,
            stock_quantity=50,
            min_order_quantity=1,
            max_order_quantity=20,
        )
    )
    db.commit()
    db.refresh(user)

    fastapi_app.dependency_overrides[get_db] = lambda: db
    fastapi_app.dependency_overrides[get_current_user] = lambda: user
    return db, user, TestClient(fastapi_app)


def _add_to_cart(client: TestClient, qty: int = 1):
    res = client.post("/api/cart/items", json={"sku": "MED-1", "quantity": qty})
    assert res.status_code == 201, res.text


def test_prepare_empty_cart_rejected():
    _, _, client = _setup()
    res = client.post("/api/orders/prepare")
    assert res.status_code == 400, res.text
    assert "empty cart" in res.json()["detail"].lower()


def test_prepare_then_confirm_success():
    _, _, client = _setup()
    _add_to_cart(client, 2)

    prep = client.post("/api/orders/prepare")
    assert prep.status_code == 201, prep.text
    payload = prep.json()
    assert payload["confirmation_id"]
    assert payload["item_count"] == 2
    assert payload["total"] == 60.0

    confirm = client.post(
        "/api/orders",
        json={"confirmation_id": payload["confirmation_id"]},
    )
    assert confirm.status_code == 201, confirm.text
    data = confirm.json()
    assert data["payment_status"] == "mock_paid"
    assert data["total_amount"] == 60.0

    cart = client.get("/api/cart").json()
    assert cart["item_count"] == 0


def test_confirm_bad_id_rejected():
    _, _, client = _setup()
    _add_to_cart(client, 1)
    res = client.post(
        "/api/orders",
        json={"confirmation_id": "00000000-0000-0000-0000-000000000000"},
    )
    assert res.status_code == 400, res.text


def test_confirm_rejected_if_cart_changed():
    _, _, client = _setup()
    _add_to_cart(client, 1)
    prep = client.post("/api/orders/prepare").json()

    # Change cart after review token was issued.
    updated = client.patch("/api/cart/items/MED-1", json={"quantity": 3})
    assert updated.status_code == 200, updated.text

    confirm = client.post(
        "/api/orders",
        json={"confirmation_id": prep["confirmation_id"]},
    )
    assert confirm.status_code == 400, confirm.text
    assert "cart changed" in confirm.json()["detail"].lower()


def test_expired_confirmation_rejected():
    db, _, client = _setup()
    _add_to_cart(client, 1)
    prep = client.post("/api/orders/prepare").json()

    from app.models.checkout_confirmation import CheckoutConfirmation

    conf = (
        db.query(CheckoutConfirmation)
        .filter(CheckoutConfirmation.id == uuid.UUID(prep["confirmation_id"]))
        .first()
    )
    conf.expires_at = conf.expires_at.replace(year=2000)
    db.commit()

    confirm = client.post(
        "/api/orders",
        json={"confirmation_id": prep["confirmation_id"]},
    )
    assert confirm.status_code == 400, confirm.text
    assert "expired" in confirm.json()["detail"].lower()


def test_cancel_prepare_then_confirm_rejected():
    _, _, client = _setup()
    _add_to_cart(client, 1)
    prep = client.post("/api/orders/prepare").json()

    cancel = client.delete(f"/api/orders/prepare/{prep['confirmation_id']}")
    assert cancel.status_code == 204, cancel.text

    confirm = client.post(
        "/api/orders",
        json={"confirmation_id": prep["confirmation_id"]},
    )
    assert confirm.status_code == 400, confirm.text


if __name__ == "__main__":
    test_prepare_empty_cart_rejected()
    test_prepare_then_confirm_success()
    test_confirm_bad_id_rejected()
    test_confirm_rejected_if_cart_changed()
    test_expired_confirmation_rejected()
    test_cancel_prepare_then_confirm_rejected()
    print("checkout confirmation tests OK")
