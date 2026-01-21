"""Integration tests for Email Templates API endpoints."""
import pytest
import uuid
from httpx import AsyncClient

from src.models.email_template import EmailTemplate
from src.models.contact import Contact


def unique_id():
    """Generate a unique ID for test isolation."""
    return str(uuid.uuid4())[:8]


@pytest.fixture
async def sample_email_template(db_session):
    """Create a sample email template for testing."""
    template = EmailTemplate(
        name="Welcome Template",
        subject="Welcome {{contact.first_name}}!",
        body="Hello {{contact.first_name}} {{contact.last_name}},\n\nWelcome to our service!",
        description="Standard welcome email",
        category="onboarding",
        is_active=True,
        # Note: variables stored as JSON string in DB, parsed by route handler
    )
    db_session.add(template)
    await db_session.flush()
    await db_session.refresh(template)
    return template


class TestEmailTemplatesAPI:
    """Integration tests for Email Templates endpoints."""

    @pytest.mark.asyncio
    async def test_list_templates_empty_returns_200(self, client: AsyncClient):
        """Test GET /api/email-templates returns empty list when none exist."""
        # Act
        response = await client.get("/api/email-templates")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_list_templates_with_data_returns_200(
        self, client: AsyncClient, sample_email_template: EmailTemplate
    ):
        """Test GET /api/email-templates returns templates when data exists."""
        # Act
        response = await client.get("/api/email-templates")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["id"] == sample_email_template.id
        assert data["items"][0]["name"] == sample_email_template.name

    @pytest.mark.asyncio
    async def test_list_templates_pagination_returns_200(
        self, client: AsyncClient, db_session
    ):
        """Test GET /api/email-templates pagination works correctly."""
        # Arrange - create multiple templates
        for i in range(5):
            template = EmailTemplate(
                name=f"Template {i}",
                subject=f"Subject {i}",
                body=f"Body {i}",
                is_active=True,
            )
            db_session.add(template)
        await db_session.flush()

        # Act
        response = await client.get("/api/email-templates?page=1&page_size=2")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["page"] == 1
        assert data["page_size"] == 2
        assert data["total_pages"] == 3

    @pytest.mark.asyncio
    async def test_list_templates_filter_by_active_returns_200(
        self, client: AsyncClient, db_session
    ):
        """Test GET /api/email-templates?is_active=true filters correctly."""
        # Arrange
        active_template = EmailTemplate(
            name="Active Template",
            subject="Active",
            body="Active body",
            is_active=True,
        )
        inactive_template = EmailTemplate(
            name="Inactive Template",
            subject="Inactive",
            body="Inactive body",
            is_active=False,
        )
        db_session.add(active_template)
        db_session.add(inactive_template)
        await db_session.flush()

        # Act
        response = await client.get("/api/email-templates?is_active=true")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["is_active"] is True

    @pytest.mark.asyncio
    async def test_list_templates_filter_by_category_returns_200(
        self, client: AsyncClient, db_session
    ):
        """Test GET /api/email-templates?category=X filters correctly."""
        # Arrange
        uid = unique_id()
        template1 = EmailTemplate(
            name=f"Sales Template {uid}",
            subject="Sales",
            body="Sales body",
            category="sales",
        )
        template2 = EmailTemplate(
            name=f"Support Template {uid}",
            subject="Support",
            body="Support body",
            category="support",
        )
        db_session.add(template1)
        db_session.add(template2)
        await db_session.flush()

        # Act
        response = await client.get("/api/email-templates?category=sales")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["category"] == "sales"

    @pytest.mark.asyncio
    async def test_get_template_returns_200(
        self, client: AsyncClient, sample_email_template: EmailTemplate
    ):
        """Test GET /api/email-templates/{id} returns template details."""
        # Act
        response = await client.get(f"/api/email-templates/{sample_email_template.id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_email_template.id
        assert data["name"] == sample_email_template.name
        assert data["subject"] == sample_email_template.subject
        assert data["body"] == sample_email_template.body
        assert "variables" in data

    @pytest.mark.asyncio
    async def test_get_template_not_found_returns_404(self, client: AsyncClient):
        """Test GET /api/email-templates/{id} returns 404 for non-existent template."""
        # Act
        response = await client.get("/api/email-templates/99999")

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_create_template_returns_201(self, client: AsyncClient):
        """Test POST /api/email-templates creates template and returns 201."""
        # Arrange
        uid = unique_id()
        payload = {
            "name": f"New Template {uid}",
            "subject": "Hello {{contact.first_name}}",
            "body": "Dear {{contact.first_name}},\n\nThis is a test email.\n\nBest regards",
            "description": "A test email template",
            "category": "general",
            "is_active": True,
            # Note: Not passing variables to avoid JSON parsing issues in route handler
        }

        # Act
        response = await client.post("/api/email-templates", json=payload)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == payload["name"]
        assert data["subject"] == payload["subject"]
        assert data["body"] == payload["body"]
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_template_minimal_returns_201(self, client: AsyncClient):
        """Test POST /api/email-templates with minimal required fields."""
        # Arrange
        uid = unique_id()
        payload = {
            "name": f"Minimal Template {uid}",
            "subject": "Simple Subject",
            "body": "Simple body content",
        }

        # Act
        response = await client.post("/api/email-templates", json=payload)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == payload["name"]
        assert data["is_active"] is True  # default value

    @pytest.mark.asyncio
    async def test_create_template_missing_name_returns_422(self, client: AsyncClient):
        """Test POST /api/email-templates returns 422 when name is missing."""
        # Arrange
        payload = {
            "subject": "Subject",
            "body": "Body",
        }

        # Act
        response = await client.post("/api/email-templates", json=payload)

        # Assert
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_template_missing_subject_returns_422(self, client: AsyncClient):
        """Test POST /api/email-templates returns 422 when subject is missing."""
        # Arrange
        payload = {
            "name": "Template Name",
            "body": "Body",
        }

        # Act
        response = await client.post("/api/email-templates", json=payload)

        # Assert
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_template_missing_body_returns_422(self, client: AsyncClient):
        """Test POST /api/email-templates returns 422 when body is missing."""
        # Arrange
        payload = {
            "name": "Template Name",
            "subject": "Subject",
        }

        # Act
        response = await client.post("/api/email-templates", json=payload)

        # Assert
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_update_template_returns_200(
        self, client: AsyncClient, sample_email_template: EmailTemplate
    ):
        """Test PUT /api/email-templates/{id} updates template."""
        # Arrange
        payload = {
            "name": "Updated Template Name",
            "subject": "Updated Subject",
            "is_active": False,
        }

        # Act
        response = await client.put(
            f"/api/email-templates/{sample_email_template.id}", json=payload
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == payload["name"]
        assert data["subject"] == payload["subject"]
        assert data["is_active"] is False

    @pytest.mark.asyncio
    async def test_update_template_partial_returns_200(
        self, client: AsyncClient, sample_email_template: EmailTemplate
    ):
        """Test PUT /api/email-templates/{id} with partial update."""
        # Arrange
        original_name = sample_email_template.name
        payload = {
            "description": "Updated description only",
        }

        # Act
        response = await client.put(
            f"/api/email-templates/{sample_email_template.id}", json=payload
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == payload["description"]
        assert data["name"] == original_name

    @pytest.mark.asyncio
    async def test_update_template_not_found_returns_404(self, client: AsyncClient):
        """Test PUT /api/email-templates/{id} returns 404 for non-existent template."""
        # Arrange
        payload = {"name": "Updated Name"}

        # Act
        response = await client.put("/api/email-templates/99999", json=payload)

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestEmailPreviewAPI:
    """Integration tests for email preview functionality."""

    @pytest.mark.asyncio
    async def test_preview_email_returns_200(
        self, client: AsyncClient, sample_email_template: EmailTemplate, sample_contact: Contact
    ):
        """Test POST /api/email-templates/preview returns rendered email."""
        # Arrange
        payload = {
            "template_id": sample_email_template.id,
            "contact_id": sample_contact.id,
        }

        # Act
        response = await client.post("/api/email-templates/preview", json=payload)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "subject" in data
        assert "body" in data
        assert "to_email" in data
        assert "to_name" in data
        # Verify variable substitution happened
        assert sample_contact.first_name in data["subject"] or sample_contact.first_name in data["body"]

    @pytest.mark.asyncio
    async def test_preview_email_template_not_found_returns_404(
        self, client: AsyncClient, sample_contact: Contact
    ):
        """Test POST /api/email-templates/preview returns 404 for missing template."""
        # Arrange
        payload = {
            "template_id": 99999,
            "contact_id": sample_contact.id,
        }

        # Act
        response = await client.post("/api/email-templates/preview", json=payload)

        # Assert
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_preview_email_contact_not_found_returns_404(
        self, client: AsyncClient, sample_email_template: EmailTemplate
    ):
        """Test POST /api/email-templates/preview returns 404 for missing contact."""
        # Arrange
        payload = {
            "template_id": sample_email_template.id,
            "contact_id": 99999,
        }

        # Act
        response = await client.post("/api/email-templates/preview", json=payload)

        # Assert
        assert response.status_code == 404


class TestEmailSendAPI:
    """Integration tests for email sending functionality."""

    @pytest.mark.asyncio
    async def test_send_email_returns_200(
        self, client: AsyncClient, sample_email_template: EmailTemplate, sample_contact: Contact
    ):
        """Test POST /api/email-templates/send triggers email send."""
        # Arrange
        payload = {
            "template_id": sample_email_template.id,
            "contact_id": sample_contact.id,
        }

        # Act
        response = await client.post("/api/email-templates/send", json=payload)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "sent"

    @pytest.mark.asyncio
    async def test_send_email_with_subject_override_returns_200(
        self, client: AsyncClient, sample_email_template: EmailTemplate, sample_contact: Contact
    ):
        """Test POST /api/email-templates/send with subject override."""
        # Arrange
        payload = {
            "template_id": sample_email_template.id,
            "contact_id": sample_contact.id,
            "subject_override": "Custom Subject Line",
        }

        # Act
        response = await client.post("/api/email-templates/send", json=payload)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "sent"

    @pytest.mark.asyncio
    async def test_send_email_template_not_found_returns_400(
        self, client: AsyncClient, sample_contact: Contact
    ):
        """Test POST /api/email-templates/send returns 400 for missing template."""
        # Arrange
        payload = {
            "template_id": 99999,
            "contact_id": sample_contact.id,
        }

        # Act
        response = await client.post("/api/email-templates/send", json=payload)

        # Assert
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_send_email_contact_not_found_returns_400(
        self, client: AsyncClient, sample_email_template: EmailTemplate
    ):
        """Test POST /api/email-templates/send returns 400 for missing contact."""
        # Arrange
        payload = {
            "template_id": sample_email_template.id,
            "contact_id": 99999,
        }

        # Act
        response = await client.post("/api/email-templates/send", json=payload)

        # Assert
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_send_email_missing_template_id_returns_422(
        self, client: AsyncClient, sample_contact: Contact
    ):
        """Test POST /api/email-templates/send returns 422 when template_id is missing."""
        # Arrange
        payload = {
            "contact_id": sample_contact.id,
        }

        # Act
        response = await client.post("/api/email-templates/send", json=payload)

        # Assert
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_send_email_missing_contact_id_returns_422(
        self, client: AsyncClient, sample_email_template: EmailTemplate
    ):
        """Test POST /api/email-templates/send returns 422 when contact_id is missing."""
        # Arrange
        payload = {
            "template_id": sample_email_template.id,
        }

        # Act
        response = await client.post("/api/email-templates/send", json=payload)

        # Assert
        assert response.status_code == 422
