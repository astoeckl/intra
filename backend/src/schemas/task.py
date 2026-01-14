from typing import Optional
from datetime import datetime
from pydantic import Field

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
