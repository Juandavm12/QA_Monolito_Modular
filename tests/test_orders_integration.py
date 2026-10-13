"""Integration tests for the Orders transaction boundary."""

from __future__ import annotations

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import Database
from app.core.errors import (
    InsufficientStockError,
    PersistenceError,
    ProductInactiveError,
)
from app.modules.inventory.services import InventoryService
from app.modules.orders.models import Order
from app.modules.orders.services import CreateOrderCommand, OrdersService


class FailingOrderPersistence:
    """Test double that fails after Inventory has reserved stock."""

    def save_order(self, session: Session, order: Order) -> None:
        """Raise a controlled technical failure during order persistence."""
        del session, order
        raise RuntimeError("Controlled persistence failure")


class FailingFlushedOrderPersistence:
    """Fail after both the stock update and order insert reach SQLite."""

    def save_order(self, session: Session, order: Order) -> None:
        """Flush and verify uncommitted SQL state before the controlled failure."""
        session.add(order)
        session.flush()
        assert InventoryService().get_inventory(session, order.product_id).quantity == 7
        assert _order_count(session) == 1
        raise RuntimeError("Controlled post-flush persistence failure")


def _order_count(session: Session) -> int:
    """Return the number of persisted orders for transaction assertions."""
    return session.scalar(select(func.count()).select_from(Order)) or 0


def test_places_order_and_commits_stock(database: Database) -> None:
    """Orders commits the new order and its matching stock reservation."""
    session = database.session_factory()
    try:
        order = OrdersService().place_order(
            session,
            CreateOrderCommand(product_id="active-product", quantity=3),
        )
    finally:
        session.close()

    verification_session = database.session_factory()
    try:
        inventory = InventoryService().get_inventory(
            verification_session,
            "active-product",
        )
        persisted_order = OrdersService().get_order(verification_session, order.id)
        assert inventory.quantity == 7
        assert persisted_order.quantity == 3
        assert persisted_order.product_id == "active-product"
    finally:
        verification_session.close()


def test_insufficient_stock_rolls_back(database: Database) -> None:
    """Insufficient stock leaves neither a new order nor a stock change."""
    session = database.session_factory()
    try:
        with pytest.raises(InsufficientStockError):
            OrdersService().place_order(
                session,
                CreateOrderCommand(product_id="active-product", quantity=11),
            )
    finally:
        session.close()

    verification_session = database.session_factory()
    try:
        inventory = InventoryService().get_inventory(
            verification_session,
            "active-product",
        )
        assert inventory.quantity == 10
        assert _order_count(verification_session) == 0
    finally:
        verification_session.close()


def test_non_sellable_product_does_not_reserve(database: Database) -> None:
    """Catalog rejection happens before Inventory can reserve stock."""
    session = database.session_factory()
    try:
        with pytest.raises(ProductInactiveError):
            OrdersService().place_order(
                session,
                CreateOrderCommand(product_id="inactive-product", quantity=2),
            )
    finally:
        session.close()

    verification_session = database.session_factory()
    try:
        inventory = InventoryService().get_inventory(
            verification_session,
            "inactive-product",
        )
        assert inventory.quantity == 4
        assert _order_count(verification_session) == 0
    finally:
        verification_session.close()


def test_post_flush_failure_rolls_back_before_session_close(database: Database) -> None:
    """Explicit rollback restores SQL state before closing the caller's session."""
    session = database.session_factory()
    service = OrdersService(persistence=FailingFlushedOrderPersistence())
    try:
        with pytest.raises(PersistenceError) as failure:
            service.place_order(
                session,
                CreateOrderCommand(product_id="active-product", quantity=3),
            )
        assert isinstance(failure.value.__cause__, RuntimeError)
        assert str(failure.value.__cause__) == "Controlled post-flush persistence failure"
        assert InventoryService().get_inventory(session, "active-product").quantity == 10
        assert _order_count(session) == 0

        verification_session = database.session_factory()
        try:
            inventory = InventoryService().get_inventory(
                verification_session, "active-product",
            )
            assert inventory.quantity == 10
            assert _order_count(verification_session) == 0
        finally:
            verification_session.close()
    finally:
        session.close()


def test_persistence_failure_rolls_back(database: Database) -> None:
    """A failure after reservation rolls back both Orders and Inventory."""
    session = database.session_factory()
    service = OrdersService(persistence=FailingOrderPersistence())
    try:
        with pytest.raises(PersistenceError):
            service.place_order(
                session,
                CreateOrderCommand(product_id="active-product", quantity=3),
            )
    finally:
        session.close()

    verification_session = database.session_factory()
    try:
        inventory = InventoryService().get_inventory(
            verification_session,
            "active-product",
        )
        assert inventory.quantity == 10
        assert _order_count(verification_session) == 0
    finally:
        verification_session.close()
