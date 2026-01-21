"""Integration tests for tasks API endpoints."""
import pytest
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient
from src.models.task import TaskStatus, TaskPriority

class TestTasksAPI:
    """Integration tests for /api/tasks endpoints."""

    @pytest.mark.integration
    async def test_should_return_200_and_empty_list_when_no_tasks(self, client):
        # Arrange - no tasks in database
        
        # Act
        response = await client.get("/api/tasks")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 0

    @pytest.mark.integration
    async def test_should_return_200_and_tasks_list(self, client, sample_task):
        # Arrange - sample_task fixture creates a task
        
        # Act
        response = await client.get("/api/tasks")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert len(data["items"]) >= 1
        assert "title" in data["items"][0]

    @pytest.mark.integration
    async def test_should_filter_tasks_by_status(self, client, multiple_tasks):
        # Arrange - multiple_tasks creates tasks with different statuses
        
        # Act
        response = await client.get(f"/api/tasks?status={TaskStatus.OPEN.value}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        for item in data["items"]:
            assert item["status"] == TaskStatus.OPEN.value

    @pytest.mark.integration
    async def test_should_filter_tasks_by_priority(self, client, multiple_tasks):
        # Arrange
        
        # Act
        response = await client.get(f"/api/tasks?priority={TaskPriority.URGENT.value}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        for item in data["items"]:
            assert item["priority"] == TaskPriority.URGENT.value

    @pytest.mark.integration
    async def test_should_return_task_by_id(self, client, sample_task):
        # Arrange
        task_id = sample_task.id
        
        # Act
        response = await client.get(f"/api/tasks/{task_id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert "title" in data
        assert "status" in data

    @pytest.mark.integration
    async def test_should_return_404_for_nonexistent_task(self, client):
        # Arrange
        nonexistent_id = 99999
        
        # Act
        response = await client.get(f"/api/tasks/{nonexistent_id}")
        
        # Assert
        assert response.status_code == 404
        error = response.json()
        assert "not found" in error["detail"].lower()

    @pytest.mark.integration
    async def test_should_create_task_with_valid_data(self, client, sample_contact):
        # Arrange
        task_data = {
            "title": "New Task",
            "status": TaskStatus.OPEN.value,
            "priority": TaskPriority.HIGH.value,
            "contact_id": sample_contact.id
        }
        
        # Act
        response = await client.post("/api/tasks", json=task_data)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Task"
        assert data["status"] == TaskStatus.OPEN.value
        assert "id" in data

    @pytest.mark.integration
    async def test_should_update_task_fields(self, client, sample_task):
        # Arrange
        task_id = sample_task.id
        update_data = {"title": "Updated Title", "priority": TaskPriority.LOW.value}
        
        # Act
        response = await client.put(f"/api/tasks/{task_id}", json=update_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == "Updated Title"
        assert data["priority"] == TaskPriority.LOW.value

    @pytest.mark.integration
    async def test_should_return_404_when_updating_nonexistent_task(self, client):
        # Arrange
        nonexistent_id = 99999
        update_data = {"title": "Updated"}
        
        # Act
        response = await client.put(f"/api/tasks/{nonexistent_id}", json=update_data)
        
        # Assert
        assert response.status_code == 404

    @pytest.mark.integration
    async def test_should_complete_task(self, client, sample_task):
        # Arrange
        task_id = sample_task.id
        complete_data = {"notes": "Task completed successfully"}
        
        # Act
        response = await client.post(f"/api/tasks/{task_id}/complete", json=complete_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "task" in data
        assert data["task"]["status"] == TaskStatus.COMPLETED.value
        assert data["task"]["completed_at"] is not None

    @pytest.mark.integration
    async def test_should_complete_task_and_create_follow_up(self, client, sample_task):
        # Arrange
        task_id = sample_task.id
        complete_data = {
            "notes": "Done",
            "create_follow_up": True,
            "follow_up_title": "Follow-up Task",
            "follow_up_priority": TaskPriority.MEDIUM.value
        }
        
        # Act
        response = await client.post(f"/api/tasks/{task_id}/complete", json=complete_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["task"]["status"] == TaskStatus.COMPLETED.value
        assert data["follow_up_task"] is not None
        assert data["follow_up_task"]["title"] == "Follow-up Task"

    @pytest.mark.integration
    async def test_should_delete_task(self, client, sample_task):
        # Arrange
        task_id = sample_task.id
        
        # Act
        response = await client.delete(f"/api/tasks/{task_id}")
        
        # Assert
        assert response.status_code == 204
        
        # Verify deleted
        get_response = await client.get(f"/api/tasks/{task_id}")
        assert get_response.status_code == 404

    @pytest.mark.integration
    async def test_should_return_404_when_deleting_nonexistent_task(self, client):
        # Arrange
        nonexistent_id = 99999
        
        # Act
        response = await client.delete(f"/api/tasks/{nonexistent_id}")
        
        # Assert
        assert response.status_code == 404

    @pytest.mark.integration
    async def test_should_support_pagination(self, client, multiple_tasks):
        # Arrange - multiple_tasks creates 5 tasks
        
        # Act - request page 1 with page size 2
        response = await client.get("/api/tasks?page=1&page_size=2")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 2
        assert len(data["items"]) <= 2
        assert data["total"] >= 5
