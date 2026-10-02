"""Shared SQLite fixtures for bounded LAB-02 and LAB-03 tests."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from app.core.database import Database
from app.modules.catalog.models import Product
from app.modules.inventory.models import InventoryItem
from app.modules.orders.models import Order  # noqa: F401


@pytest.fixture
def database(tmp_path: Path) -> Database:
    """Return a temporary file-backed database with deterministic products."""
    database_path = tmp_path / "lab_orders.db"
    database = Database(f"sqlite:///{database_path}")
    database.create_all()
    session = database.session_factory()
    try:
        session.add_all(
            [
                Product(
                    id="active-product",
                    name="Active product",
                    unit_price=Decimal("12.50"),
                    is_active=True,
                ),
                Product(
                    id="zero-stock-product",
                    name="Zero-stock product",
                    unit_price=Decimal("8.00"),
                    is_active=True,
                ),
                Product(
                    id="inactive-product",
                    name="Inactive product",
                    unit_price=Decimal("5.00"),
                    is_active=False,
                ),
            ]
        )
        session.add_all(
            [
                InventoryItem(product_id="active-product", quantity=10),
                InventoryItem(product_id="zero-stock-product", quantity=0),
                InventoryItem(product_id="inactive-product", quantity=4),
            ]
        )
        session.commit()
    finally:
        session.close()
    return database
