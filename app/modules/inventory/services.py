"""Public Inventory application-service interfaces."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.errors import InsufficientStockError, ProductNotFoundError
from app.modules.inventory.models import InventoryItem


@dataclass(frozen=True)
class InventoryView:
    """Inventory data that HTTP handlers and Orders may consume."""

    product_id: str
    quantity: int


class InventoryService:
    """Expose inventory lookups and reservations through the caller's session."""

    def get_inventory(self, session: Session, product_id: str) -> InventoryView:
        """Return current stock for a product.

        Args:
            session: Session used for the lookup.
            product_id: Public product identifier.

        Returns:
            The current inventory view.

        Raises:
            ProductNotFoundError: If no inventory record exists for the product.
        """
        item = session.get(InventoryItem, product_id)
        if item is None:
            raise ProductNotFoundError("Product inventory does not exist.")
        return self._to_view(item)

    def reserve(self, session: Session, product_id: str, quantity: int) -> None:
        """Reserve stock without committing the caller's transaction.

        Args:
            session: Session owned by the calling application service.
            product_id: Public product identifier.
            quantity: Number of units to reserve.

        Raises:
            ProductNotFoundError: If no inventory record exists for the product.
            InsufficientStockError: If fewer than the requested units are available.
        """
        item = session.get(InventoryItem, product_id)
        if item is None:
            raise ProductNotFoundError("Product inventory does not exist.")
        if item.quantity < quantity:
            raise InsufficientStockError("Insufficient stock.")
        item.quantity -= quantity

    @staticmethod
    def _to_view(item: InventoryItem) -> InventoryView:
        """Convert the private persistence model into the public view."""
        return InventoryView(product_id=item.product_id, quantity=item.quantity)
