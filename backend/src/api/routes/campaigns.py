"""
Campaign API Routes.

Provides CRUD operations for marketing campaigns. Campaigns group leads
and track their acquisition source (social media, email, landing pages).
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.schemas.campaign import (
    CampaignCreate,
    CampaignUpdate,
    CampaignResponse,
    CampaignListResponse,
)
from src.schemas.base import PaginatedResponse
from src.services import campaign_service

router = APIRouter()


@router.get("", response_model=PaginatedResponse)
async def list_campaigns(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_active: bool = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """
    List campaigns with pagination and optional active filter.

    Args:
        page: Page number (1-indexed).
        page_size: Items per page (max 100).
        is_active: Filter by active status. None returns all.

    Returns:
        Paginated list of campaigns sorted by creation date (newest first).
    """
    skip = (page - 1) * page_size
    campaigns, total = await campaign_service.get_campaigns(
        db, skip=skip, limit=page_size, is_active=is_active
    )

    return PaginatedResponse(
        items=[CampaignListResponse.model_validate(c) for c in campaigns],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve a single campaign by ID.

    Returns:
        Campaign details including associated leads count.

    Raises:
        HTTPException 404: Campaign does not exist.
    """
    campaign = await campaign_service.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    response = CampaignResponse.model_validate(campaign)
    response.leads_count = len(campaign.leads) if campaign.leads else 0
    return response


@router.post("", response_model=CampaignResponse, status_code=201)
async def create_campaign(
    campaign_data: CampaignCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new marketing campaign.

    Args:
        campaign_data: Campaign details including name, type, and optional dates.

    Returns:
        Created campaign with assigned ID.
    """
    campaign = await campaign_service.create_campaign(db, campaign_data)
    return CampaignResponse.model_validate(campaign)


@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: int,
    campaign_data: CampaignUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update an existing campaign.

    Args:
        campaign_id: Campaign identifier.
        campaign_data: Fields to update. Only provided fields are modified.

    Returns:
        Updated campaign.

    Raises:
        HTTPException 404: Campaign does not exist.
    """
    campaign = await campaign_service.update_campaign(db, campaign_id, campaign_data)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return CampaignResponse.model_validate(campaign)
