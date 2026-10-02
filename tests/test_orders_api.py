"""HTTP-boundary tests for the Orders API."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.core.database import Database
from app.main import create_app
from app.modules.inventory.services import InventoryService
from app.modules.orders.models import Order


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
