from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.models.lead import LeadStatus
from src.schemas.lead import (
    LeadCreate,
    LeadCreateFromForm,
    LeadUpdate,
    LeadResponse,
    LeadListResponse,
    LeadImportResult,
)
from src.schemas.base import PaginatedResponse
from src.services import lead_service

router = APIRouter()


@router.get("", response_model=PaginatedResponse)
async def list_leads(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: LeadStatus = Query(None),
    campaign_id: int = Query(None),
    db: AsyncSession = Depends(get_db),
):
    skip = (page - 1) * page_size
    leads, total = await lead_service.get_leads(
        db, skip=skip, limit=page_size, status=status, campaign_id=campaign_id
    )
    
    items = []
    for lead in leads:
        contact = lead.contact
        contact_name = f"{contact.first_name} {contact.last_name}" if contact else "N/A"
        company_name = contact.company.name if contact and contact.company else None
        
        item = LeadListResponse(
            id=lead.id,
            status=lead.status,
            source=lead.source,
            contact_id=lead.contact_id,
            contact_name=contact_name,
            contact_email=contact.email if contact else None,
            contact_phone=contact.phone if contact else None,
            contact_mobile=contact.mobile if contact else None,
            contact_position=contact.position if contact else None,
            company_name=company_name,
            campaign_id=lead.campaign_id,
            campaign_name=lead.campaign.name if lead.campaign else None,
            created_at=lead.created_at,
            updated_at=lead.updated_at,
        )
        items.append(item)
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
):
    lead = await lead_service.get_lead(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return LeadResponse.model_validate(lead)


@router.post("", response_model=LeadResponse, status_code=201)
async def create_lead(
    lead_data: LeadCreate,
    db: AsyncSession = Depends(get_db),
):
    lead = await lead_service.create_lead(db, lead_data)
    return LeadResponse.model_validate(lead)


@router.put("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: int,
    lead_data: LeadUpdate,
    db: AsyncSession = Depends(get_db),
):
    lead = await lead_service.update_lead(db, lead_id, lead_data)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return LeadResponse.model_validate(lead)


@router.post("/import", response_model=LeadImportResult)
async def import_leads(
    file: UploadFile = File(...),
    campaign_id: int = Query(None),
    db: AsyncSession = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    content = await file.read()
    result = await lead_service.import_leads_from_file(
        db, content, file.filename, campaign_id
    )
    return result
