"""
Tests for API Routes.
"""
from datetime import datetime, timezone, timedelta

import pytest
from httpx import AsyncClient

from src.models.contact import Contact
from src.models.lead import Lead, LeadStatus
from src.models.task import Task, TaskStatus, TaskPriority
from src.models.campaign import Campaign
from src.models.contact_history import ContactHistory


class TestLeadsAPI:
    """Tests for Leads API endpoints."""

    @pytest.mark.asyncio
    async def test_list_leads_empty(self, client: AsyncClient):
        """Test listing leads when none exist."""
        response = await client.get("/api/leads")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_list_leads_with_data(
        self, client: AsyncClient, sample_lead: Lead
    ):
        """Test listing leads with data."""
        response = await client.get("/api/leads")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["id"] == sample_lead.id

    @pytest.mark.asyncio
    async def test_list_leads_pagination(
        self, client: AsyncClient, multiple_leads: list[Lead]
    ):
        """Test leads pagination."""
        response = await client.get("/api/leads?page=1&page_size=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["page"] == 1
        assert data["page_size"] == 2
        assert data["total_pages"] == 3

    @pytest.mark.asyncio
    async def test_list_leads_filter_by_status(
        self, client: AsyncClient, multiple_leads: list[Lead]
    ):
        """Test filtering leads by status."""
        response = await client.get("/api/leads?status=new")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        for item in data["items"]:
            assert item["status"] == "new"

    @pytest.mark.asyncio
    async def test_get_lead(self, client: AsyncClient, sample_lead: Lead):
        """Test getting a single lead."""
        response = await client.get(f"/api/leads/{sample_lead.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_lead.id

    @pytest.mark.asyncio
    async def test_get_lead_not_found(self, client: AsyncClient):
        """Test getting a non-existent lead."""
        response = await client.get("/api/leads/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_create_lead(
        self, client: AsyncClient, sample_contact: Contact, sample_campaign: Campaign
    ):
        """Test creating a lead."""
        response = await client.post(
            "/api/leads",
            json={
                "contact_id": sample_contact.id,
                "campaign_id": sample_campaign.id,
                "status": "new",
                "source": "api_test",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["contact_id"] == sample_contact.id
        assert data["source"] == "api_test"

    @pytest.mark.asyncio
    async def test_update_lead(self, client: AsyncClient, sample_lead: Lead):
        """Test updating a lead."""
        response = await client.put(
            f"/api/leads/{sample_lead.id}",
            json={
                "status": "contacted",
                "notes": "Erstkontakt durchgeführt",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "contacted"
        assert data["notes"] == "Erstkontakt durchgeführt"

    @pytest.mark.asyncio
    async def test_update_lead_not_found(self, client: AsyncClient):
        """Test updating a non-existent lead."""
        response = await client.put(
            "/api/leads/99999",
            json={"status": "contacted"},
        )
        assert response.status_code == 404


class TestContactsAPI:
    """Tests for Contacts API endpoints."""

    @pytest.mark.asyncio
    async def test_list_contacts_empty(self, client: AsyncClient):
        """Test listing contacts when none exist."""
        response = await client.get("/api/contacts")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_list_contacts_with_data(
        self, client: AsyncClient, sample_contact: Contact
    ):
        """Test listing contacts with data."""
        response = await client.get("/api/contacts")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1

    @pytest.mark.asyncio
    async def test_list_contacts_search(
        self, client: AsyncClient, multiple_contacts: list[Contact]
    ):
        """Test searching contacts."""
        response = await client.get("/api/contacts?search=Anna")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["first_name"] == "Anna"

    @pytest.mark.asyncio
    async def test_search_contacts_autocomplete(
        self, client: AsyncClient, multiple_contacts: list[Contact]
    ):
        """Test contact search autocomplete."""
        response = await client.get("/api/contacts/search?q=Schmidt")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "Schmidt" in data[0]["full_name"]

    @pytest.mark.asyncio
    async def test_search_contacts_autocomplete_min_length(
        self, client: AsyncClient
    ):
        """Test that search requires minimum 2 characters."""
        response = await client.get("/api/contacts/search?q=A")
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_get_contact(self, client: AsyncClient, sample_contact: Contact):
        """Test getting a single contact."""
        response = await client.get(f"/api/contacts/{sample_contact.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_contact.id
        assert data["first_name"] == sample_contact.first_name

    @pytest.mark.asyncio
    async def test_get_contact_not_found(self, client: AsyncClient):
        """Test getting a non-existent contact."""
        response = await client.get("/api/contacts/99999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_contact(self, client: AsyncClient):
        """Test creating a contact."""
        response = await client.post(
            "/api/contacts",
            json={
                "first_name": "Neuer",
                "last_name": "Kontakt",
                "email": "neuer.kontakt@test.at",
                "phone": "+43 1 1234567",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["first_name"] == "Neuer"
        assert data["last_name"] == "Kontakt"
        assert data["email"] == "neuer.kontakt@test.at"

    @pytest.mark.asyncio
    async def test_update_contact(self, client: AsyncClient, sample_contact: Contact):
        """Test updating a contact."""
        response = await client.put(
            f"/api/contacts/{sample_contact.id}",
            json={
                "position": "CEO",
                "notes": "Befördert",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["position"] == "CEO"
        assert data["notes"] == "Befördert"

    @pytest.mark.asyncio
    async def test_delete_contact(self, client: AsyncClient, sample_contact: Contact):
        """Test soft deleting a contact."""
        response = await client.delete(f"/api/contacts/{sample_contact.id}")
        assert response.status_code == 204
        
        # Verify contact is now inactive
        get_response = await client.get(f"/api/contacts/{sample_contact.id}")
        assert get_response.status_code == 200
        assert get_response.json()["is_active"] is False


class TestContactHistoryAPI:
    """Tests for Contact History API endpoints."""

    @pytest.mark.asyncio
    async def test_get_contact_history(
        self, client: AsyncClient, sample_contact: Contact, sample_history_note: ContactHistory
    ):
        """Test getting contact history."""
        response = await client.get(f"/api/contacts/{sample_contact.id}/history")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["type"] == "note"

    @pytest.mark.asyncio
    async def test_add_note(self, client: AsyncClient, sample_contact: Contact):
        """Test adding a note to contact history."""
        response = await client.post(
            f"/api/contacts/{sample_contact.id}/notes",
            json={"content": "Wichtige Notiz zum Kontakt"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "note"
        assert data["content"] == "Wichtige Notiz zum Kontakt"

    @pytest.mark.asyncio
    async def test_add_call(self, client: AsyncClient, sample_contact: Contact):
        """Test adding a call to contact history."""
        response = await client.post(
            f"/api/contacts/{sample_contact.id}/calls",
            json={
                "content": "Gespräch über Angebot",
                "duration_minutes": 15,
                "outcome": "reached",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "call"
        assert data["content"] == "Gespräch über Angebot"

    @pytest.mark.asyncio
    async def test_update_history_entry(
        self, client: AsyncClient, sample_history_note: ContactHistory
    ):
        """Test updating a history entry."""
        response = await client.put(
            f"/api/contacts/history/{sample_history_note.id}",
            json={
                "title": "Aktualisierte Notiz",
                "content": "Neuer Inhalt",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Aktualisierte Notiz"
        assert data["content"] == "Neuer Inhalt"

    @pytest.mark.asyncio
    async def test_delete_history_entry(
        self, client: AsyncClient, sample_history_note: ContactHistory
    ):
        """Test deleting a history entry."""
        response = await client.delete(
            f"/api/contacts/history/{sample_history_note.id}"
        )
        assert response.status_code == 204


class TestTasksAPI:
    """Tests for Tasks API endpoints."""

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
        self, client: AsyncClient, sample_task: Task
    ):
        """Test listing tasks with data."""
        response = await client.get("/api/tasks")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["id"] == sample_task.id

    @pytest.mark.asyncio
    async def test_list_tasks_filter_by_status(
        self, client: AsyncClient, sample_task: Task
    ):
        """Test filtering tasks by status."""
        response = await client.get("/api/tasks?status=open")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["status"] == "open"

    @pytest.mark.asyncio
    async def test_list_tasks_overdue(
        self, client: AsyncClient, sample_task: Task, sample_overdue_task: Task
    ):
        """Test listing overdue tasks."""
        response = await client.get("/api/tasks?is_overdue=true")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["id"] == sample_overdue_task.id
        assert data["items"][0]["is_overdue"] is True

    @pytest.mark.asyncio
    async def test_get_my_tasks(
        self, client: AsyncClient, sample_task: Task
    ):
        """Test getting tasks assigned to current user."""
        response = await client.get("/api/tasks/my")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1

    @pytest.mark.asyncio
    async def test_get_task(self, client: AsyncClient, sample_task: Task):
        """Test getting a single task."""
        response = await client.get(f"/api/tasks/{sample_task.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_task.id
        assert data["title"] == sample_task.title

    @pytest.mark.asyncio
    async def test_get_task_not_found(self, client: AsyncClient):
        """Test getting a non-existent task."""
        response = await client.get("/api/tasks/99999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_task(
        self, client: AsyncClient, sample_contact: Contact
    ):
        """Test creating a task."""
        due_date = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        response = await client.post(
            "/api/tasks",
            json={
                "title": "Neue Aufgabe",
                "description": "Beschreibung",
                "priority": "high",
                "due_date": due_date,
                "contact_id": sample_contact.id,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Neue Aufgabe"
        assert data["priority"] == "high"

    @pytest.mark.asyncio
    async def test_update_task(self, client: AsyncClient, sample_task: Task):
        """Test updating a task."""
        response = await client.put(
            f"/api/tasks/{sample_task.id}",
            json={
                "title": "Aktualisierte Aufgabe",
                "status": "in_progress",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Aktualisierte Aufgabe"
        assert data["status"] == "in_progress"

    @pytest.mark.asyncio
    async def test_complete_task(self, client: AsyncClient, sample_task: Task):
        """Test completing a task."""
        response = await client.post(
            f"/api/tasks/{sample_task.id}/complete",
            json={
                "notes": "Aufgabe erledigt",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["task"]["status"] == "completed"
        assert data["follow_up_task"] is None

    @pytest.mark.asyncio
    async def test_complete_task_with_followup(
        self, client: AsyncClient, sample_task: Task
    ):
        """Test completing a task with follow-up."""
        follow_up_due = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        response = await client.post(
            f"/api/tasks/{sample_task.id}/complete",
            json={
                "notes": "Erstgespräch durchgeführt",
                "create_follow_up": True,
                "follow_up_title": "Nachfassen",
                "follow_up_due_date": follow_up_due,
                "follow_up_priority": "high",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["task"]["status"] == "completed"
        assert data["follow_up_task"] is not None
        assert data["follow_up_task"]["title"] == "Nachfassen"

    @pytest.mark.asyncio
    async def test_delete_task(self, client: AsyncClient, sample_task: Task):
        """Test deleting a task."""
        response = await client.delete(f"/api/tasks/{sample_task.id}")
        assert response.status_code == 204
        
        # Verify task is gone
        get_response = await client.get(f"/api/tasks/{sample_task.id}")
        assert get_response.status_code == 404


class TestHealthAPI:
    """Tests for Health check endpoint."""

    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """Test health check endpoint."""
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
