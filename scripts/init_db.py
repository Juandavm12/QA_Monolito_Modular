"""Idempotently initialize and seed the local laboratory database."""

from __future__ import annotations

from scripts.seed_data import seed_synthetic_data

from app.core.database import Database
from app.modules.catalog.models import Product
from app.modules.inventory.models import InventoryItem
from app.modules.orders.models import Order


ORM_MODELS = (Product, InventoryItem, Order)


def main() -> None:
    """Create every schema table and insert absent synthetic records."""
    database = Database()
    database.create_all()
    seed_synthetic_data(database)
    print("Database initialization: complete")


if __name__ == "__main__":
    main()
