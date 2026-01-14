"""Tests for the task API routes."""
import pytest
from datetime import datetime, timezone
from httpx import AsyncClient

from src.models.task import Task, TaskStatus, TaskPriority
from src.models.contact import Contact


class TestListTasksEndpoint:
    """Tests for GET /api/tasks endpoint."""

    @pytest.mark.asyncio
    async def test_list_tasks_empty(self, client: AsyncClient):
        """Test listing tasks when none exist."""
        response = await client.get("/api/tasks")

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_list_tasks_with_data(
        self, client: AsyncClient, multiple_tasks: list[Task]
    ):
        """Test listing all tasks."""
        response = await client.get("/api/tasks")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 5

    @pytest.mark.asyncio
    async def test_list_tasks_filter_by_status(
        self, client: AsyncClient, multiple_tasks: list[Task]
    ):
        """Test filtering tasks by status."""
        response = await client.get("/api/tasks", params={"status": "open"})

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert all(item["status"] == "open" for item in data["items"])

    @pytest.mark.asyncio
    async def test_list_tasks_filter_by_deferred_status(
        self, client: AsyncClient, multiple_tasks: list[Task]
    ):
        """Test filtering tasks by deferred status."""
        response = await client.get("/api/tasks", params={"status": "deferred"})

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["status"] == "deferred"

    @pytest.mark.asyncio
    async def test_list_tasks_filter_by_priority(
        self, client: AsyncClient, multiple_tasks: list[Task]
    ):
        """Test filtering tasks by priority."""
        response = await client.get("/api/tasks", params={"priority": "urgent"})

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["priority"] == "urgent"

    @pytest.mark.asyncio
    async def test_list_tasks_pagination(
        self, client: AsyncClient, multiple_tasks: list[Task]
    ):
        """Test task pagination."""
        response = await client.get("/api/tasks", params={"page": 1, "page_size": 2})

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2
        assert data["page"] == 1
        assert data["page_size"] == 2
        assert data["total_pages"] == 3

    @pytest.mark.asyncio
    async def test_list_tasks_includes_contact_name(
        self, client: AsyncClient, sample_task: Task
    ):
        """Test that task list includes contact name."""
        response = await client.get("/api/tasks")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["contact_name"] == "Max Mustermann"


