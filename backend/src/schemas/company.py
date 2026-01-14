from typing import Optional
from pydantic import EmailStr, HttpUrl, Field

from src.schemas.base import BaseSchema, TimestampSchema


class CompanyBase(BaseSchema):
    """Base company schema."""
    
    name: str = Field(..., min_length=1, max_length=255)
    street: Optional[str] = Field(None, max_length=255)
    zip_code: Optional[str] = Field(None, max_length=20)
    city: Optional[str] = Field(None, max_length=100)
    country: str = Field(default="Österreich", max_length=100)
    website: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None
    employee_count: Optional[int] = Field(None, ge=0)
    potential_category: Optional[str] = Field(None, pattern="^[ABCD]$")
    industry: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class CompanyCreate(CompanyBase):
    """Schema for creating a company."""
    pass


class CompanyUpdate(BaseSchema):
    """Schema for updating a company."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    street: Optional[str] = Field(None, max_length=255)
    zip_code: Optional[str] = Field(None, max_length=20)
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None
    employee_count: Optional[int] = Field(None, ge=0)
    potential_category: Optional[str] = Field(None, pattern="^[ABCD]$")
    industry: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class CompanyResponse(CompanyBase, TimestampSchema):
    """Schema for company response."""
    
    id: int
    contacts_count: int = 0


class CompanyListResponse(CompanyBase, TimestampSchema):
    """Schema for company list item."""
    
    id: int
