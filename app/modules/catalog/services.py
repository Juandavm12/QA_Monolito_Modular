"""Public Catalog application-service interfaces."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import ProductInactiveError, ProductNotFoundError
from app.modules.catalog.models import Product


@dataclass(frozen=True)
class ProductView:
    """Catalog data that other modules and HTTP handlers may consume."""

    id: str
    name: str
    unit_price: Decimal
    is_active: bool


class CatalogService:
    """Expose Catalog operations without exposing its SQLAlchemy model."""

    def get_active_product(self, session: Session, product_id: str) -> ProductView:
        """Return a sellable product or a controlled Catalog error.

        Args:
            session: Session participating in the caller's unit of work.
            product_id: Public identifier for the requested product.

        Returns:
            A read-only view with the applicable unit price.

        Raises:
            ProductNotFoundError: If no product has the identifier.
            ProductInactiveError: If the product is not sellable.
        """
        product = session.get(Product, product_id)
        if product is None:
            raise ProductNotFoundError("Product does not exist.")
        if not product.is_active:
            raise ProductInactiveError("Product is inactive.")
        return self._to_view(product)

    def get_product(self, session: Session, product_id: str) -> ProductView:
        """Return a Catalog product regardless of active state.

        Args:
            session: Session used for the lookup.
            product_id: Public identifier for the requested product.

        Returns:
            The product view.

        Raises:
            ProductNotFoundError: If no product has the identifier.
        """
        product = session.get(Product, product_id)
        if product is None:
            raise ProductNotFoundError("Product does not exist.")
        return self._to_view(product)

    def list_products(self, session: Session) -> list[ProductView]:
        """List Catalog products in a stable identifier order.

        Args:
            session: Session used for the lookup.

        Returns:
            Product views ordered by identifier.
        """
        products = session.scalars(select(Product).order_by(Product.id)).all()
        return [self._to_view(product) for product in products]

    @staticmethod
    def _to_view(product: Product) -> ProductView:
        """Convert the private persistence model into the public view."""
        return ProductView(
            id=product.id,
            name=product.name,
            unit_price=product.unit_price,
            is_active=product.is_active,
        )
