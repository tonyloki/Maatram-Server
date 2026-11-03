"""Common Pydantic schemas and standard response envelopes."""

from typing import Any, TypeVar

from pydantic import BaseModel, ConfigDict, Field

DataT = TypeVar("DataT")


class BaseSchema(BaseModel):
    """Base schema with strict configurations."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class ErrorDetail(BaseModel):
    """Individual field error or metadata."""

    field: str | None = None
    message: str
    type: str | None = None


class ErrorEnvelope(BaseModel):
    """Standardized error envelope."""

    code: str
    message: str
    details: Any = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """Standard HTTP error response payload."""

    error: ErrorEnvelope


class SuccessResponse[DataT](BaseSchema):
    """Standard success payload envelope."""

    data: DataT
    message: str | None = None


class PaginationMetadata(BaseModel):
    """Pagination cursor and offset metadata."""

    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


class PaginatedResponse[DataT](BaseSchema):
    """Paginated collection envelope."""

    items: list[DataT]
    pagination: PaginationMetadata
