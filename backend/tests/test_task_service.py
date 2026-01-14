"""
Tests for Task Service.
"""
from datetime import datetime, timezone, timedelta

import pytest

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.contact import Contact
from src.models.task import Task, TaskStatus, TaskPriority
from src.models.contact_history import ContactHistory, HistoryType
from src.schemas.task import TaskCreate, TaskUpdate, TaskComplete
from src.services import task_service


class TestGetTasks:
    """Tests for get_tasks function."""

    @pytest.mark.asyncio
    async def test_get_tasks_empty(self, db_session: AsyncSession):
        """Test getting tasks when none exist."""
        tasks, total = await task_service.get_tasks(db_session)
        assert tasks == []
        assert total == 0

    @pytest.mark.asyncio
    async def test_get_tasks_with_data(
        self, db_session: AsyncSession, sample_task: Task
    ):
        """Test getting tasks with existing data."""
        tasks, total = await task_service.get_tasks(db_session)
        assert len(tasks) == 1
        assert total == 1
        assert tasks[0].id == sample_task.id

    @pytest.mark.asyncio
    async def test_get_tasks_pagination(
        self, db_session: AsyncSession, sample_contact: Contact
    ):
        """Test tasks pagination."""
        # Create multiple tasks
        for i in range(10):
            task = Task(
                title=f"Task {i}",
                status=TaskStatus.OPEN,
                priority=TaskPriority.MEDIUM,
                contact_id=sample_contact.id,
            )
            db_session.add(task)
        await db_session.flush()
        
        # Get first page (3 items)
        tasks, total = await task_service.get_tasks(db_session, skip=0, limit=3)
        assert len(tasks) == 3
        assert total == 10

        # Get second page
        tasks, total = await task_service.get_tasks(db_session, skip=3, limit=3)
        assert len(tasks) == 3
        assert total == 10

    @pytest.mark.asyncio
    async def test_get_tasks_filter_by_status(
        self, db_session: AsyncSession, sample_contact: Contact
    ):
        """Test filtering tasks by status."""
        # Create tasks with different statuses
        for status in [TaskStatus.OPEN, TaskStatus.IN_PROGRESS, TaskStatus.COMPLETED]:
            task = Task(
                title=f"Task {status.value}",
                status=status,
                priority=TaskPriority.MEDIUM,
                contact_id=sample_contact.id,
            )
            db_session.add(task)
        await db_session.flush()
        
        tasks, total = await task_service.get_tasks(
            db_session, status=TaskStatus.OPEN
        )
        assert total == 1
        assert tasks[0].status == TaskStatus.OPEN

    @pytest.mark.asyncio
    async def test_get_tasks_filter_by_assigned_to(
        self, db_session: AsyncSession, sample_contact: Contact
    ):
        """Test filtering tasks by assigned user."""
        # Create tasks with different assignees
        for user in ["user1", "user2", "user1"]:
            task = Task(
                title=f"Task for {user}",
                status=TaskStatus.OPEN,
                priority=TaskPriority.MEDIUM,
                assigned_to=user,
                contact_id=sample_contact.id,
            )
            db_session.add(task)
        await db_session.flush()
        
        tasks, total = await task_service.get_tasks(
            db_session, assigned_to="user1"
        )
        assert total == 2

    @pytest.mark.asyncio
    async def test_get_tasks_filter_by_contact(
        self, db_session: AsyncSession, sample_contact: Contact, sample_contact_no_company: Contact
    ):
        """Test filtering tasks by contact."""
        # Create tasks for different contacts
        task1 = Task(
            title="Task 1",
            status=TaskStatus.OPEN,
            priority=TaskPriority.MEDIUM,
            contact_id=sample_contact.id,
        )
        task2 = Task(
            title="Task 2",
            status=TaskStatus.OPEN,
            priority=TaskPriority.MEDIUM,
            contact_id=sample_contact_no_company.id,
        )
        db_session.add(task1)
        db_session.add(task2)
        await db_session.flush()
        
        tasks, total = await task_service.get_tasks(
            db_session, contact_id=sample_contact.id
        )
        assert total == 1
        assert tasks[0].contact_id == sample_contact.id

    @pytest.mark.asyncio
    async def test_get_tasks_filter_overdue(
        self, db_session: AsyncSession, sample_task: Task, sample_overdue_task: Task
    ):
        """Test filtering for overdue tasks."""
        tasks, total = await task_service.get_tasks(
            db_session, is_overdue=True
        )
        assert total == 1
        assert tasks[0].id == sample_overdue_task.id


