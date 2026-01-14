from typing import Optional
from pydantic import Field

from src.schemas.base import BaseSchema, TimestampSchema
from src.models.contact_history import HistoryType


class ContactHistoryBase(BaseSchema):
    """Base contact history schema."""
    
    type: HistoryType
    title: str = Field(..., min_length=1, max_length=255)
    content: Optional[str] = None


class NoteCreate(BaseSchema):
    """Schema for creating a note."""
    
    content: str = Field(..., min_length=1)


class CallCreate(BaseSchema):
    """Schema for documenting a call."""
    
    content: str = Field(..., min_length=1)
    duration_minutes: Optional[int] = None
    outcome: Optional[str] = None  # reached, voicemail, no_answer


class ContactHistoryUpdate(BaseSchema):
    """Schema for updating a history entry."""
    
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = None


class ContactHistoryResponse(ContactHistoryBase, TimestampSchema):
    """Schema for contact history response."""
    
    id: int
    contact_id: int
    created_by: Optional[str] = None
    extra_data: Optional[str] = None
