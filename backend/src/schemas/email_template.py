from typing import Optional
from pydantic import Field

from src.schemas.base import BaseSchema, TimestampSchema


class EmailTemplateBase(BaseSchema):
    """Base email template schema."""
    
    name: str = Field(..., min_length=1, max_length=255)
    subject: str = Field(..., min_length=1, max_length=500)
    body: str = Field(..., min_length=1)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50)
    is_active: bool = True


class EmailTemplateCreate(EmailTemplateBase):
    """Schema for creating an email template."""
    
    variables: Optional[list[str]] = None


class EmailTemplateUpdate(BaseSchema):
    """Schema for updating an email template."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    subject: Optional[str] = Field(None, min_length=1, max_length=500)
    body: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None
    variables: Optional[list[str]] = None


class EmailTemplateResponse(EmailTemplateBase, TimestampSchema):
    """Schema for email template response."""
    
    id: int
    variables: Optional[list[str]] = None


class EmailSend(BaseSchema):
    """Schema for sending an email."""
    
    template_id: int
    contact_id: int
    subject_override: Optional[str] = None
    attachments: Optional[list[str]] = None


class EmailPreview(BaseSchema):
    """Schema for email preview request."""
    
    template_id: int
    contact_id: int


class EmailPreviewResponse(BaseSchema):
    """Schema for email preview response."""
    
    subject: str
    body: str
    to_email: str
    to_name: str
