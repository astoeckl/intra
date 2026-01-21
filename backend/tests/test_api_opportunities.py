"""Integration tests for Opportunities API endpoints."""
import pytest
import uuid
from datetime import date, timedelta
from httpx import AsyncClient

from src.models.opportunity import Opportunity, OpportunityStage
from src.models.company import Company
from src.models.contact import Contact
from src.models.lead import Lead, LeadStatus


def unique_id():
    """Generate a unique ID for test isolation."""
    return str(uuid.uuid4())[:8]


@pytest.fixture
async def sample_opportunity(db_session, sample_company: Company, sample_contact: Contact):
    """Create a sample opportunity for testing."""
    opportunity = Opportunity(
        name="Test Opportunity",
        stage=OpportunityStage.QUALIFICATION,
        expected_value=50000.00,
        probability=10,
        expected_close_date=date.today() + timedelta(days=30),
        company_id=sample_company.id,
        contact_id=sample_contact.id,
    )
    db_session.add(opportunity)
    await db_session.flush()
    await db_session.refresh(opportunity)
    return opportunity


@pytest.fixture
async def hot_lead(db_session, sample_contact: Contact, sample_campaign):
    """Create a hot lead for conversion testing."""
    lead = Lead(
        status=LeadStatus.HOT,
        source="website",
        contact_id=sample_contact.id,
        campaign_id=sample_campaign.id,
    )
    db_session.add(lead)
    await db_session.flush()
    await db_session.refresh(lead)
    return lead


