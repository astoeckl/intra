from typing import Optional, Sequence
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.company import Company
from src.schemas.company import CompanyCreate, CompanyUpdate


async def get_companies(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
) -> tuple[Sequence[Company], int]:
    """Get all companies with pagination and optional search."""
    query = select(Company)
    count_query = select(func.count(Company.id))
    
    if search:
        search_filter = Company.name.ilike(f"%{search}%")
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)
    
    query = query.order_by(Company.name).offset(skip).limit(limit)
    
    result = await db.execute(query)
    companies = result.scalars().all()
    
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0
    
    return companies, total


async def get_company(db: AsyncSession, company_id: int) -> Optional[Company]:
    """Get a single company by ID."""
    result = await db.execute(select(Company).where(Company.id == company_id))
    return result.scalar_one_or_none()


async def get_company_by_name(db: AsyncSession, name: str) -> Optional[Company]:
    """Get a company by exact name."""
    result = await db.execute(select(Company).where(Company.name == name))
    return result.scalar_one_or_none()


async def create_company(db: AsyncSession, company_data: CompanyCreate) -> Company:
    """Create a new company."""
    company = Company(**company_data.model_dump())
    db.add(company)
    await db.flush()
    await db.refresh(company)
    return company


async def update_company(
    db: AsyncSession, company_id: int, company_data: CompanyUpdate
) -> Optional[Company]:
    """Update an existing company."""
    company = await get_company(db, company_id)
    if not company:
        return None
    
    update_data = company_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(company, field, value)
    
    await db.flush()
    await db.refresh(company)
    return company


async def delete_company(db: AsyncSession, company_id: int) -> bool:
    """Delete a company."""
    company = await get_company(db, company_id)
    if not company:
        return False
    
    await db.delete(company)
    return True
