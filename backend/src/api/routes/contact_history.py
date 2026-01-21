"""
Contact History API Routes.

Provides endpoints for managing contact interaction history including
notes, calls, emails, and other timeline events.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.schemas.contact_history import (
    ContactHistoryResponse,
    ContactHistoryUpdate,
    NoteCreate,
    CallCreate,
)
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
    """
    Retrieve contact interaction timeline.

    Returns all history entries (notes, calls, emails, status changes)
    sorted by date descending (most recent first).

    Args:
        contact_id: Contact identifier.
        page: Page number (1-indexed).
        page_size: Items per page (default 50, max 100).

    Returns:
        Paginated list of history entries.
    """
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
    """
    Add a note to contact history.

    Args:
        contact_id: Contact identifier.
        note_data: Note content.

    Returns:
        Created history entry.
    """
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
    """
    Document a phone call in contact history.

    Args:
        contact_id: Contact identifier.
        call_data: Call details including duration and outcome.

    Returns:
        Created history entry with call metadata.
    """
    # TODO: Get actual user from auth context
    current_user = "current_user"

    history = await history_service.add_call(db, contact_id, call_data, created_by=current_user)
    return ContactHistoryResponse.model_validate(history)


@router.put("/history/{history_id}", response_model=ContactHistoryResponse)
async def update_history_entry(
    history_id: int,
    update_data: ContactHistoryUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update an existing history entry.

    Only title and content can be modified.

    Raises:
        HTTPException 404: History entry does not exist.
    """
    history = await history_service.update_history_entry(db, history_id, update_data)
    if not history:
        raise HTTPException(status_code=404, detail="History entry not found")
    return ContactHistoryResponse.model_validate(history)


@router.delete("/history/{history_id}", status_code=204)
async def delete_history_entry(
    history_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Permanently delete a history entry.

    Raises:
        HTTPException 404: History entry does not exist.
    """
    deleted = await history_service.delete_history_entry(db, history_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="History entry not found")
