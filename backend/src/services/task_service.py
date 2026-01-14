from typing import Optional, Sequence
from datetime import datetime, timezone
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.task import Task, TaskStatus, TaskPriority
from src.models.contact import Contact
from src.models.contact_history import ContactHistory, HistoryType
from src.schemas.task import TaskCreate, TaskUpdate, TaskComplete


async def get_tasks(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    status: Optional[TaskStatus] = None,
    assigned_to: Optional[str] = None,
    contact_id: Optional[int] = None,
    is_overdue: Optional[bool] = None,
) -> tuple[Sequence[Task], int]:
    """Get all tasks with pagination and filters."""
    query = select(Task).options(selectinload(Task.contact))
    count_query = select(func.count(Task.id))
    
    filters = []
    if status:
        filters.append(Task.status == status)
    if assigned_to:
        filters.append(Task.assigned_to == assigned_to)
    if contact_id:
        filters.append(Task.contact_id == contact_id)
    if is_overdue:
        now = datetime.now(timezone.utc)
        filters.append(and_(
            Task.due_date < now,
            Task.status.in_([TaskStatus.OPEN, TaskStatus.IN_PROGRESS])
        ))
    
    if filters:
        query = query.where(*filters)
        count_query = count_query.where(*filters)
    
    query = query.order_by(Task.due_date.asc().nullslast(), Task.priority.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0
    
    return tasks, total


async def get_my_tasks(
    db: AsyncSession,
    assigned_to: str,
    skip: int = 0,
    limit: int = 20,
) -> tuple[Sequence[Task], int]:
    """Get tasks assigned to a specific user."""
    return await get_tasks(db, skip=skip, limit=limit, assigned_to=assigned_to)


async def get_task(db: AsyncSession, task_id: int) -> Optional[Task]:
    """Get a single task by ID."""
    result = await db.execute(
        select(Task)
        .options(selectinload(Task.contact))
        .where(Task.id == task_id)
    )
    return result.scalar_one_or_none()


async def create_task(
    db: AsyncSession,
    task_data: TaskCreate,
    created_by: Optional[str] = None,
) -> Task:
    """Create a new task."""
    task = Task(**task_data.model_dump(), created_by=created_by)
    db.add(task)
    await db.flush()
    
    # Create history entry if contact is associated
    if task.contact_id:
        history = ContactHistory(
            contact_id=task.contact_id,
            type=HistoryType.TASK_CREATED,
            title="Aufgabe erstellt",
            content=f"Aufgabe: {task.title}",
            created_by=created_by,
        )
        db.add(history)
    
    await db.refresh(task)
    return task


async def update_task(
    db: AsyncSession,
    task_id: int,
    task_data: TaskUpdate,
) -> Optional[Task]:
    """Update an existing task."""
    task = await get_task(db, task_id)
    if not task:
        return None
    
    update_data = task_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    await db.flush()
    await db.refresh(task)
    return task


async def complete_task(
    db: AsyncSession,
    task_id: int,
    complete_data: TaskComplete,
    completed_by: Optional[str] = None,
) -> Optional[tuple[Task, Optional[Task]]]:
    """Complete a task with optional follow-up task."""
    task = await get_task(db, task_id)
    if not task:
        return None
    
    # Mark task as completed
    task.status = TaskStatus.COMPLETED
    task.completed_at = datetime.now(timezone.utc)
    
    # Add completion notes to task description
    if complete_data.notes:
        if task.description:
            task.description += f"\n\nAbschlussnotiz: {complete_data.notes}"
        else:
            task.description = f"Abschlussnotiz: {complete_data.notes}"
    
    follow_up_task = None
    
    # Create follow-up task if requested
    if complete_data.create_follow_up and complete_data.follow_up_title:
        follow_up_task = Task(
            title=complete_data.follow_up_title,
            due_date=complete_data.follow_up_due_date,
            priority=complete_data.follow_up_priority,
            contact_id=task.contact_id,
            assigned_to=task.assigned_to,
            created_by=completed_by,
            parent_task_id=task.id,
            status=TaskStatus.OPEN,
        )
        db.add(follow_up_task)
    
    await db.flush()
    await db.refresh(task)
    if follow_up_task:
        await db.refresh(follow_up_task)
    
    return task, follow_up_task


async def delete_task(db: AsyncSession, task_id: int) -> bool:
    """Delete a task."""
    task = await get_task(db, task_id)
    if not task:
        return False
    
    await db.delete(task)
    return True
