from typing import Optional
from pydantic import Field, EmailStr

from src.schemas.base import BaseSchema, TimestampSchema
from src.schemas.contact import ContactListResponse
from src.schemas.campaign import CampaignListResponse
from src.models.lead import LeadStatus


class LeadBase(BaseSchema):
    status: LeadStatus = LeadStatus.COLD
    source: Optional[str] = Field(None, max_length=100)
    utm_source: Optional[str] = Field(None, max_length=100)
    utm_medium: Optional[str] = Field(None, max_length=100)
    utm_campaign: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class LeadCreate(LeadBase):
    contact_id: int
    campaign_id: Optional[int] = None


class LeadCreateFromForm(BaseSchema):
    """Landing page form submission."""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=50)
    company_name: Optional[str] = Field(None, max_length=255)
    campaign_id: Optional[int] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None


class LeadUpdate(BaseSchema):
    status: Optional[LeadStatus] = None
    source: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    campaign_id: Optional[int] = None


class LeadImportRow(BaseSchema):
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company_name: Optional[str] = None
    source: Optional[str] = None


class LeadImportResult(BaseSchema):
    total_rows: int
    imported: int
    failed: int
    errors: list[str]


class LeadResponse(LeadBase, TimestampSchema):
    id: int
    contact_id: int
    campaign_id: Optional[int] = None
    contact: Optional[ContactListResponse] = None
    campaign: Optional[CampaignListResponse] = None


class LeadListResponse(TimestampSchema):
    id: int
    status: LeadStatus
    source: Optional[str] = None
    contact_id: int
    contact_name: str
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_mobile: Optional[str] = None
    contact_position: Optional[str] = None
    company_name: Optional[str] = None
    campaign_id: Optional[int] = None
    campaign_name: Optional[str] = None
