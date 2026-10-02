"""Inventory persistence model owned by the Inventory module."""

from __future__ import annotations

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class InventoryItem(Base):
    """Available units for one Catalog product."""

    __tablename__ = "inventory_items"
    __table_args__ = (CheckConstraint("quantity >= 0", name="ck_inventory_quantity"),)

    product_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("products.id"),
        primary_key=True,
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