class TestGetTaskEndpoint:
    """Tests for GET /api/tasks/{task_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_task_success(
        self, client: AsyncClient, sample_task: Task
    ):
        """Test getting a single task."""
        response = await client.get(f"/api/tasks/{sample_task.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_task.id
        assert data["title"] == "Test Aufgabe"
        assert data["description"] == "Test Beschreibung"
        assert data["status"] == "open"
        assert data["priority"] == "medium"

    @pytest.mark.asyncio
    async def test_get_task_not_found(self, client: AsyncClient):
        """Test getting a non-existent task."""
        response = await client.get("/api/tasks/99999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Task not found"


class TestCreateTaskEndpoint:
    """Tests for POST /api/tasks endpoint."""

    @pytest.mark.asyncio
    async def test_create_task_minimal(self, client: AsyncClient):
        """Test creating a task with minimal data."""
        task_data = {"title": "Neue Aufgabe"}

        response = await client.post("/api/tasks", json=task_data)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Neue Aufgabe"
        assert data["status"] == "open"
        assert data["priority"] == "medium"

    @pytest.mark.asyncio
    async def test_create_task_full(
        self, client: AsyncClient, sample_contact: Contact
    ):
        """Test creating a task with all fields."""
        task_data = {
            "title": "Vollständige Aufgabe",
            "description": "Detaillierte Beschreibung",
            "status": "in_progress",
            "priority": "high",
            "due_date": "2026-02-15T14:00:00Z",
            "contact_id": sample_contact.id,
            "assigned_to": "test_user",
        }

        response = await client.post("/api/tasks", json=task_data)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Vollständige Aufgabe"
        assert data["description"] == "Detaillierte Beschreibung"
        assert data["status"] == "in_progress"
        assert data["priority"] == "high"
        assert data["contact_id"] == sample_contact.id

    @pytest.mark.asyncio
    async def test_create_task_validation_error(self, client: AsyncClient):
        """Test creating a task with invalid data."""
        task_data = {"title": ""}  # Empty title should fail

        response = await client.post("/api/tasks", json=task_data)

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_task_with_urgent_priority(self, client: AsyncClient):
        """Test creating a task with urgent priority."""
        task_data = {
            "title": "Dringende Aufgabe",
            "priority": "urgent",
        }

        response = await client.post("/api/tasks", json=task_data)

        assert response.status_code == 201
        data = response.json()
        assert data["priority"] == "urgent"


class TestUpdateTaskEndpoint:
    """Tests for PUT /api/tasks/{task_id} endpoint."""

    @pytest.mark.asyncio
    async def test_update_task_title(
        self, client: AsyncClient, sample_task: Task
    ):
        """Test updating task title."""
        update_data = {"title": "Aktualisierter Titel"}

        response = await client.put(
            f"/api/tasks/{sample_task.id}", json=update_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Aktualisierter Titel"

    @pytest.mark.asyncio
    async def test_update_task_status_to_deferred(
        self, client: AsyncClient, sample_task: Task
    ):
        """Test updating task status to deferred."""
        update_data = {"status": "deferred"}

        response = await client.put(
            f"/api/tasks/{sample_task.id}", json=update_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "deferred"

    @pytest.mark.asyncio
    async def test_update_task_priority(
        self, client: AsyncClient, sample_task: Task
    ):
        """Test updating task priority."""
        update_data = {"priority": "urgent"}

        response = await client.put(
            f"/api/tasks/{sample_task.id}", json=update_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["priority"] == "urgent"

    @pytest.mark.asyncio
    async def test_update_task_not_found(self, client: AsyncClient):
        """Test updating non-existent task."""
        update_data = {"title": "Nicht existent"}

        response = await client.put("/api/tasks/99999", json=update_data)

        assert response.status_code == 404


class TestCompleteTaskEndpoint:
    """Tests for POST /api/tasks/{task_id}/complete endpoint."""

    @pytest.mark.asyncio
    async def test_complete_task_basic(
        self, client: AsyncClient, sample_task: Task
    ):
        """Test completing a task."""
        response = await client.post(
            f"/api/tasks/{sample_task.id}/complete", json={}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["task"]["status"] == "completed"
        assert data["task"]["completed_at"] is not None
        assert data["follow_up_task"] is None

    @pytest.mark.asyncio
    async def test_complete_task_with_notes(
        self, client: AsyncClient, sample_task: Task
    ):
        """Test completing a task with notes."""
        complete_data = {"notes": "Erfolgreich erledigt"}

        response = await client.post(
            f"/api/tasks/{sample_task.id}/complete", json=complete_data
        )

        assert response.status_code == 200
        data = response.json()
        assert "Abschlussnotiz" in data["task"]["description"]

    @pytest.mark.asyncio
    async def test_complete_task_with_follow_up(
        self, client: AsyncClient, sample_task: Task
    ):
        """Test completing a task with follow-up."""
        complete_data = {
            "create_follow_up": True,
            "follow_up_title": "Nachfassen",
            "follow_up_due_date": "2026-02-01T10:00:00Z",
            "follow_up_priority": "high",
        }

        response = await client.post(
            f"/api/tasks/{sample_task.id}/complete", json=complete_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["task"]["status"] == "completed"
        assert data["follow_up_task"] is not None
        assert data["follow_up_task"]["title"] == "Nachfassen"
        assert data["follow_up_task"]["priority"] == "high"
        assert data["follow_up_task"]["status"] == "open"

    @pytest.mark.asyncio
    async def test_complete_task_not_found(self, client: AsyncClient):
        """Test completing non-existent task."""
        response = await client.post(
            "/api/tasks/99999/complete", json={}
        )

        assert response.status_code == 404


class TestDeleteTaskEndpoint:
    """Tests for DELETE /api/tasks/{task_id} endpoint."""

    @pytest.mark.asyncio
    async def test_delete_task_success(
        self, client: AsyncClient, sample_task: Task
    ):
        """Test deleting a task."""
        response = await client.delete(f"/api/tasks/{sample_task.id}")

        assert response.status_code == 204

        # Verify task is deleted
        get_response = await client.get(f"/api/tasks/{sample_task.id}")
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_task_not_found(self, client: AsyncClient):
        """Test deleting non-existent task."""
        response = await client.delete("/api/tasks/99999")

        assert response.status_code == 404


class TestTaskStatusEnum:
    """Tests for task status enum values."""

    @pytest.mark.asyncio
    async def test_all_status_values_work(self, client: AsyncClient):
        """Test that all status values can be used."""
        statuses = ["open", "in_progress", "deferred", "completed", "cancelled"]

        for status in statuses:
            task_data = {"title": f"Task with {status}", "status": status}
            response = await client.post("/api/tasks", json=task_data)
            assert response.status_code == 201
            assert response.json()["status"] == status

    @pytest.mark.asyncio
    async def test_invalid_status_rejected(self, client: AsyncClient):
        """Test that invalid status values are rejected."""
        task_data = {"title": "Invalid", "status": "invalid_status"}

        response = await client.post("/api/tasks", json=task_data)

        assert response.status_code == 422


class TestTaskPriorityEnum:
    """Tests for task priority enum values."""

    @pytest.mark.asyncio
    async def test_all_priority_values_work(self, client: AsyncClient):
        """Test that all priority values can be used."""
        priorities = ["low", "medium", "high", "urgent"]

        for priority in priorities:
            task_data = {"title": f"Task with {priority}", "priority": priority}
            response = await client.post("/api/tasks", json=task_data)
            assert response.status_code == 201
            assert response.json()["priority"] == priority
