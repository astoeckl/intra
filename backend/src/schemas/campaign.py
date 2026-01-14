from typing import Optional
from datetime import date
from pydantic import Field

from src.schemas.base import BaseSchema, TimestampSchema


class CampaignBase(BaseSchema):
    """Base campaign schema."""
    
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    type: str = Field(..., max_length=50)  # social_media, email, landing_page
    source: Optional[str] = Field(None, max_length=100)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: bool = True
    landing_page_url: Optional[str] = Field(None, max_length=500)
    lead_magnet: Optional[str] = Field(None, max_length=255)


class CampaignCreate(CampaignBase):
    """Schema for creating a campaign."""
    pass


class CampaignUpdate(BaseSchema):
    """Schema for updating a campaign."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    type: Optional[str] = Field(None, max_length=50)
    source: Optional[str] = Field(None, max_length=100)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None
    landing_page_url: Optional[str] = Field(None, max_length=500)
    lead_magnet: Optional[str] = Field(None, max_length=255)


class CampaignResponse(CampaignBase, TimestampSchema):
    """Schema for campaign response."""
    
    id: int
    leads_count: int = 0


class CampaignListResponse(CampaignBase, TimestampSchema):
    """Schema for campaign list item."""
    
    id: int
