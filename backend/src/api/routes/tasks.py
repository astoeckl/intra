"""
Task API Routes.

Provides CRUD operations for tasks including completion workflow
with optional follow-up task creation.
"""

from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.models.task import TaskStatus, TaskPriority, Task
from src.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskComplete,
    TaskResponse,
    TaskListResponse,
)
from src.schemas.base import PaginatedResponse
from src.services import task_service

router = APIRouter()


def check_task_overdue(task: Task, now: datetime) -> bool:
    """Check if a task is overdue, handling both timezone-aware and naive datetimes."""
    if task.due_date is None:
        return False
    if task.status not in [TaskStatus.OPEN, TaskStatus.IN_PROGRESS]:
        return False

    due_date = task.due_date
    # Handle naive datetimes by assuming UTC
    if due_date.tzinfo is None:
        due_date = due_date.replace(tzinfo=timezone.utc)
    return due_date < now


@router.get("", response_model=PaginatedResponse)
async def list_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: TaskStatus = Query(None),
    priority: TaskPriority = Query(None),
    assigned_to: str = Query(None),
    contact_id: int = Query(None),
    is_overdue: bool = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """
    List tasks with pagination and filters.

    Args:
        page: Page number (1-indexed).
        page_size: Items per page (max 100).
        status: Filter by task status.
        priority: Filter by priority level.
        assigned_to: Filter by assigned user.
        contact_id: Filter by associated contact.
        is_overdue: Filter to only show overdue tasks (open/in_progress past due_date).

    Returns:
        Paginated list sorted by due_date (soonest first), then priority.
    """
    skip = (page - 1) * page_size
    tasks, total = await task_service.get_tasks(
        db,
        skip=skip,
        limit=page_size,
        status=status,
        priority=priority,
        assigned_to=assigned_to,
        contact_id=contact_id,
        is_overdue=is_overdue,
    )

    now = datetime.now(timezone.utc)
    items = []
    for task in tasks:
        item = TaskListResponse(
            id=task.id,
            title=task.title,
            status=task.status,
            priority=task.priority,
            due_date=task.due_date,
            assigned_to=task.assigned_to,
            contact_id=task.contact_id,
            contact_name=f"{task.contact.first_name} {task.contact.last_name}" if task.contact else None,
            is_overdue=check_task_overdue(task, now),
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
        items.append(item)

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/my")
async def list_my_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    List tasks assigned to the current user.

    Convenience endpoint that filters by the authenticated user.
    """
    # TODO: Get actual user from auth context
    current_user = "current_user"

    skip = (page - 1) * page_size
    tasks, total = await task_service.get_my_tasks(
        db, assigned_to=current_user, skip=skip, limit=page_size
    )

    now = datetime.now(timezone.utc)
    items = []
    for task in tasks:
        item = TaskListResponse(
            id=task.id,
            title=task.title,
            status=task.status,
            priority=task.priority,
            due_date=task.due_date,
            assigned_to=task.assigned_to,
            contact_id=task.contact_id,
            contact_name=f"{task.contact.first_name} {task.contact.last_name}" if task.contact else None,
            is_overdue=check_task_overdue(task, now),
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
        items.append(item)

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve a single task with full details.

    Returns:
        Task with contact relationship.

    Raises:
        HTTPException 404: Task does not exist.
    """
    task = await task_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse.model_validate(task)


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new task.

    If a contact is associated, a history entry is automatically created.

    Args:
        task_data: Task details. due_date cannot be in the past.

    Returns:
        Created task with contact relationship.
    """
    # TODO: Get actual user from auth context
    current_user = "current_user"
    task = await task_service.create_task(db, task_data, created_by=current_user)
    return TaskResponse.model_validate(task)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update an existing task.

    Raises:
        HTTPException 404: Task does not exist.
    """
    task = await task_service.update_task(db, task_id, task_data)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse.model_validate(task)


@router.post("/{task_id}/complete")
async def complete_task(
    task_id: int,
    complete_data: TaskComplete,
    db: AsyncSession = Depends(get_db),
):
    """
    Mark a task as completed with optional follow-up creation.

    Args:
        task_id: Task to complete.
        complete_data: Completion notes and optional follow-up task details.

    Returns:
        Completed task and optional newly created follow-up task.

    Raises:
        HTTPException 404: Task does not exist.
    """
    # TODO: Get actual user from auth context
    current_user = "current_user"

    result = await task_service.complete_task(db, task_id, complete_data, completed_by=current_user)
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")

    task, follow_up = result
    return {
        "task": TaskResponse.model_validate(task),
        "follow_up_task": TaskResponse.model_validate(follow_up) if follow_up else None,
    }


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Permanently delete a task.

    Raises:
        HTTPException 404: Task does not exist.
    """
    deleted = await task_service.delete_task(db, task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
