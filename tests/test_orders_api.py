"""HTTP-boundary tests for the Orders API."""

from __future__ import annotations

from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.core.database import Database
from app.main import create_app
from app.modules.inventory.services import InventoryService
from app.modules.orders.models import Order


def test_valid_order_http_flow_persists_order_and_stock(database: Database) -> None:
    """HTTP creation and reads reflect a committed order and stock reservation."""
    with TestClient(create_app(database_url=database.url)) as client:
        initial = client.get("/inventory/active-product")
        assert initial.status_code == 200
        assert initial.json() == {"product_id": "active-product", "quantity": 10}

        response = client.post(
            "/orders", json={"product_id": "active-product", "quantity": 3},
        )
        assert response.status_code == 201
        order = response.json()
        assert order["id"]
        assert order["created_at"]
        assert order["product_id"] == "active-product"
        assert order["quantity"] == 3
        assert Decimal(str(order["unit_price"])) == Decimal("12.50")

        retrieved = client.get(f"/orders/{order['id']}")
        assert retrieved.status_code == 200
        assert retrieved.json() == order
        inventory = client.get("/inventory/active-product")
        assert inventory.status_code == 200
        assert inventory.json() == {"product_id": "active-product", "quantity": 7}

    session = database.session_factory()
    try:
        persisted = session.get(Order, order["id"])
        assert persisted is not None
        assert persisted.product_id == "active-product"
        assert persisted.quantity == 3
        assert persisted.unit_price == Decimal("12.50")
        assert session.scalar(select(func.count()).select_from(Order)) == 1
        assert InventoryService().get_inventory(session, "active-product").quantity == 7
    finally:
        session.close()


def test_invalid_quantity_is_rejected_without_persistence(database: Database) -> None:
    """FastAPI rejects a zero quantity before Orders can persist data."""
    with TestClient(create_app(database_url=database.url)) as client:
        response = client.post(
            "/orders",
            json={"product_id": "active-product", "quantity": 0},
        )

    assert response.status_code == 422

    session = database.session_factory()
    try:
        inventory = InventoryService().get_inventory(session, "active-product")
        order_count = session.scalar(select(func.count()).select_from(Order)) or 0
        assert inventory.quantity == 10
        assert order_count == 0
    finally:
        session.close()
