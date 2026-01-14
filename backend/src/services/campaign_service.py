from typing import Optional, Sequence
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.campaign import Campaign
from src.schemas.campaign import CampaignCreate, CampaignUpdate


async def get_campaigns(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    is_active: Optional[bool] = None,
) -> tuple[Sequence[Campaign], int]:
    """Get all campaigns with pagination."""
    query = select(Campaign)
    count_query = select(func.count(Campaign.id))
    
    if is_active is not None:
        query = query.where(Campaign.is_active == is_active)
        count_query = count_query.where(Campaign.is_active == is_active)
    
    query = query.order_by(Campaign.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    campaigns = result.scalars().all()
    
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0
    
    return campaigns, total


async def get_campaign(db: AsyncSession, campaign_id: int) -> Optional[Campaign]:
    """Get a single campaign by ID."""
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    return result.scalar_one_or_none()


async def create_campaign(db: AsyncSession, campaign_data: CampaignCreate) -> Campaign:
    """Create a new campaign."""
    campaign = Campaign(**campaign_data.model_dump())
    db.add(campaign)
    await db.flush()
    await db.refresh(campaign)
    return campaign


async def update_campaign(
    db: AsyncSession, campaign_id: int, campaign_data: CampaignUpdate
) -> Optional[Campaign]:
    """Update an existing campaign."""
    campaign = await get_campaign(db, campaign_id)
    if not campaign:
        return None
    
    update_data = campaign_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(campaign, field, value)
    
    await db.flush()
    await db.refresh(campaign)
    return campaign
