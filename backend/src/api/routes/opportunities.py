from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.models.opportunity import OpportunityStage
from src.schemas.opportunity import (
    OpportunityCreate,
    OpportunityCreateFromLead,
    OpportunityUpdate,
    OpportunityClose,
    OpportunityResponse,
    OpportunityListResponse,
    PipelineStats,
)
from src.schemas.base import PaginatedResponse
from src.services import opportunity_service

router = APIRouter()


@router.get("", response_model=PaginatedResponse)
async def list_opportunities(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    stage: OpportunityStage = Query(None),
    company_id: int = Query(None),
    contact_id: int = Query(None),
    db: AsyncSession = Depends(get_db),
):
    skip = (page - 1) * page_size
    opportunities, total = await opportunity_service.get_opportunities(
        db, skip=skip, limit=page_size, stage=stage, company_id=company_id, contact_id=contact_id
    )
    
    items = []
    for opp in opportunities:
        company_name = opp.company.name if opp.company else None
        contact_name = f"{opp.contact.first_name} {opp.contact.last_name}" if opp.contact else None
        
        item = OpportunityListResponse(
            id=opp.id,
            name=opp.name,
            stage=opp.stage,
            expected_value=float(opp.expected_value) if opp.expected_value else None,
            probability=opp.probability,
            expected_close_date=opp.expected_close_date,
            actual_close_date=opp.actual_close_date,
            company_id=opp.company_id,
            company_name=company_name,
            contact_id=opp.contact_id,
            contact_name=contact_name,
            created_at=opp.created_at,
            updated_at=opp.updated_at,
        )
        items.append(item)
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/stats", response_model=PipelineStats)
async def get_pipeline_stats(
    db: AsyncSession = Depends(get_db),
):
    return await opportunity_service.get_pipeline_stats(db)


@router.get("/{opportunity_id}", response_model=OpportunityResponse)
async def get_opportunity(
    opportunity_id: int,
    db: AsyncSession = Depends(get_db),
):
    opp = await opportunity_service.get_opportunity(db, opportunity_id)
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    return OpportunityResponse(
        id=opp.id,
        name=opp.name,
        stage=opp.stage,
        expected_value=float(opp.expected_value) if opp.expected_value else None,
        probability=opp.probability,
        expected_close_date=opp.expected_close_date,
        actual_close_date=opp.actual_close_date,
        close_reason=opp.close_reason,
        notes=opp.notes,
        company_id=opp.company_id,
        contact_id=opp.contact_id,
        lead_id=opp.lead_id,
        company_name=opp.company.name if opp.company else None,
        contact_name=f"{opp.contact.first_name} {opp.contact.last_name}" if opp.contact else None,
        created_at=opp.created_at,
        updated_at=opp.updated_at,
    )


@router.post("", response_model=OpportunityResponse, status_code=201)
async def create_opportunity(
    data: OpportunityCreate,
    db: AsyncSession = Depends(get_db),
):
    opp = await opportunity_service.create_opportunity(db, data)
    return OpportunityResponse(
        id=opp.id,
        name=opp.name,
        stage=opp.stage,
        expected_value=float(opp.expected_value) if opp.expected_value else None,
        probability=opp.probability,
        expected_close_date=opp.expected_close_date,
        actual_close_date=opp.actual_close_date,
        close_reason=opp.close_reason,
        notes=opp.notes,
        company_id=opp.company_id,
        contact_id=opp.contact_id,
        lead_id=opp.lead_id,
        company_name=opp.company.name if opp.company else None,
        contact_name=f"{opp.contact.first_name} {opp.contact.last_name}" if opp.contact else None,
        created_at=opp.created_at,
        updated_at=opp.updated_at,
    )


@router.put("/{opportunity_id}", response_model=OpportunityResponse)
async def update_opportunity(
    opportunity_id: int,
    data: OpportunityUpdate,
    db: AsyncSession = Depends(get_db),
):
    opp = await opportunity_service.update_opportunity(db, opportunity_id, data)
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    return OpportunityResponse(
        id=opp.id,
        name=opp.name,
        stage=opp.stage,
        expected_value=float(opp.expected_value) if opp.expected_value else None,
        probability=opp.probability,
        expected_close_date=opp.expected_close_date,
        actual_close_date=opp.actual_close_date,
        close_reason=opp.close_reason,
        notes=opp.notes,
        company_id=opp.company_id,
        contact_id=opp.contact_id,
        lead_id=opp.lead_id,
        company_name=opp.company.name if opp.company else None,
        contact_name=f"{opp.contact.first_name} {opp.contact.last_name}" if opp.contact else None,
        created_at=opp.created_at,
        updated_at=opp.updated_at,
    )


@router.delete("/{opportunity_id}", status_code=204)
async def delete_opportunity(
    opportunity_id: int,
    db: AsyncSession = Depends(get_db),
):
    deleted = await opportunity_service.delete_opportunity(db, opportunity_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Opportunity not found")


@router.post("/convert/{lead_id}", response_model=OpportunityResponse, status_code=201)
async def convert_lead_to_opportunity(
    lead_id: int,
    data: OpportunityCreateFromLead,
    db: AsyncSession = Depends(get_db),
):
    opp = await opportunity_service.convert_lead_to_opportunity(db, lead_id, data)
    if not opp:
        raise HTTPException(
            status_code=400,
            detail="Lead not found, not qualified, or already converted"
        )
    
    return OpportunityResponse(
        id=opp.id,
        name=opp.name,
        stage=opp.stage,
        expected_value=float(opp.expected_value) if opp.expected_value else None,
        probability=opp.probability,
        expected_close_date=opp.expected_close_date,
        actual_close_date=opp.actual_close_date,
        close_reason=opp.close_reason,
        notes=opp.notes,
        company_id=opp.company_id,
        contact_id=opp.contact_id,
        lead_id=opp.lead_id,
        company_name=opp.company.name if opp.company else None,
        contact_name=f"{opp.contact.first_name} {opp.contact.last_name}" if opp.contact else None,
        created_at=opp.created_at,
        updated_at=opp.updated_at,
    )


@router.post("/{opportunity_id}/close", response_model=OpportunityResponse)
async def close_opportunity(
    opportunity_id: int,
    data: OpportunityClose,
    db: AsyncSession = Depends(get_db),
):
    opp = await opportunity_service.close_opportunity(db, opportunity_id, data)
    if not opp:
        raise HTTPException(
            status_code=400,
            detail="Opportunity not found or already closed"
        )
    
    return OpportunityResponse(
        id=opp.id,
        name=opp.name,
        stage=opp.stage,
        expected_value=float(opp.expected_value) if opp.expected_value else None,
        probability=opp.probability,
        expected_close_date=opp.expected_close_date,
        actual_close_date=opp.actual_close_date,
        close_reason=opp.close_reason,
        notes=opp.notes,
        company_id=opp.company_id,
        contact_id=opp.contact_id,
        lead_id=opp.lead_id,
        company_name=opp.company.name if opp.company else None,
        contact_name=f"{opp.contact.first_name} {opp.contact.last_name}" if opp.contact else None,
        created_at=opp.created_at,
        updated_at=opp.updated_at,
    )
