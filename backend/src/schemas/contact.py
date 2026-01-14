from typing import Optional
from pydantic import EmailStr, Field

from src.schemas.base import BaseSchema, TimestampSchema
from src.schemas.company import CompanyListResponse


class ContactBase(BaseSchema):
    """Base contact schema."""
    
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    mobile: Optional[str] = Field(None, max_length=50)
    position: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    salutation: Optional[str] = Field(None, max_length=20)
    title: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None
    is_primary: bool = False
    is_active: bool = True


class ContactCreate(ContactBase):
    """Schema for creating a contact."""
    
    company_id: Optional[int] = None


class ContactUpdate(BaseSchema):
    """Schema for updating a contact."""
    
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    mobile: Optional[str] = Field(None, max_length=50)
    position: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    salutation: Optional[str] = Field(None, max_length=20)
    title: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None
    is_primary: Optional[bool] = None
    is_active: Optional[bool] = None
    company_id: Optional[int] = None


class ContactResponse(ContactBase, TimestampSchema):
    """Schema for contact response."""
    
    id: int
    company_id: Optional[int] = None
    company: Optional[CompanyListResponse] = None
    full_name: str


class ContactListResponse(TimestampSchema):
    """Schema for contact list item."""
    
    id: int
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    position: Optional[str] = None
    company_id: Optional[int] = None
    company_name: Optional[str] = None
    is_active: bool


class ContactSearchResult(BaseSchema):
    """Schema for contact search autocomplete."""
    
    id: int
    full_name: str
    email: Optional[str] = None
    company_name: Optional[str] = None
