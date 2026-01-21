"""Unit tests for task_service."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone, timedelta
from src.services import task_service
from src.schemas.task import TaskCreate, TaskUpdate, TaskComplete
from src.models.task import Task, TaskStatus, TaskPriority

class TestTaskService:
    """Unit tests for task service functions."""

    @pytest.mark.unit
    async def test_should_get_tasks_with_pagination(self, mock_db, mock_query_result):
        # Arrange
        mock_tasks = [
            Task(id=1, title="Task 1", status=TaskStatus.OPEN, priority=TaskPriority.HIGH),
            Task(id=2, title="Task 2", status=TaskStatus.IN_PROGRESS, priority=TaskPriority.MEDIUM),
        ]
        mock_query_result.scalars = MagicMock(return_value=MagicMock(all=MagicMock(return_value=mock_tasks)))
        
        mock_count_result = MagicMock()
        mock_count_result.scalar = MagicMock(return_value=2)
        
        mock_db.execute = AsyncMock(side_effect=[mock_query_result, mock_count_result])
        
        # Act
        tasks, total = await task_service.get_tasks(mock_db, skip=0, limit=20)
        
        # Assert
        assert len(tasks) == 2
        assert total == 2
        assert mock_db.execute.call_count == 2

    @pytest.mark.unit
    async def test_should_filter_tasks_by_status(self, mock_db, mock_query_result):
        # Arrange
        mock_tasks = [Task(id=1, title="Open Task", status=TaskStatus.OPEN, priority=TaskPriority.HIGH)]
        mock_query_result.scalars = MagicMock(return_value=MagicMock(all=MagicMock(return_value=mock_tasks)))
        
        mock_count_result = MagicMock()
        mock_count_result.scalar = MagicMock(return_value=1)
        
        mock_db.execute = AsyncMock(side_effect=[mock_query_result, mock_count_result])
        
        # Act
        tasks, total = await task_service.get_tasks(mock_db, status=TaskStatus.OPEN)
        
        # Assert
        assert len(tasks) == 1
        assert tasks[0].status == TaskStatus.OPEN

    @pytest.mark.unit
    async def test_should_get_task_by_id(self, mock_db):
        # Arrange
        expected_task = Task(id=1, title="Test Task", status=TaskStatus.OPEN, priority=TaskPriority.HIGH)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=expected_task)
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        # Act
        task = await task_service.get_task(mock_db, task_id=1)
        
        # Assert
        assert task is not None
        assert task.id == 1
        assert task.title == "Test Task"

    @pytest.mark.unit
    async def test_should_create_task_with_history_when_contact_exists(self, mock_db):
        # Arrange
        task_data = TaskCreate(
            title="New Task",
            status=TaskStatus.OPEN,
            priority=TaskPriority.HIGH,
            contact_id=1
        )
        created_task = Task(id=1, **task_data.model_dump(), created_by="test_user")
        
        with patch('src.services.task_service.get_task', AsyncMock(return_value=created_task)):
            # Act
            result = await task_service.create_task(mock_db, task_data, created_by="test_user")
        
        # Assert
        mock_db.add.assert_called()
        assert mock_db.add.call_count == 2  # Task + History
        assert mock_db.flush.await_count >= 1

    @pytest.mark.unit
    async def test_should_create_task_without_history_when_no_contact(self, mock_db):
        # Arrange
        task_data = TaskCreate(
            title="Standalone Task",
            status=TaskStatus.OPEN,
            priority=TaskPriority.MEDIUM
        )
        created_task = Task(id=1, **task_data.model_dump())
        
        with patch('src.services.task_service.get_task', AsyncMock(return_value=created_task)):
            # Act
            result = await task_service.create_task(mock_db, task_data)
        
        # Assert
        mock_db.add.assert_called_once()  # Only task, no history

    @pytest.mark.unit
    async def test_should_update_task_fields(self, mock_db):
        # Arrange
        existing_task = Task(id=1, title="Old Title", status=TaskStatus.OPEN, priority=TaskPriority.LOW)
        update_data = TaskUpdate(title="New Title", priority=TaskPriority.HIGH)
        
        with patch('src.services.task_service.get_task', AsyncMock(return_value=existing_task)):
            # Act
            result = await task_service.update_task(mock_db, task_id=1, task_data=update_data)
        
        # Assert
        assert result is not None
        assert result.title == "New Title"
        assert result.priority == TaskPriority.HIGH
        mock_db.flush.assert_awaited()

    @pytest.mark.unit
    async def test_should_complete_task_with_notes(self, mock_db):
        # Arrange
        existing_task = Task(id=1, title="Task", status=TaskStatus.IN_PROGRESS, priority=TaskPriority.HIGH)
        complete_data = TaskComplete(notes="All done!")
        
        with patch('src.services.task_service.get_task', AsyncMock(return_value=existing_task)):
            # Act
            result = await task_service.complete_task(mock_db, task_id=1, complete_data=complete_data)
        
        # Assert
        assert result is not None
        task, follow_up = result
        assert task.status == TaskStatus.COMPLETED
        assert "All done!" in task.description
        assert task.completed_at is not None
        assert follow_up is None

    @pytest.mark.unit
    async def test_should_complete_task_and_create_follow_up(self, mock_db):
        # Arrange
        existing_task = Task(
            id=1, 
            title="Task", 
            status=TaskStatus.IN_PROGRESS, 
            priority=TaskPriority.HIGH, 
            contact_id=1
        )
        complete_data = TaskComplete(
            notes="Done",
            create_follow_up=True,
            follow_up_title="Follow-up Task",
            follow_up_priority=TaskPriority.MEDIUM
        )
        
        with patch('src.services.task_service.get_task', AsyncMock(return_value=existing_task)):
            # Act
            result = await task_service.complete_task(mock_db, task_id=1, complete_data=complete_data)
        
        # Assert
        assert result is not None
        task, follow_up = result
        assert task.status == TaskStatus.COMPLETED
        mock_db.add.assert_called()  # Follow-up task added

    @pytest.mark.unit
    async def test_should_delete_task_successfully(self, mock_db):
        # Arrange
        existing_task = Task(id=1, title="Task to delete", status=TaskStatus.OPEN, priority=TaskPriority.LOW)
        
        with patch('src.services.task_service.get_task', AsyncMock(return_value=existing_task)):
            # Act
            result = await task_service.delete_task(mock_db, task_id=1)
        
        # Assert
        assert result is True
        mock_db.delete.assert_awaited_once_with(existing_task)

    @pytest.mark.unit
    async def test_should_return_false_when_deleting_nonexistent_task(self, mock_db):
        # Arrange
        with patch('src.services.task_service.get_task', AsyncMock(return_value=None)):
            # Act
            result = await task_service.delete_task(mock_db, task_id=999)
        
        # Assert
        assert result is False
        mock_db.delete.assert_not_awaited()
