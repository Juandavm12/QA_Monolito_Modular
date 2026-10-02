"""Application errors mapped by the HTTP boundary."""


class DomainError(Exception):
    """Base class for controlled business errors."""


class ProductNotFoundError(DomainError):
    """Raised when Catalog does not contain the requested product."""


class ProductInactiveError(DomainError):
    """Raised when a Catalog product cannot be sold."""


class InsufficientStockError(DomainError):
    """Raised when Inventory cannot reserve the requested quantity."""


class OrderNotFoundError(DomainError):
    """Raised when Orders does not contain the requested order."""


class PersistenceError(Exception):
    """Raised when persistence fails without exposing implementation details."""
