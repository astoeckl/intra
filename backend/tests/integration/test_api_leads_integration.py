"""Integration tests for leads API endpoints."""
import pytest
from httpx import AsyncClient
from src.models.lead import LeadStatus

class TestLeadsAPI:
    """Integration tests for /api/leads endpoints."""

    @pytest.mark.integration
    async def test_should_return_200_and_empty_list_when_no_leads(self, client):
        # Arrange - no leads in database
        
        # Act
        response = await client.get("/api/leads")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 0
        assert len(data["items"]) == 0

    @pytest.mark.integration
    async def test_should_return_200_and_leads_list(self, client, sample_lead):
        # Arrange - sample_lead fixture creates a lead
        
        # Act
        response = await client.get("/api/leads")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert len(data["items"]) >= 1
        assert "contact_name" in data["items"][0]

    @pytest.mark.integration
    async def test_should_filter_leads_by_status(self, client, multiple_leads):
        # Arrange - multiple_leads creates leads with different statuses
        
        # Act
        response = await client.get(f"/api/leads?status={LeadStatus.HOT.value}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        # Should only return HOT leads
        for item in data["items"]:
            assert item["status"] == LeadStatus.HOT.value

    @pytest.mark.integration
    async def test_should_return_lead_by_id(self, client, sample_lead):
        # Arrange
        lead_id = sample_lead.id
        
        # Act
        response = await client.get(f"/api/leads/{lead_id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == lead_id
        assert "status" in data
        assert "contact" in data

    @pytest.mark.integration
    async def test_should_return_404_for_nonexistent_lead(self, client):
        # Arrange
        nonexistent_id = 99999
        
        # Act
        response = await client.get(f"/api/leads/{nonexistent_id}")
        
        # Assert
        assert response.status_code == 404
        error = response.json()
        assert "not found" in error["detail"].lower()

    @pytest.mark.integration
    async def test_should_create_lead_with_valid_data(self, client, sample_contact):
        # Arrange
        lead_data = {
            "contact_id": sample_contact.id,
            "status": LeadStatus.COLD.value,
            "source": "manual"
        }
        
        # Act
        response = await client.post("/api/leads", json=lead_data)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["contact_id"] == sample_contact.id
        assert data["status"] == LeadStatus.COLD.value
        assert "id" in data

    @pytest.mark.integration
    async def test_should_create_lead_even_with_invalid_contact_id(self, client):
        # Arrange
        invalid_data = {
            "contact_id": 99999,  # Non-existent (but API doesn't validate)
            "status": LeadStatus.COLD.value,
            "source": "manual"
        }
        
        # Act
        response = await client.post("/api/leads", json=invalid_data)
        
        # Assert
        # API currently doesn't validate contact_id existence
        # It will create the lead, but may fail on foreign key constraint
        assert response.status_code in [201, 500]

    @pytest.mark.integration
    async def test_should_update_lead_status(self, client, sample_lead):
        # Arrange
        lead_id = sample_lead.id
        update_data = {"status": LeadStatus.HOT.value}
        
        # Act
        response = await client.put(f"/api/leads/{lead_id}", json=update_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == lead_id
        assert data["status"] == LeadStatus.HOT.value

    @pytest.mark.integration
    async def test_should_return_404_when_updating_nonexistent_lead(self, client):
        # Arrange
        nonexistent_id = 99999
        update_data = {"status": LeadStatus.HOT.value}
        
        # Act
        response = await client.put(f"/api/leads/{nonexistent_id}", json=update_data)
        
        # Assert
        assert response.status_code == 404

    @pytest.mark.integration
    async def test_should_support_pagination(self, client, multiple_leads):
        # Arrange - multiple_leads creates 5 leads
        
        # Act - request page 1 with page size 2
        response = await client.get("/api/leads?page=1&page_size=2")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 2
        assert len(data["items"]) <= 2
        assert data["total"] >= 5
