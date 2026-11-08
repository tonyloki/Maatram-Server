"""Common Pydantic schemas and standard response envelopes."""

from typing import Annotated, Any, TypeVar

from fastapi import Query
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


class PaginationParams:
    """Standardized pagination dependency enforcing bounds and alias support."""

    def __init__(
        self,
        page: Annotated[int, Query(ge=1, description="Page number (1-indexed)")] = 1,
        limit: Annotated[
            int | None,
            Query(ge=1, le=100, description="Items per page (max 100)"),
        ] = None,
        page_size: Annotated[
            int | None,
            Query(ge=1, le=100, description="Items per page alias (max 100)"),
        ] = None,
    ):
        self.page = page
        self.limit = limit if limit is not None else (page_size if page_size is not None else 20)
        self.page_size = self.limit
        self.offset = (self.page - 1) * self.limit
