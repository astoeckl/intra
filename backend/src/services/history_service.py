from typing import Optional, Sequence
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.contact_history import ContactHistory, HistoryType
from src.schemas.contact_history import NoteCreate, CallCreate, ContactHistoryUpdate


async def get_contact_history(
    db: AsyncSession,
    contact_id: int,
    skip: int = 0,
    limit: int = 50,
) -> tuple[Sequence[ContactHistory], int]:
    """Get history entries for a contact."""
    query = (
        select(ContactHistory)
        .where(ContactHistory.contact_id == contact_id)
        .order_by(ContactHistory.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    
    count_query = select(func.count(ContactHistory.id)).where(
        ContactHistory.contact_id == contact_id
    )
    
    result = await db.execute(query)
    history = result.scalars().all()
    
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0
    
    return history, total


async def add_note(
    db: AsyncSession,
    contact_id: int,
    note_data: NoteCreate,
    created_by: Optional[str] = None,
) -> ContactHistory:
    """Add a note to contact history."""
    history = ContactHistory(
        contact_id=contact_id,
        type=HistoryType.NOTE,
        title="Notiz hinzugefügt",
        content=note_data.content,
        created_by=created_by,
    )
    db.add(history)
    await db.flush()
    await db.refresh(history)
    return history


async def add_call(
    db: AsyncSession,
    contact_id: int,
    call_data: CallCreate,
    created_by: Optional[str] = None,
) -> ContactHistory:
    """Add a call documentation to contact history."""
    import json
    
    extra_data = json.dumps({
        "duration_minutes": call_data.duration_minutes,
        "outcome": call_data.outcome,
    })
    
    history = ContactHistory(
        contact_id=contact_id,
        type=HistoryType.CALL,
        title="Anruf dokumentiert",
        content=call_data.content,
        extra_data=extra_data,
        created_by=created_by,
    )
    db.add(history)
    await db.flush()
    await db.refresh(history)
    return history


async def add_email_sent(
    db: AsyncSession,
    contact_id: int,
    subject: str,
    template_name: str,
    created_by: Optional[str] = None,
) -> ContactHistory:
    """Add email sent entry to contact history."""
    history = ContactHistory(
        contact_id=contact_id,
        type=HistoryType.EMAIL,
        title=f"E-Mail gesendet: {subject}",
        content=f"Vorlage: {template_name}",
        created_by=created_by,
    )
    db.add(history)
    await db.flush()
    await db.refresh(history)
    return history


async def get_history_entry(
    db: AsyncSession,
    history_id: int,
) -> Optional[ContactHistory]:
    """Get a single history entry by ID."""
    query = select(ContactHistory).where(ContactHistory.id == history_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def update_history_entry(
    db: AsyncSession,
    history_id: int,
    update_data: ContactHistoryUpdate,
) -> Optional[ContactHistory]:
    """Update a history entry."""
    history = await get_history_entry(db, history_id)
    if not history:
        return None
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(history, field, value)
    
    await db.flush()
    await db.refresh(history)
    return history


async def delete_history_entry(
    db: AsyncSession,
    history_id: int,
) -> bool:
    """Delete a history entry."""
    history = await get_history_entry(db, history_id)
    if not history:
        return False
    
    await db.delete(history)
    await db.flush()
    return True
