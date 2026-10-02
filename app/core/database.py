"""SQLAlchemy configuration and SQLite-specific safeguards."""

from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DEFAULT_DATABASE_URL = "sqlite:///./runtime/lab02.db"


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models in this application."""


class Database:
    """Own the database engine and sessions used by one application instance."""

    def __init__(self, database_url: str | None = None) -> None:
        """Configure an engine from an explicit URL or ``DATABASE_URL``.

        Args:
            database_url: URL used by this application instance when provided.
        """
        self.url = database_url or os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
        self._prepare_default_directory()
        engine_options: dict[str, object] = {}
        if self.url.startswith("sqlite"):
            engine_options["connect_args"] = {"check_same_thread": False}
        self.engine: Engine = create_engine(self.url, **engine_options)
        if self.url.startswith("sqlite"):
            event.listen(self.engine, "connect", self._enable_sqlite_foreign_keys)
        self.session_factory = sessionmaker(
            bind=self.engine,
            autoflush=False,
            expire_on_commit=False,
        )

    def _prepare_default_directory(self) -> None:
        """Create the ignored default runtime directory when it is selected."""
        if self.url == DEFAULT_DATABASE_URL:
            Path("runtime").mkdir(exist_ok=True)

    @staticmethod
    def _enable_sqlite_foreign_keys(connection: object, _: object) -> None:
        """Enable foreign-key enforcement for each SQLite connection."""
        cursor = connection.cursor()  # type: ignore[union-attr]
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    def session(self) -> Generator[Session, None, None]:
        """Yield one request-scoped SQLAlchemy session.

        Yields:
            An open session that callers must close after use.
        """
        session = self.session_factory()
        try:
            yield session
        finally:
            session.close()

    def create_all(self) -> None:
        """Create the application's tables when they do not already exist."""
        Base.metadata.create_all(self.engine)
