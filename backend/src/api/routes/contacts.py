from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.schemas.contact import (
    ContactCreate,
    ContactUpdate,
    ContactResponse,
    ContactListResponse,
    ContactSearchResult,
    LeadSummary,
)
from src.schemas.base import PaginatedResponse
from src.services import contact_service

router = APIRouter()


@router.get("", response_model=PaginatedResponse)
async def list_contacts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str = Query(None),
    company_id: int = Query(None),
    is_active: bool = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Get all contacts with pagination and filters."""
    skip = (page - 1) * page_size
    contacts, total = await contact_service.get_contacts(
        db,
        skip=skip,
        limit=page_size,
        search=search,
        company_id=company_id,
        is_active=is_active,
    )
    
    items = []
    for contact in contacts:
        item = ContactListResponse(
            id=contact.id,
            first_name=contact.first_name,
            last_name=contact.last_name,
            email=contact.email,
            phone=contact.phone,
            position=contact.position,
            company_id=contact.company_id,
            company_name=contact.company.name if contact.company else None,
            is_active=contact.is_active,
            created_at=contact.created_at,
            updated_at=contact.updated_at,
        )
        items.append(item)
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/search", response_model=list[ContactSearchResult])
async def search_contacts(
    q: str = Query(..., min_length=2),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Search contacts for autocomplete. Target: <200ms response time."""
    return await contact_service.search_contacts(db, q, limit)


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a single contact by ID."""
    contact = await contact_service.get_contact(db, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    leads = [
        LeadSummary(id=lead.id, status=lead.status, source=lead.source)
        for lead in contact.leads
    ]
    
    return ContactResponse(
        id=contact.id,
        first_name=contact.first_name,
        last_name=contact.last_name,
        email=contact.email,
        phone=contact.phone,
        mobile=contact.mobile,
        position=contact.position,
        department=contact.department,
        salutation=contact.salutation,
        title=contact.title,
        notes=contact.notes,
        is_primary=contact.is_primary,
        is_active=contact.is_active,
        company_id=contact.company_id,
        company=contact.company,
        full_name=contact.full_name,
        leads=leads,
        created_at=contact.created_at,
        updated_at=contact.updated_at,
    )


@router.post("", response_model=ContactResponse, status_code=201)
async def create_contact(
    contact_data: ContactCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new contact."""
    contact = await contact_service.create_contact(db, contact_data)
    await db.refresh(contact, ["company"])
    
    return ContactResponse(
        id=contact.id,
        first_name=contact.first_name,
        last_name=contact.last_name,
        email=contact.email,
        phone=contact.phone,
        mobile=contact.mobile,
        position=contact.position,
        department=contact.department,
        salutation=contact.salutation,
        title=contact.title,
        notes=contact.notes,
        is_primary=contact.is_primary,
        is_active=contact.is_active,
        company_id=contact.company_id,
        company=contact.company,
        full_name=contact.full_name,
        created_at=contact.created_at,
        updated_at=contact.updated_at,
    )


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    contact_data: ContactUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing contact."""
    contact = await contact_service.update_contact(db, contact_id, contact_data)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    return ContactResponse(
        id=contact.id,
        first_name=contact.first_name,
        last_name=contact.last_name,
        email=contact.email,
        phone=contact.phone,
        mobile=contact.mobile,
        position=contact.position,
        department=contact.department,
        salutation=contact.salutation,
        title=contact.title,
        notes=contact.notes,
        is_primary=contact.is_primary,
        is_active=contact.is_active,
        company_id=contact.company_id,
        company=contact.company,
        full_name=contact.full_name,
        created_at=contact.created_at,
        updated_at=contact.updated_at,
    )


@router.delete("/{contact_id}", status_code=204)
async def delete_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Soft delete a contact (set is_active=False)."""
    deleted = await contact_service.delete_contact(db, contact_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Contact not found")
