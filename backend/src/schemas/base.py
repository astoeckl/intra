from datetime import datetime
from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    
    model_config = ConfigDict(from_attributes=True)


class TimestampSchema(BaseSchema):
    """Schema with timestamp fields."""
    
    created_at: datetime
    updated_at: datetime


class PaginationParams(BaseModel):
    """Pagination parameters."""
    
    page: int = 1
    page_size: int = 20
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""
    
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int
