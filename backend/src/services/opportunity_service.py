from typing import Optional, Sequence
from datetime import date
from sqlalchemy import select, func, and_, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.opportunity import Opportunity, OpportunityStage, STAGE_DEFAULT_PROBABILITY
from src.models.lead import Lead, LeadStatus
from src.models.contact import Contact
from src.models.company import Company
from src.models.contact_history import ContactHistory, HistoryType
from src.schemas.opportunity import (
    OpportunityCreate,
    OpportunityUpdate,
    OpportunityCreateFromLead,
    OpportunityClose,
    PipelineStageStats,
    PipelineStats,
)


async def get_opportunities(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    stage: Optional[OpportunityStage] = None,
    company_id: Optional[int] = None,
    contact_id: Optional[int] = None,
) -> tuple[Sequence[Opportunity], int]:
    query = (
        select(Opportunity)
        .options(
            selectinload(Opportunity.company),
            selectinload(Opportunity.contact),
        )
    )
    count_query = select(func.count(Opportunity.id))
    
    filters = []
    if stage:
        filters.append(Opportunity.stage == stage)
    if company_id:
        filters.append(Opportunity.company_id == company_id)
    if contact_id:
        filters.append(Opportunity.contact_id == contact_id)
    
    if filters:
        query = query.where(*filters)
        count_query = count_query.where(*filters)
    
    query = query.order_by(Opportunity.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    opportunities = result.scalars().all()
    
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0
    
    return opportunities, total


async def get_opportunity(db: AsyncSession, opportunity_id: int) -> Optional[Opportunity]:
    result = await db.execute(
        select(Opportunity)
        .options(
            selectinload(Opportunity.company),
            selectinload(Opportunity.contact),
            selectinload(Opportunity.lead),
        )
        .where(Opportunity.id == opportunity_id)
    )
    return result.scalar_one_or_none()


async def create_opportunity(db: AsyncSession, data: OpportunityCreate) -> Opportunity:
    opportunity = Opportunity(
        name=data.name,
        stage=data.stage,
        expected_value=data.expected_value,
        probability=data.probability,
        expected_close_date=data.expected_close_date,
        notes=data.notes,
        company_id=data.company_id,
        contact_id=data.contact_id,
    )
    db.add(opportunity)
    await db.flush()
    
    if data.contact_id:
        history = ContactHistory(
            contact_id=data.contact_id,
            type=HistoryType.NOTE,
            title="Opportunity erstellt",
            content=f"Neue Opportunity: {data.name}",
        )
        db.add(history)
    
    await db.refresh(opportunity)
    return opportunity


async def update_opportunity(
    db: AsyncSession, opportunity_id: int, data: OpportunityUpdate
) -> Optional[Opportunity]:
    opportunity = await get_opportunity(db, opportunity_id)
    if not opportunity:
        return None
    
    old_stage = opportunity.stage
    update_data = data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(opportunity, field, value)
    
    if "stage" in update_data and old_stage != opportunity.stage:
        if data.probability is None:
            opportunity.probability = STAGE_DEFAULT_PROBABILITY.get(
                opportunity.stage, opportunity.probability
            )
        
        if opportunity.contact_id:
            history = ContactHistory(
                contact_id=opportunity.contact_id,
                type=HistoryType.STATUS_CHANGE,
                title="Opportunity-Stage geaendert",
                content=f"Stage von '{old_stage.value}' zu '{opportunity.stage.value}' geaendert",
            )
            db.add(history)
    
    await db.flush()
    await db.refresh(opportunity)
    return opportunity


async def delete_opportunity(db: AsyncSession, opportunity_id: int) -> bool:
    opportunity = await get_opportunity(db, opportunity_id)
    if not opportunity:
        return False
    
    await db.delete(opportunity)
    await db.flush()
    return True


async def convert_lead_to_opportunity(
    db: AsyncSession, lead_id: int, data: OpportunityCreateFromLead
) -> Optional[Opportunity]:
    result = await db.execute(
        select(Lead)
        .options(
            selectinload(Lead.contact).selectinload(Contact.company),
        )
        .where(Lead.id == lead_id)
    )
    lead = result.scalar_one_or_none()
    
    if not lead:
        return None
    
    if lead.status != LeadStatus.QUALIFIED:
        return None
    
    existing = await db.execute(
        select(Opportunity).where(Opportunity.lead_id == lead_id)
    )
    if existing.scalar_one_or_none():
        return None
    
    opportunity = Opportunity(
        name=data.name,
        stage=OpportunityStage.QUALIFICATION,
        expected_value=data.expected_value,
        probability=STAGE_DEFAULT_PROBABILITY[OpportunityStage.QUALIFICATION],
        expected_close_date=data.expected_close_date,
        notes=data.notes,
        company_id=lead.contact.company_id if lead.contact else None,
        contact_id=lead.contact_id,
        lead_id=lead.id,
    )
    db.add(opportunity)
    
    lead.status = LeadStatus.CONVERTED
    
    if lead.contact_id:
        history = ContactHistory(
            contact_id=lead.contact_id,
            type=HistoryType.NOTE,
            title="Lead zu Opportunity konvertiert",
            content=f"Lead wurde zu Opportunity '{data.name}' konvertiert",
        )
        db.add(history)
    
    await db.flush()
    await db.refresh(opportunity)
    return opportunity


async def close_opportunity(
    db: AsyncSession, opportunity_id: int, data: OpportunityClose
) -> Optional[Opportunity]:
    opportunity = await get_opportunity(db, opportunity_id)
    if not opportunity:
        return None
    
    if opportunity.is_closed:
        return None
    
    opportunity.stage = OpportunityStage.CLOSED_WON if data.won else OpportunityStage.CLOSED_LOST
    opportunity.probability = 100 if data.won else 0
    opportunity.actual_close_date = date.today()
    opportunity.close_reason = data.close_reason
    
    if data.actual_value is not None:
        opportunity.expected_value = data.actual_value
    
    if opportunity.contact_id:
        status_text = "gewonnen" if data.won else "verloren"
        history = ContactHistory(
            contact_id=opportunity.contact_id,
            type=HistoryType.STATUS_CHANGE,
            title=f"Opportunity {status_text}",
            content=f"Opportunity '{opportunity.name}' wurde {status_text}. Grund: {data.close_reason or 'Nicht angegeben'}",
        )
        db.add(history)
    
    await db.flush()
    await db.refresh(opportunity)
    return opportunity


async def get_pipeline_stats(db: AsyncSession) -> PipelineStats:
    result = await db.execute(
        select(
            Opportunity.stage,
            func.count(Opportunity.id).label('count'),
            func.coalesce(func.sum(Opportunity.expected_value), 0).label('total_value'),
        )
        .group_by(Opportunity.stage)
    )
    rows = result.all()
    
    stages = []
    total_opportunities = 0
    total_value = 0.0
    weighted_value = 0.0
    
    for row in rows:
        stage_stat = PipelineStageStats(
            stage=row.stage,
            count=row.count,
            total_value=float(row.total_value),
            weighted_value=float(row.total_value) * (STAGE_DEFAULT_PROBABILITY.get(row.stage, 50) / 100),
        )
        stages.append(stage_stat)
        total_opportunities += row.count
        total_value += float(row.total_value)
        weighted_value += stage_stat.weighted_value
    
    won_count = await db.execute(
        select(func.count(Opportunity.id))
        .where(Opportunity.stage == OpportunityStage.CLOSED_WON)
    )
    won = won_count.scalar() or 0
    
    closed_count = await db.execute(
        select(func.count(Opportunity.id))
        .where(Opportunity.stage.in_([OpportunityStage.CLOSED_WON, OpportunityStage.CLOSED_LOST]))
    )
    total_closed = closed_count.scalar() or 0
    
    win_rate = (won / total_closed * 100) if total_closed > 0 else 0.0
    
    open_stages = [s for s in OpportunityStage if s not in (OpportunityStage.CLOSED_WON, OpportunityStage.CLOSED_LOST)]
    avg_result = await db.execute(
        select(func.avg(Opportunity.expected_value))
        .where(Opportunity.stage.in_(open_stages))
    )
    average_deal_size = float(avg_result.scalar() or 0)
    
    return PipelineStats(
        total_opportunities=total_opportunities,
        total_value=total_value,
        weighted_value=weighted_value,
        stages=stages,
        win_rate=win_rate,
        average_deal_size=average_deal_size,
    )