class TestGetMyTasks:
    """Tests for get_my_tasks function."""

    @pytest.mark.asyncio
    async def test_get_my_tasks(
        self, db_session: AsyncSession, sample_contact: Contact
    ):
        """Test getting tasks for a specific user."""
        # Create tasks for different users
        for user in ["current_user", "other_user", "current_user"]:
            task = Task(
                title=f"Task for {user}",
                status=TaskStatus.OPEN,
                priority=TaskPriority.MEDIUM,
                assigned_to=user,
                contact_id=sample_contact.id,
            )
            db_session.add(task)
        await db_session.flush()
        
        tasks, total = await task_service.get_my_tasks(
            db_session, assigned_to="current_user"
        )
        assert total == 2


class TestGetTask:
    """Tests for get_task function."""

    @pytest.mark.asyncio
    async def test_get_task_exists(
        self, db_session: AsyncSession, sample_task: Task
    ):
        """Test getting an existing task."""
        task = await task_service.get_task(db_session, sample_task.id)
        assert task is not None
        assert task.id == sample_task.id
        assert task.contact is not None

    @pytest.mark.asyncio
    async def test_get_task_not_exists(self, db_session: AsyncSession):
        """Test getting a non-existent task."""
        task = await task_service.get_task(db_session, 99999)
        assert task is None


class TestCreateTask:
    """Tests for create_task function."""

    @pytest.mark.asyncio
    async def test_create_task_minimal(self, db_session: AsyncSession):
        """Test creating a task with minimal data."""
        task_data = TaskCreate(
            title="Neue Aufgabe",
        )
        task = await task_service.create_task(db_session, task_data)
        
        assert task.id is not None
        assert task.title == "Neue Aufgabe"
        assert task.status == TaskStatus.OPEN
        assert task.priority == TaskPriority.MEDIUM

    @pytest.mark.asyncio
    async def test_create_task_full(
        self, db_session: AsyncSession, sample_contact: Contact
    ):
        """Test creating a task with full data."""
        due_date = datetime.now(timezone.utc) + timedelta(days=7)
        task_data = TaskCreate(
            title="Vollständige Aufgabe",
            description="Beschreibung der Aufgabe",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.HIGH,
            due_date=due_date,
            contact_id=sample_contact.id,
            assigned_to="test_user",
        )
        task = await task_service.create_task(
            db_session, task_data, created_by="creator_user"
        )
        
        assert task.id is not None
        assert task.title == "Vollständige Aufgabe"
        assert task.description == "Beschreibung der Aufgabe"
        assert task.status == TaskStatus.IN_PROGRESS
        assert task.priority == TaskPriority.HIGH
        assert task.contact_id == sample_contact.id
        assert task.assigned_to == "test_user"
        assert task.created_by == "creator_user"

    @pytest.mark.asyncio
    async def test_create_task_creates_history_entry(
        self, db_session: AsyncSession, sample_contact: Contact
    ):
        """Test that creating a task creates a history entry."""
        task_data = TaskCreate(
            title="Aufgabe mit Historie",
            contact_id=sample_contact.id,
        )
        task = await task_service.create_task(
            db_session, task_data, created_by="test_user"
        )
        await db_session.commit()
        
        # Check history entry was created
        result = await db_session.execute(
            select(ContactHistory).where(
                ContactHistory.contact_id == sample_contact.id,
                ContactHistory.type == HistoryType.TASK_CREATED,
            )
        )
        history = result.scalar_one_or_none()
        assert history is not None
        assert "Aufgabe erstellt" in history.title


class TestUpdateTask:
    """Tests for update_task function."""

    @pytest.mark.asyncio
    async def test_update_task_success(
        self, db_session: AsyncSession, sample_task: Task
    ):
        """Test updating a task successfully."""
        update_data = TaskUpdate(
            title="Aktualisierter Titel",
            status=TaskStatus.IN_PROGRESS,
        )
        task = await task_service.update_task(db_session, sample_task.id, update_data)
        
        assert task is not None
        assert task.title == "Aktualisierter Titel"
        assert task.status == TaskStatus.IN_PROGRESS

    @pytest.mark.asyncio
    async def test_update_task_not_exists(self, db_session: AsyncSession):
        """Test updating a non-existent task."""
        update_data = TaskUpdate(title="Test")
        task = await task_service.update_task(db_session, 99999, update_data)
        assert task is None

    @pytest.mark.asyncio
    async def test_update_task_partial(
        self, db_session: AsyncSession, sample_task: Task
    ):
        """Test partial update (only specified fields)."""
        original_title = sample_task.title
        update_data = TaskUpdate(priority=TaskPriority.URGENT)
        
        task = await task_service.update_task(db_session, sample_task.id, update_data)
        
        assert task.title == original_title  # Unchanged
        assert task.priority == TaskPriority.URGENT


