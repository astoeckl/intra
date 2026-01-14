from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.schemas.contact_history import ContactHistoryResponse, NoteCreate, CallCreate
from src.schemas.base import PaginatedResponse
from src.services import history_service

router = APIRouter()


@router.get("/{contact_id}/history", response_model=PaginatedResponse)
async def get_contact_history(
    contact_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Get history/timeline for a contact."""
    skip = (page - 1) * page_size
    history, total = await history_service.get_contact_history(
        db, contact_id, skip=skip, limit=page_size
    )
    
    return PaginatedResponse(
        items=[ContactHistoryResponse.model_validate(h) for h in history],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.post("/{contact_id}/notes", response_model=ContactHistoryResponse, status_code=201)
async def add_note(
    contact_id: int,
    note_data: NoteCreate,
    db: AsyncSession = Depends(get_db),
):
    """Add a note to contact history."""
    # TODO: Get actual user from auth context
    current_user = "current_user"
    
    history = await history_service.add_note(db, contact_id, note_data, created_by=current_user)
    return ContactHistoryResponse.model_validate(history)


@router.post("/{contact_id}/calls", response_model=ContactHistoryResponse, status_code=201)
async def add_call(
    contact_id: int,
    call_data: CallCreate,
    db: AsyncSession = Depends(get_db),
):
    """Add a call documentation to contact history."""
    # TODO: Get actual user from auth context
    current_user = "current_user"
    
    history = await history_service.add_call(db, contact_id, call_data, created_by=current_user)
    return ContactHistoryResponse.model_validate(history)
