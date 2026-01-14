from typing import Optional, Sequence
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.contact import Contact
from src.models.company import Company
from src.schemas.contact import ContactCreate, ContactUpdate, ContactSearchResult


async def get_contacts(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    company_id: Optional[int] = None,
    is_active: Optional[bool] = None,
) -> tuple[Sequence[Contact], int]:
    """Get all contacts with pagination and filters."""
    query = select(Contact).options(selectinload(Contact.company))
    count_query = select(func.count(Contact.id))
    
    filters = []
    if search:
        search_filter = or_(
            Contact.first_name.ilike(f"%{search}%"),
            Contact.last_name.ilike(f"%{search}%"),
            Contact.email.ilike(f"%{search}%"),
        )
        filters.append(search_filter)
    
    if company_id is not None:
        filters.append(Contact.company_id == company_id)
    
    if is_active is not None:
        filters.append(Contact.is_active == is_active)
    
    if filters:
        query = query.where(*filters)
        count_query = count_query.where(*filters)
    
    query = query.order_by(Contact.last_name, Contact.first_name).offset(skip).limit(limit)
    
    result = await db.execute(query)
    contacts = result.scalars().all()
    
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0
    
    return contacts, total


async def search_contacts(
    db: AsyncSession, query: str, limit: int = 10
) -> list[ContactSearchResult]:
    """Search contacts for autocomplete (<200ms target)."""
    if not query or len(query) < 2:
        return []
    
    search_query = (
        select(
            Contact.id,
            Contact.first_name,
            Contact.last_name,
            Contact.email,
            Contact.title,
            Company.name.label("company_name"),
        )
        .outerjoin(Company, Contact.company_id == Company.id)
        .where(
            or_(
                Contact.first_name.ilike(f"%{query}%"),
                Contact.last_name.ilike(f"%{query}%"),
                Contact.email.ilike(f"%{query}%"),
                Company.name.ilike(f"%{query}%"),
            )
        )
        .where(Contact.is_active == True)
        .order_by(Contact.last_name, Contact.first_name)
        .limit(limit)
    )
    
    result = await db.execute(search_query)
    rows = result.all()
    
    return [
        ContactSearchResult(
            id=row.id,
            full_name=f"{row.title + ' ' if row.title else ''}{row.first_name} {row.last_name}",
            email=row.email,
            company_name=row.company_name,
        )
        for row in rows
    ]


async def get_contact(db: AsyncSession, contact_id: int) -> Optional[Contact]:
    """Get a single contact by ID with company."""
    result = await db.execute(
        select(Contact)
        .options(selectinload(Contact.company))
        .where(Contact.id == contact_id)
    )
    return result.scalar_one_or_none()


async def create_contact(db: AsyncSession, contact_data: ContactCreate) -> Contact:
    """Create a new contact."""
    contact = Contact(**contact_data.model_dump())
    db.add(contact)
    await db.flush()
    await db.refresh(contact)
    return contact


async def update_contact(
    db: AsyncSession, contact_id: int, contact_data: ContactUpdate
) -> Optional[Contact]:
    """Update an existing contact."""
    contact = await get_contact(db, contact_id)
    if not contact:
        return None
    
    update_data = contact_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contact, field, value)
    
    await db.flush()
    await db.refresh(contact)
    return contact


async def delete_contact(db: AsyncSession, contact_id: int) -> bool:
    """Delete a contact (soft delete by setting is_active=False)."""
    contact = await get_contact(db, contact_id)
    if not contact:
        return False
    
    contact.is_active = False
    await db.flush()
    return True


async def get_or_create_contact_by_email(
    db: AsyncSession,
    email: str,
    first_name: str,
    last_name: str,
    company_id: Optional[int] = None,
    **kwargs,
) -> tuple[Contact, bool]:
    """Get existing contact by email or create new one."""
    result = await db.execute(
        select(Contact).where(Contact.email == email)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        return existing, False
    
    contact = Contact(
        email=email,
        first_name=first_name,
        last_name=last_name,
        company_id=company_id,
        **kwargs,
    )
    db.add(contact)
    await db.flush()
    await db.refresh(contact)
    return contact, True
