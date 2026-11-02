"""Base declarative model and custom types for cross-database compatibility."""

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, DateTime, String, Uuid
from sqlalchemy.dialects.postgresql import ARRAY, INET, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import TypeDecorator


# Cross-dialect INET type (PostgreSQL INET, String(45) on other dialects)
class CompatibleINET(TypeDecorator[str]):
    """INET column type compatible with PostgreSQL and SQLite."""

    impl = String(45)
    cache_ok = True

    def load_dialect_impl(self, dialect: Any) -> Any:
        if dialect.name == "postgresql":
            return dialect.type_descriptor(INET())
        return dialect.type_descriptor(String(45))


# Cross-dialect JSONB type (PostgreSQL JSONB, JSON on SQLite)
class CompatibleJSONB(TypeDecorator[Any]):
    """JSONB column type compatible with PostgreSQL and SQLite."""

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect: Any) -> Any:
        if dialect.name == "postgresql":
            return dialect.type_descriptor(JSONB())
        return dialect.type_descriptor(JSON())


# Cross-dialect String Array (PostgreSQL TEXT[], JSON on SQLite)
class CompatibleTextArray(TypeDecorator[list[str]]):
    """Array of strings compatible with PostgreSQL and SQLite."""

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect: Any) -> Any:
        if dialect.name == "postgresql":
            return dialect.type_descriptor(ARRAY(String))
        return dialect.type_descriptor(JSON())


def utc_now() -> datetime:
    """Return current UTC timezone-aware datetime."""
    return datetime.now(UTC)


class Base(DeclarativeBase):
    """Declarative Base class for all 29 domain models."""

    # Automatically derive tablename or allow explicit __tablename__
    pass


class UUIDPrimaryKeyMixin:
    """Primary key mixin using UUIDv4 / UUIDv7."""

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )


class TimestampMixin:
    """Audit timestamps mixin for entity creation and modification."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )
