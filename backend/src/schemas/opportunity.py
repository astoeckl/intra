from typing import Optional
from datetime import date
from pydantic import Field

from src.schemas.base import BaseSchema, TimestampSchema
from src.models.opportunity import OpportunityStage


class OpportunityBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=255)
    stage: OpportunityStage = OpportunityStage.QUALIFICATION
    expected_value: Optional[float] = Field(None, ge=0)
    probability: int = Field(10, ge=0, le=100)
    expected_close_date: Optional[date] = None
    notes: Optional[str] = None


class OpportunityCreate(OpportunityBase):
    company_id: Optional[int] = None
    contact_id: Optional[int] = None


class OpportunityCreateFromLead(BaseSchema):
    name: str = Field(..., min_length=1, max_length=255)
    expected_value: Optional[float] = Field(None, ge=0)
    expected_close_date: Optional[date] = None
    notes: Optional[str] = None


class OpportunityUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    stage: Optional[OpportunityStage] = None
    expected_value: Optional[float] = Field(None, ge=0)
    probability: Optional[int] = Field(None, ge=0, le=100)
    expected_close_date: Optional[date] = None
    notes: Optional[str] = None
    company_id: Optional[int] = None
    contact_id: Optional[int] = None


class OpportunityClose(BaseSchema):
    won: bool
    close_reason: Optional[str] = Field(None, max_length=255)
    actual_value: Optional[float] = Field(None, ge=0)


class OpportunityResponse(OpportunityBase, TimestampSchema):
    id: int
    actual_close_date: Optional[date] = None
    close_reason: Optional[str] = None
    company_id: Optional[int] = None
    contact_id: Optional[int] = None
    lead_id: Optional[int] = None
    company_name: Optional[str] = None
    contact_name: Optional[str] = None


class OpportunityListResponse(TimestampSchema):
    id: int
    name: str
    stage: OpportunityStage
    expected_value: Optional[float] = None
    probability: int
    expected_close_date: Optional[date] = None
    actual_close_date: Optional[date] = None
    company_id: Optional[int] = None
    company_name: Optional[str] = None
    contact_id: Optional[int] = None
    contact_name: Optional[str] = None


class PipelineStageStats(BaseSchema):
    stage: OpportunityStage
    count: int
    total_value: float
    weighted_value: float


class PipelineStats(BaseSchema):
    total_opportunities: int
    total_value: float
    weighted_value: float
    stages: list[PipelineStageStats]
    win_rate: float
    average_deal_size: float
