"""FastAPI application factory for the modular ordering laboratory."""

from __future__ import annotations

from collections.abc import Generator
from datetime import datetime
from decimal import Decimal
from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import Database
from app.core.errors import (
    InsufficientStockError,
    OrderNotFoundError,
    PersistenceError,
    ProductInactiveError,
    ProductNotFoundError,
)
# Import all ORM models before any call to Database.create_all().
from app.modules.catalog.models import Product  # noqa: F401
from app.modules.catalog.services import CatalogService, ProductView
from app.modules.inventory.models import InventoryItem  # noqa: F401
from app.modules.inventory.services import InventoryService, InventoryView
from app.modules.orders.models import Order  # noqa: F401
from app.modules.orders.services import CreateOrderCommand, OrdersService, OrderView


class ProductResponse(BaseModel):
    """Product payload returned by the Catalog endpoint."""

    id: str
    name: str
    unit_price: Decimal
    is_active: bool


class InventoryResponse(BaseModel):
    """Inventory payload returned by the Inventory endpoint."""

    product_id: str
    quantity: int


class CreateOrderRequest(BaseModel):
    """Validated payload accepted by the order endpoint."""

    product_id: str = Field(min_length=1, max_length=50)
    quantity: int = Field(gt=0)


class OrderResponse(BaseModel):
    """Order payload returned after placement or lookup."""

    id: str
    product_id: str
    quantity: int
    unit_price: Decimal
    created_at: datetime


def create_app(database_url: str | None = None) -> FastAPI:
    """Build an application instance with its own database infrastructure.

    Args:
        database_url: Optional SQLAlchemy URL, primarily for isolated tests.

    Returns:
        A configured FastAPI application.
    """
    database = Database(database_url)
    database.create_all()
    catalog_service = CatalogService()
    inventory_service = InventoryService()
    orders_service = OrdersService(
        catalog=catalog_service,
        inventory=inventory_service,
    )

    app = FastAPI(title="QA Monolito Modular")
    app.state.database = database

    def get_session() -> Generator[Session, None, None]:
        """Provide one request-scoped database session."""
        yield from database.session()

    @app.exception_handler(ProductNotFoundError)
    async def product_not_found_handler(
        _request: object,
        _error: ProductNotFoundError,
    ) -> JSONResponse:
        """Map missing products to a public 404 response."""
        return JSONResponse(status_code=404, content={"detail": "Product not found."})

    @app.exception_handler(OrderNotFoundError)
    async def order_not_found_handler(
        _request: object,
        _error: OrderNotFoundError,
    ) -> JSONResponse:
        """Map missing orders to a public 404 response."""
        return JSONResponse(status_code=404, content={"detail": "Order not found."})

    @app.exception_handler(ProductInactiveError)
    async def product_inactive_handler(
        _request: object,
        _error: ProductInactiveError,
    ) -> JSONResponse:
        """Map inactive products to a public conflict response."""
        return JSONResponse(status_code=409, content={"detail": "Product is inactive."})

    @app.exception_handler(InsufficientStockError)
    async def insufficient_stock_handler(
        _request: object,
        _error: InsufficientStockError,
    ) -> JSONResponse:
        """Map unavailable inventory to a public conflict response."""
        return JSONResponse(status_code=409, content={"detail": "Insufficient stock."})

    @app.exception_handler(PersistenceError)
    async def persistence_error_handler(
        _request: object,
        _error: PersistenceError,
    ) -> JSONResponse:
        """Map technical persistence failures without exposing internals."""
        return JSONResponse(
            status_code=500,
            content={"detail": "Unable to persist order."},
        )

    @app.get("/health")
    def health() -> dict[str, str]:
        """Return a minimal application health response."""
        return {"status": "ok"}

    @app.get("/products", response_model=list[ProductResponse])
    def list_products(
        session: Session = Depends(get_session),
    ) -> list[ProductView]:
        """List Catalog products in identifier order."""
        return catalog_service.list_products(session)

    @app.get("/inventory/{product_id}", response_model=InventoryResponse)
    def get_inventory(
        product_id: str,
        session: Session = Depends(get_session),
    ) -> InventoryView:
        """Return available stock for a product."""
        return inventory_service.get_inventory(session, product_id)

    @app.post("/orders", response_model=OrderResponse, status_code=201)
    def place_order(
        request: CreateOrderRequest,
        session: Session = Depends(get_session),
    ) -> OrderView:
        """Place one order through the Orders transaction boundary."""
        command = CreateOrderCommand(
            product_id=request.product_id,
            quantity=request.quantity,
        )
        return orders_service.place_order(session, command)

    @app.get("/orders/{order_id}", response_model=OrderResponse)
    def get_order(
        order_id: str,
        session: Session = Depends(get_session),
    ) -> OrderView:
        """Look up an existing order by identifier."""
        return orders_service.get_order(session, order_id)

    return app
