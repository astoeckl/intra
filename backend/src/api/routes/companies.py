from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.schemas.company import (
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
    CompanyListResponse,
)
from src.schemas.base import PaginatedResponse
from src.services import company_service

router = APIRouter()


@router.get("", response_model=PaginatedResponse)
async def list_companies(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Get all companies with pagination."""
    skip = (page - 1) * page_size
    companies, total = await company_service.get_companies(
        db, skip=skip, limit=page_size, search=search
    )
    
    return PaginatedResponse(
        items=[CompanyListResponse.model_validate(c) for c in companies],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a single company by ID."""
    company = await company_service.get_company(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    response = CompanyResponse.model_validate(company)
    response.contacts_count = len(company.contacts) if company.contacts else 0
    return response


@router.post("", response_model=CompanyResponse, status_code=201)
async def create_company(
    company_data: CompanyCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new company."""
    # Check for duplicate name
    existing = await company_service.get_company_by_name(db, company_data.name)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Company with name '{company_data.name}' already exists",
        )
    
    company = await company_service.create_company(db, company_data)
    return CompanyResponse.model_validate(company)


@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: int,
    company_data: CompanyUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing company."""
    company = await company_service.update_company(db, company_id, company_data)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return CompanyResponse.model_validate(company)


@router.delete("/{company_id}", status_code=204)
async def delete_company(
    company_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a company."""
    deleted = await company_service.delete_company(db, company_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Company not found")