class TestOpportunitiesAPI:
    """Integration tests for Opportunities endpoints."""

    @pytest.mark.asyncio
    async def test_list_opportunities_empty_returns_200(self, client: AsyncClient):
        """Test GET /api/opportunities returns empty list when none exist."""
        # Act
        response = await client.get("/api/opportunities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_list_opportunities_with_data_returns_200(
        self, client: AsyncClient, sample_opportunity: Opportunity
    ):
        """Test GET /api/opportunities returns opportunities when data exists."""
        # Act
        response = await client.get("/api/opportunities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["id"] == sample_opportunity.id
        assert data["items"][0]["name"] == sample_opportunity.name

    @pytest.mark.asyncio
    async def test_list_opportunities_pagination_returns_200(
        self, client: AsyncClient, db_session, sample_company: Company
    ):
        """Test GET /api/opportunities pagination works correctly."""
        # Arrange - create multiple opportunities
        for i in range(5):
            opp = Opportunity(
                name=f"Test Opportunity {i}",
                stage=OpportunityStage.QUALIFICATION,
                company_id=sample_company.id,
            )
            db_session.add(opp)
        await db_session.flush()

        # Act
        response = await client.get("/api/opportunities?page=1&page_size=2")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["page"] == 1
        assert data["page_size"] == 2
        assert data["total_pages"] == 3

    @pytest.mark.asyncio
    async def test_list_opportunities_filter_by_stage_returns_200(
        self, client: AsyncClient, db_session, sample_company: Company
    ):
        """Test GET /api/opportunities?stage=qualification filters correctly."""
        # Arrange
        opp1 = Opportunity(
            name="Qualification Opp",
            stage=OpportunityStage.QUALIFICATION,
            company_id=sample_company.id,
        )
        opp2 = Opportunity(
            name="Proposal Opp",
            stage=OpportunityStage.PROPOSAL,
            company_id=sample_company.id,
        )
        db_session.add(opp1)
        db_session.add(opp2)
        await db_session.flush()

        # Act
        response = await client.get("/api/opportunities?stage=qualification")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["stage"] == "qualification"

    @pytest.mark.asyncio
    async def test_list_opportunities_filter_by_company_returns_200(
        self, client: AsyncClient, sample_opportunity: Opportunity
    ):
        """Test GET /api/opportunities?company_id=X filters correctly."""
        # Act
        response = await client.get(
            f"/api/opportunities?company_id={sample_opportunity.company_id}"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["company_id"] == sample_opportunity.company_id

    @pytest.mark.asyncio
    async def test_get_opportunity_returns_200(
        self, client: AsyncClient, sample_opportunity: Opportunity
    ):
        """Test GET /api/opportunities/{id} returns opportunity details."""
        # Act
        response = await client.get(f"/api/opportunities/{sample_opportunity.id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_opportunity.id
        assert data["name"] == sample_opportunity.name
        assert data["stage"] == sample_opportunity.stage.value
        assert data["expected_value"] == float(sample_opportunity.expected_value)
        assert "company_name" in data
        assert "contact_name" in data

    @pytest.mark.asyncio
    async def test_get_opportunity_not_found_returns_404(self, client: AsyncClient):
        """Test GET /api/opportunities/{id} returns 404 for non-existent opportunity."""
        # Act
        response = await client.get("/api/opportunities/99999")

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_create_opportunity_returns_201(
        self, client: AsyncClient, sample_company: Company, sample_contact: Contact
    ):
        """Test POST /api/opportunities creates opportunity and returns 201."""
        # Arrange
        uid = unique_id()
        payload = {
            "name": f"New Opportunity {uid}",
            "stage": "qualification",
            "expected_value": 75000.00,
            "probability": 25,
            "expected_close_date": (date.today() + timedelta(days=60)).isoformat(),
            "company_id": sample_company.id,
            "contact_id": sample_contact.id,
            "notes": "Promising deal",
        }

        # Act
        response = await client.post("/api/opportunities", json=payload)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == payload["name"]
        assert data["stage"] == "qualification"
        assert data["expected_value"] == 75000.00
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_opportunity_minimal_returns_201(self, client: AsyncClient):
        """Test POST /api/opportunities with minimal required fields."""
        # Arrange
        uid = unique_id()
        payload = {
            "name": f"Minimal Opportunity {uid}",
        }

        # Act
        response = await client.post("/api/opportunities", json=payload)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == payload["name"]
        assert data["stage"] == "qualification"  # default
        assert data["probability"] == 10  # default

    @pytest.mark.asyncio
    async def test_create_opportunity_missing_name_returns_422(self, client: AsyncClient):
        """Test POST /api/opportunities returns 422 when name is missing."""
        # Arrange
        payload = {
            "stage": "qualification",
        }

        # Act
        response = await client.post("/api/opportunities", json=payload)

        # Assert
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_opportunity_invalid_stage_returns_422(self, client: AsyncClient):
        """Test POST /api/opportunities returns 422 for invalid stage."""
        # Arrange
        payload = {
            "name": "Invalid Stage Opp",
            "stage": "invalid_stage",
        }

        # Act
        response = await client.post("/api/opportunities", json=payload)

        # Assert
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_opportunity_invalid_probability_returns_422(
        self, client: AsyncClient
    ):
        """Test POST /api/opportunities returns 422 for probability > 100."""
        # Arrange
        payload = {
            "name": "Invalid Probability Opp",
            "probability": 150,  # Invalid, must be 0-100
        }

        # Act
        response = await client.post("/api/opportunities", json=payload)

        # Assert
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_update_opportunity_returns_200(
        self, client: AsyncClient, sample_opportunity: Opportunity
    ):
        """Test PUT /api/opportunities/{id} updates opportunity."""
        # Arrange
        payload = {
            "name": "Updated Opportunity Name",
            "stage": "proposal",
            "expected_value": 100000.00,
            "probability": 50,
        }

        # Act
        response = await client.put(
            f"/api/opportunities/{sample_opportunity.id}", json=payload
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == payload["name"]
        assert data["stage"] == "proposal"
        assert data["expected_value"] == 100000.00
        assert data["probability"] == 50

    @pytest.mark.asyncio
    async def test_update_opportunity_partial_returns_200(
        self, client: AsyncClient, sample_opportunity: Opportunity
    ):
        """Test PUT /api/opportunities/{id} with partial update."""
        # Arrange
        original_name = sample_opportunity.name
        payload = {
            "notes": "Updated notes only",
        }

        # Act
        response = await client.put(
            f"/api/opportunities/{sample_opportunity.id}", json=payload
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["notes"] == payload["notes"]
        assert data["name"] == original_name

    @pytest.mark.asyncio
    async def test_update_opportunity_not_found_returns_404(self, client: AsyncClient):
        """Test PUT /api/opportunities/{id} returns 404 for non-existent opportunity."""
        # Arrange
        payload = {"name": "Updated Name"}

        # Act
        response = await client.put("/api/opportunities/99999", json=payload)

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_delete_opportunity_returns_204(
        self, client: AsyncClient, sample_opportunity: Opportunity
    ):
        """Test DELETE /api/opportunities/{id} deletes opportunity."""
        # Act
        response = await client.delete(f"/api/opportunities/{sample_opportunity.id}")

        # Assert
        assert response.status_code == 204

        # Verify opportunity is deleted
        get_response = await client.get(f"/api/opportunities/{sample_opportunity.id}")
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_opportunity_not_found_returns_404(self, client: AsyncClient):
        """Test DELETE /api/opportunities/{id} returns 404 for non-existent opportunity."""
        # Act
        response = await client.delete("/api/opportunities/99999")

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestOpportunityConversionAPI:
    """Integration tests for lead-to-opportunity conversion."""

    @pytest.mark.asyncio
    async def test_convert_lead_to_opportunity_returns_201(
        self, client: AsyncClient, hot_lead: Lead
    ):
        """Test POST /api/opportunities/convert/{lead_id} converts hot lead."""
        # Arrange
        uid = unique_id()
        payload = {
            "name": f"Converted Opportunity {uid}",
            "expected_value": 80000.00,
            "expected_close_date": (date.today() + timedelta(days=45)).isoformat(),
            "notes": "Converted from hot lead",
        }

        # Act
        response = await client.post(
            f"/api/opportunities/convert/{hot_lead.id}", json=payload
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == payload["name"]
        assert data["lead_id"] == hot_lead.id
        assert data["contact_id"] == hot_lead.contact_id

    @pytest.mark.asyncio
    async def test_convert_non_hot_lead_returns_400(
        self, client: AsyncClient, sample_lead: Lead
    ):
        """Test POST /api/opportunities/convert/{lead_id} fails for non-hot lead."""
        # sample_lead has COLD status
        # Arrange
        payload = {
            "name": "Should Fail Conversion",
        }

        # Act
        response = await client.post(
            f"/api/opportunities/convert/{sample_lead.id}", json=payload
        )

        # Assert
        assert response.status_code == 400
        assert "not hot" in response.json()["detail"].lower() or "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_convert_nonexistent_lead_returns_400(self, client: AsyncClient):
        """Test POST /api/opportunities/convert/{lead_id} fails for non-existent lead."""
        # Arrange
        payload = {
            "name": "Should Fail",
        }

        # Act
        response = await client.post(
            "/api/opportunities/convert/99999", json=payload
        )

        # Assert
        assert response.status_code == 400


class TestOpportunityCloseAPI:
    """Integration tests for closing opportunities."""

    @pytest.mark.asyncio
    async def test_close_opportunity_won_returns_200(
        self, client: AsyncClient, sample_opportunity: Opportunity
    ):
        """Test POST /api/opportunities/{id}/close marks opportunity as won."""
        # Arrange
        payload = {
            "won": True,
            "close_reason": "Customer signed contract",
            "actual_value": 55000.00,
        }

        # Act
        response = await client.post(
            f"/api/opportunities/{sample_opportunity.id}/close", json=payload
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["stage"] == "closed_won"
        assert data["close_reason"] == payload["close_reason"]
        assert data["actual_close_date"] is not None

    @pytest.mark.asyncio
    async def test_close_opportunity_lost_returns_200(
        self, client: AsyncClient, sample_opportunity: Opportunity
    ):
        """Test POST /api/opportunities/{id}/close marks opportunity as lost."""
        # Arrange
        payload = {
            "won": False,
            "close_reason": "Lost to competitor",
        }

        # Act
        response = await client.post(
            f"/api/opportunities/{sample_opportunity.id}/close", json=payload
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["stage"] == "closed_lost"
        assert data["close_reason"] == payload["close_reason"]

    @pytest.mark.asyncio
    async def test_close_nonexistent_opportunity_returns_400(self, client: AsyncClient):
        """Test POST /api/opportunities/{id}/close returns 400 for non-existent."""
        # Arrange
        payload = {"won": True}

        # Act
        response = await client.post(
            "/api/opportunities/99999/close", json=payload
        )

        # Assert
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_close_already_closed_opportunity_returns_400(
        self, client: AsyncClient, db_session, sample_company: Company
    ):
        """Test POST /api/opportunities/{id}/close fails for already closed opportunity."""
        # Arrange - create already closed opportunity
        closed_opp = Opportunity(
            name="Already Closed Opp",
            stage=OpportunityStage.CLOSED_WON,
            company_id=sample_company.id,
            actual_close_date=date.today(),
        )
        db_session.add(closed_opp)
        await db_session.flush()
        await db_session.refresh(closed_opp)

        payload = {"won": False, "close_reason": "Try to re-close"}

        # Act
        response = await client.post(
            f"/api/opportunities/{closed_opp.id}/close", json=payload
        )

        # Assert
        assert response.status_code == 400
        assert "already closed" in response.json()["detail"].lower()


class TestPipelineStatsAPI:
    """Integration tests for pipeline statistics."""

    @pytest.mark.asyncio
    async def test_get_pipeline_stats_empty_returns_200(self, client: AsyncClient):
        """Test GET /api/opportunities/stats returns stats even when empty."""
        # Act
        response = await client.get("/api/opportunities/stats")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "total_opportunities" in data
        assert "total_value" in data
        assert "weighted_value" in data
        assert "stages" in data
        assert "win_rate" in data
        assert "average_deal_size" in data

    @pytest.mark.asyncio
    async def test_get_pipeline_stats_with_data_returns_200(
        self, client: AsyncClient, sample_opportunity: Opportunity
    ):
        """Test GET /api/opportunities/stats returns correct stats with data."""
        # Act
        response = await client.get("/api/opportunities/stats")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total_opportunities"] >= 1
        assert isinstance(data["stages"], list)
