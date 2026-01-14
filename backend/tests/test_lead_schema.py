import pytest
from pydantic import ValidationError

from src.models.lead import LeadStatus
from src.schemas.lead import (
    LeadCreate,
    LeadUpdate,
    LeadCreateFromForm,
    LeadImportResult,
    LeadResponse,
    LeadListResponse,
)


class TestLeadCreate:
    def test_valid_lead_create(self):
        data = LeadCreate(contact_id=1, status=LeadStatus.WARM)
        assert data.contact_id == 1
        assert data.status == LeadStatus.WARM

    def test_default_status(self):
        data = LeadCreate(contact_id=1)
        assert data.status == LeadStatus.COLD

    def test_with_campaign(self):
        data = LeadCreate(contact_id=1, campaign_id=5)
        assert data.campaign_id == 5

    def test_with_source(self):
        data = LeadCreate(contact_id=1, source="website")
        assert data.source == "website"

    def test_missing_contact_id(self):
        with pytest.raises(ValidationError):
            LeadCreate()


class TestLeadUpdate:
    def test_partial_update(self):
        data = LeadUpdate(status=LeadStatus.HOT)
        assert data.status == LeadStatus.HOT
        assert data.source is None

    def test_empty_update(self):
        data = LeadUpdate()
        assert data.status is None
        assert data.notes is None


class TestLeadCreateFromForm:
    def test_valid_form(self):
        data = LeadCreateFromForm(
            first_name="Max",
            last_name="Mustermann",
            email="max@test.com",
        )
        assert data.first_name == "Max"
        assert data.email == "max@test.com"

    def test_with_optional_fields(self):
        data = LeadCreateFromForm(
            first_name="Max",
            last_name="Mustermann",
            email="max@test.com",
            phone="+43 123",
            company_name="Test GmbH",
            utm_source="google",
        )
        assert data.phone == "+43 123"
        assert data.company_name == "Test GmbH"
        assert data.utm_source == "google"

    def test_invalid_email(self):
        with pytest.raises(ValidationError):
            LeadCreateFromForm(
                first_name="Max",
                last_name="Mustermann",
                email="invalid",
            )

    def test_empty_name(self):
        with pytest.raises(ValidationError):
            LeadCreateFromForm(
                first_name="",
                last_name="Mustermann",
                email="max@test.com",
            )


class TestLeadImportResult:
    def test_import_result(self):
        result = LeadImportResult(
            total_rows=100,
            imported=95,
            failed=5,
            errors=["Row 5: Missing name"],
        )
        assert result.total_rows == 100
        assert result.imported == 95
        assert result.failed == 5
        assert len(result.errors) == 1


class TestLeadListResponse:
    def test_list_response(self):
        from datetime import datetime
        
        data = LeadListResponse(
            id=1,
            status=LeadStatus.WARM,
            contact_id=1,
            contact_name="Max Mustermann",
            contact_email="max@test.com",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        assert data.id == 1
        assert data.contact_name == "Max Mustermann"
        assert data.status == LeadStatus.WARM
