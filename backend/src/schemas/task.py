from typing import Optional
from datetime import datetime, timezone
from pydantic import Field, field_validator

from src.schemas.base import BaseSchema, TimestampSchema
from src.schemas.contact import ContactListResponse
from src.models.task import TaskStatus, TaskPriority


class TaskBase(BaseSchema):
    """Base task schema."""
    
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.OPEN
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None


class TaskCreate(TaskBase):
    """Schema for creating a task."""
    
    contact_id: Optional[int] = None
    assigned_to: Optional[str] = None
    parent_task_id: Optional[int] = None
    
    @field_validator('due_date')
    @classmethod
    def due_date_not_in_past(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Validate that due_date is not in the past."""
        if v is not None:
            now = datetime.now(timezone.utc)
            # Compare only dates, not times (allow today)
            if v.date() < now.date():
                raise ValueError('Fälligkeitsdatum darf nicht in der Vergangenheit liegen')
        return v


class TaskUpdate(BaseSchema):
    """Schema for updating a task."""
    
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    assigned_to: Optional[str] = None
    contact_id: Optional[int] = None


class TaskComplete(BaseSchema):
    """Schema for completing a task with optional follow-up."""
    
    notes: Optional[str] = None
    create_follow_up: bool = False
    follow_up_title: Optional[str] = None
    follow_up_due_date: Optional[datetime] = None
    follow_up_priority: TaskPriority = TaskPriority.MEDIUM
    
    @field_validator('follow_up_due_date')
    @classmethod
    def follow_up_due_date_not_in_past(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Validate that follow_up_due_date is not in the past."""
        if v is not None:
            now = datetime.now(timezone.utc)
            if v.date() < now.date():
                raise ValueError('Fälligkeitsdatum darf nicht in der Vergangenheit liegen')
        return v


class TaskResponse(TaskBase, TimestampSchema):
    """Schema for task response."""
    
    id: int
    contact_id: Optional[int] = None
    assigned_to: Optional[str] = None
    created_by: Optional[str] = None
    completed_at: Optional[datetime] = None
    parent_task_id: Optional[int] = None
    contact: Optional[ContactListResponse] = None


class TaskListResponse(TimestampSchema):
    """Schema for task list item."""
    
    id: int
    title: str
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[datetime] = None
    assigned_to: Optional[str] = None
    contact_id: Optional[int] = None
    contact_name: Optional[str] = None
    is_overdue: bool = False