class TestCompleteTask:
    """Tests for complete_task function."""

    @pytest.mark.asyncio
    async def test_complete_task_simple(
        self, db_session: AsyncSession, sample_task: Task
    ):
        """Test completing a task without follow-up."""
        complete_data = TaskComplete(
            notes="Aufgabe erfolgreich abgeschlossen",
        )
        result = await task_service.complete_task(
            db_session, sample_task.id, complete_data, completed_by="test_user"
        )
        
        assert result is not None
        task, follow_up = result
        
        assert task.status == TaskStatus.COMPLETED
        assert task.completed_at is not None
        assert "Abschlussnotiz" in task.description
        assert follow_up is None

    @pytest.mark.asyncio
    async def test_complete_task_with_followup(
        self, db_session: AsyncSession, sample_task: Task
    ):
        """Test completing a task with follow-up task."""
        follow_up_due = datetime.now(timezone.utc) + timedelta(days=7)
        complete_data = TaskComplete(
            notes="Erstgespräch durchgeführt",
            create_follow_up=True,
            follow_up_title="Angebot nachfassen",
            follow_up_due_date=follow_up_due,
            follow_up_priority=TaskPriority.HIGH,
        )
        result = await task_service.complete_task(
            db_session, sample_task.id, complete_data, completed_by="test_user"
        )
        
        assert result is not None
        task, follow_up = result
        
        assert task.status == TaskStatus.COMPLETED
        assert follow_up is not None
        assert follow_up.title == "Angebot nachfassen"
        assert follow_up.priority == TaskPriority.HIGH
        assert follow_up.status == TaskStatus.OPEN
        assert follow_up.parent_task_id == task.id
        assert follow_up.contact_id == task.contact_id
        assert follow_up.assigned_to == task.assigned_to

    @pytest.mark.asyncio
    async def test_complete_task_not_exists(self, db_session: AsyncSession):
        """Test completing a non-existent task."""
        complete_data = TaskComplete()
        result = await task_service.complete_task(
            db_session, 99999, complete_data
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_complete_task_appends_notes_to_description(
        self, db_session: AsyncSession, sample_task: Task
    ):
        """Test that completion notes are appended to existing description."""
        original_description = sample_task.description
        
        complete_data = TaskComplete(notes="Zusätzliche Notiz")
        result = await task_service.complete_task(
            db_session, sample_task.id, complete_data
        )
        
        task, _ = result
        assert original_description in task.description
        assert "Zusätzliche Notiz" in task.description


class TestDeleteTask:
    """Tests for delete_task function."""

    @pytest.mark.asyncio
    async def test_delete_task_success(
        self, db_session: AsyncSession, sample_task: Task
    ):
        """Test deleting a task."""
        task_id = sample_task.id
        result = await task_service.delete_task(db_session, task_id)
        
        assert result is True
        
        # Flush to persist the deletion
        await db_session.flush()
        
        # Task should no longer exist
        task = await task_service.get_task(db_session, task_id)
        assert task is None

    @pytest.mark.asyncio
    async def test_delete_task_not_exists(self, db_session: AsyncSession):
        """Test deleting a non-existent task."""
        result = await task_service.delete_task(db_session, 99999)
        assert result is False


class TestTaskOrdering:
    """Tests for task ordering in queries."""

    @pytest.mark.asyncio
    async def test_tasks_ordered_by_due_date_and_priority(
        self, db_session: AsyncSession, sample_contact: Contact
    ):
        """Test that tasks are ordered by due_date (asc) and priority (desc)."""
        now = datetime.now(timezone.utc)
        
        # Create tasks with different due dates and priorities
        task1 = Task(
            title="Task Due Tomorrow High",
            due_date=now + timedelta(days=1),
            priority=TaskPriority.HIGH,
            status=TaskStatus.OPEN,
            contact_id=sample_contact.id,
        )
        task2 = Task(
            title="Task Due Today Low",
            due_date=now + timedelta(hours=1),
            priority=TaskPriority.LOW,
            status=TaskStatus.OPEN,
            contact_id=sample_contact.id,
        )
        task3 = Task(
            title="Task No Due Date Urgent",
            due_date=None,
            priority=TaskPriority.URGENT,
            status=TaskStatus.OPEN,
            contact_id=sample_contact.id,
        )
        
        db_session.add_all([task1, task2, task3])
        await db_session.flush()
        
        tasks, _ = await task_service.get_tasks(db_session)
        
        # Due today should come first (earliest due_date)
        assert tasks[0].title == "Task Due Today Low"
        # Due tomorrow should come second
        assert tasks[1].title == "Task Due Tomorrow High"
        # No due date should come last
        assert tasks[2].title == "Task No Due Date Urgent"
