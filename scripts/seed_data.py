"""Idempotent synthetic data seeding for the ordering laboratory."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.database import Database
from app.modules.catalog.models import Product
from app.modules.inventory.models import InventoryItem
from app.modules.orders.models import Order


ORM_MODELS = (Product, InventoryItem, Order)
SYNTHETIC_PRODUCTS = (
    ("product-active", "Active product", Decimal("12.50"), True, 10),
    ("product-zero", "Zero-stock product", Decimal("8.00"), True, 0),
    ("product-inactive", "Inactive product", Decimal("5.00"), False, 4),
)


def seed_synthetic_data(database: Database) -> None:
    """Insert the required synthetic products and inventory when absent.

    Args:
        database: Database whose schema has already been initialized.
    """
    session: Session = database.session_factory()
    try:
        for product_id, name, unit_price, is_active, quantity in SYNTHETIC_PRODUCTS:
            if session.get(Product, product_id) is None:
                session.add(
                    Product(
                        id=product_id,
                        name=name,
                        unit_price=unit_price,
                        is_active=is_active,
                    )
                )
            if session.get(InventoryItem, product_id) is None:
                session.add(InventoryItem(product_id=product_id, quantity=quantity))
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def main() -> None:
    """Initialize schema and seed the database selected by ``DATABASE_URL``."""
    database = Database()
    database.create_all()
    seed_synthetic_data(database)
    print("Synthetic seed: complete")


if __name__ == "__main__":
    main()
