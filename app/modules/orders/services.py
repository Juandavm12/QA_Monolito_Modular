"""Public Orders application-service interfaces."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Protocol
from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.errors import (
    DomainError,
    OrderNotFoundError,
    PersistenceError,
)
from app.modules.catalog.services import CatalogService
from app.modules.inventory.services import InventoryService
from app.modules.orders.models import Order


@dataclass(frozen=True)
class CreateOrderCommand:
    """Input required to place one order."""

    product_id: str
    quantity: int


@dataclass(frozen=True)
class OrderView:
    """Order data that HTTP handlers may consume."""

    id: str
    product_id: str
    quantity: int
    unit_price: Decimal
    created_at: datetime


class OrderPersistence(Protocol):
    """Persist Orders-owned models in an existing transaction."""

    def save_order(self, session: Session, order: Order) -> None:
        """Stage an order for persistence without committing.

        Args:
            session: Session owned by Orders.
            order: New order to stage.
        """


class SqlAlchemyOrderPersistence:
    """Default persistence adapter for the Orders model."""

    def save_order(self, session: Session, order: Order) -> None:
        """Stage an order in the current SQLAlchemy session.

        Args:
            session: Session owned by Orders.
            order: New order to stage.
        """
        session.add(order)


class OrdersService:
    """Coordinate Catalog, Inventory, and Orders persistence atomically."""

    def __init__(
        self,
        catalog: CatalogService | None = None,
        inventory: InventoryService | None = None,
        persistence: OrderPersistence | None = None,
    ) -> None:
        """Configure module collaborators.

        Args:
            catalog: Catalog contract used to validate sellable products.
            inventory: Inventory contract used to reserve stock.
            persistence: Orders persistence adapter used after reservation.
        """
        self._catalog = catalog or CatalogService()
        self._inventory = inventory or InventoryService()
        self._persistence = persistence or SqlAlchemyOrderPersistence()

    def place_order(self, session: Session, command: CreateOrderCommand) -> OrderView:
        """Validate, reserve, persist, and commit one order as one transaction.

        Args:
            session: Session supplied by the caller and committed by Orders.
            command: Product and positive quantity requested by the caller.

        Returns:
            The committed order view.

        Raises:
            DomainError: If the product is not sellable or stock is insufficient.
            PersistenceError: If order persistence fails after reservation.
            ValueError: If the requested quantity is not positive.
        """
        if command.quantity <= 0:
            raise ValueError("Quantity must be positive.")

        try:
            product = self._catalog.get_active_product(session, command.product_id)
            self._inventory.reserve(session, command.product_id, command.quantity)
            order = Order(
                id=str(uuid4()),
                product_id=product.id,
                quantity=command.quantity,
                unit_price=product.unit_price,
            )
            self._persistence.save_order(session, order)
            session.commit()
        except DomainError:
            session.rollback()
            raise
        except Exception as error:
            session.rollback()
            raise PersistenceError("Order persistence failed.") from error

        return self._to_view(order)

    def get_order(self, session: Session, order_id: str) -> OrderView:
        """Return an order by public identifier.

        Args:
            session: Session used for the lookup.
            order_id: Public order identifier.

        Returns:
            The order view.

        Raises:
            OrderNotFoundError: If no order has the identifier.
        """
        order = session.get(Order, order_id)
        if order is None:
            raise OrderNotFoundError("Order does not exist.")
        return self._to_view(order)

    @staticmethod
    def _to_view(order: Order) -> OrderView:
        """Convert the private persistence model into the public view."""
        return OrderView(
            id=order.id,
            product_id=order.product_id,
            quantity=order.quantity,
            unit_price=order.unit_price,
            created_at=order.created_at,
        )
