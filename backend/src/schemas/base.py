"""
Base Schema Classes.

Provides reusable Pydantic schemas for common patterns.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """
    Base schema with ORM mode enabled.

    All schemas inheriting from this support creating instances
    from SQLAlchemy model objects via from_attributes=True.
    """

    model_config = ConfigDict(from_attributes=True)


class TimestampSchema(BaseSchema):
    """Schema including created_at and updated_at timestamps."""

    created_at: datetime
    updated_at: datetime


class PaginationParams(BaseModel):
    """
    Input parameters for paginated endpoints.

    Provides calculated offset property for database queries.
    """

    page: int = 1
    page_size: int = 20

    @property
    def offset(self) -> int:
        """Calculate database offset from page number."""
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseModel):
    """
    Standard wrapper for paginated API responses.

    Contains items array plus pagination metadata for
    client-side pagination controls.
    """

    items: list
    total: int
    page: int
    page_size: int
    total_pages: int
