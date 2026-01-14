import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from src.main import app
from src.core.database import get_db
from src.models.lead import LeadStatus
from tests.conftest import TestSessionLocal


async def override_get_db():
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestListLeads:
    @pytest.mark.asyncio
    async def test_list_leads_empty(self, client):
        response = await client.get("/api/leads")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_list_leads_pagination(self, client):
        response = await client.get("/api/leads?page=1&page_size=10")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data


class TestCreateLead:
    @pytest.mark.asyncio
    async def test_create_lead_missing_contact(self, client):
        response = await client.post("/api/leads", json={})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_lead_invalid_status(self, client):
        response = await client.post(
            "/api/leads",
            json={"contact_id": 1, "status": "invalid_status"},
        )
        assert response.status_code == 422


class TestGetLead:
    @pytest.mark.asyncio
    async def test_get_lead_not_found(self, client):
        response = await client.get("/api/leads/9999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Lead not found"


class TestUpdateLead:
    @pytest.mark.asyncio
    async def test_update_lead_not_found(self, client):
        response = await client.put(
            "/api/leads/9999",
            json={"status": "hot"},
        )
        assert response.status_code == 404


class TestImportLeads:
    @pytest.mark.asyncio
    async def test_import_no_file(self, client):
        response = await client.post("/api/leads/import")
        assert response.status_code == 422
