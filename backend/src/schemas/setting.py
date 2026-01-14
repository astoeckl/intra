from typing import Optional, Literal
from pydantic import Field

from src.schemas.base import BaseSchema, TimestampSchema


# ============ Setting Schemas ============

class SettingBase(BaseSchema):
    """Base setting schema."""
    
    key: str = Field(..., min_length=1, max_length=255)
    category: str = Field(..., min_length=1, max_length=100)
    value: Optional[str] = None
    value_type: Literal["string", "number", "boolean", "json"] = "string"


class SettingCreate(SettingBase):
    """Schema for creating a setting."""
    pass


class SettingUpdate(BaseSchema):
    """Schema for updating a setting."""
    
    value: Optional[str] = None
    value_type: Optional[Literal["string", "number", "boolean", "json"]] = None


class SettingResponse(SettingBase, TimestampSchema):
    """Schema for setting response."""
    
    id: int


# ============ LookupValue Schemas ============

class LookupValueBase(BaseSchema):
    """Base lookup value schema."""
    
    category: str = Field(..., min_length=1, max_length=100)
    value: str = Field(..., min_length=1, max_length=100)
    label: str = Field(..., min_length=1, max_length=255)
    sort_order: int = Field(default=0, ge=0)
    is_active: bool = True


class LookupValueCreate(LookupValueBase):
    """Schema for creating a lookup value."""
    pass


class LookupValueUpdate(BaseSchema):
    """Schema for updating a lookup value."""
    
    value: Optional[str] = Field(None, min_length=1, max_length=100)
    label: Optional[str] = Field(None, min_length=1, max_length=255)
    sort_order: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class LookupValueResponse(LookupValueBase, TimestampSchema):
    """Schema for lookup value response."""
    
    id: int


# ============ Lookup Categories ============

# List of valid lookup categories for reference
LOOKUP_CATEGORIES = [
    "lead_status",
    "potential_category",
    "industry",
    "country",
    "salutation",
    "title",
    "contact_lead_status",
    "task_priority",
    "campaign_type",
    "campaign_source",
]
