"""Tests for Lead Service."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.lead import Lead, LeadStatus
from src.models.contact import Contact
from src.models.campaign import Campaign
from src.models.contact_history import ContactHistory, HistoryType
from src.schemas.lead import LeadCreate, LeadUpdate
from src.services import lead_service


class TestGetLeads:
    @pytest.mark.asyncio
    async def test_get_leads_empty(self, db_session: AsyncSession):
        leads, total = await lead_service.get_leads(db_session)
        assert leads == []
        assert total == 0

    @pytest.mark.asyncio
    async def test_get_leads_with_data(
        self, db_session: AsyncSession, sample_lead: Lead
    ):
        leads, total = await lead_service.get_leads(db_session)
        assert len(leads) == 1
        assert total == 1
        assert leads[0].id == sample_lead.id

    @pytest.mark.asyncio
    async def test_get_leads_pagination(
        self, db_session: AsyncSession, multiple_leads: list[Lead]
    ):
        leads, total = await lead_service.get_leads(db_session, skip=0, limit=2)
        assert len(leads) == 2
        assert total == 5

        leads, total = await lead_service.get_leads(db_session, skip=2, limit=2)
        assert len(leads) == 2
        assert total == 5

        leads, total = await lead_service.get_leads(db_session, skip=4, limit=2)
        assert len(leads) == 1
        assert total == 5

    @pytest.mark.asyncio
    async def test_get_leads_filter_by_status(
        self, db_session: AsyncSession, multiple_leads: list[Lead]
    ):
        leads, total = await lead_service.get_leads(
            db_session, status=LeadStatus.COLD
        )
        assert total == 2
        for lead in leads:
            assert lead.status == LeadStatus.COLD

    @pytest.mark.asyncio
    async def test_get_leads_filter_by_campaign(
        self, db_session: AsyncSession, multiple_leads: list[Lead], sample_campaign: Campaign
    ):
        leads, total = await lead_service.get_leads(
            db_session, campaign_id=sample_campaign.id
        )
        assert total == 3
        for lead in leads:
            assert lead.campaign_id == sample_campaign.id


class TestGetLead:
    @pytest.mark.asyncio
    async def test_get_lead_exists(
        self, db_session: AsyncSession, sample_lead: Lead
    ):
        lead = await lead_service.get_lead(db_session, sample_lead.id)
        assert lead is not None
        assert lead.id == sample_lead.id
        assert lead.contact is not None
        assert lead.campaign is not None

    @pytest.mark.asyncio
    async def test_get_lead_not_exists(self, db_session: AsyncSession):
        lead = await lead_service.get_lead(db_session, 99999)
        assert lead is None


class TestCreateLead:
    @pytest.mark.asyncio
    async def test_create_lead_success(
        self, db_session: AsyncSession, sample_contact: Contact, sample_campaign: Campaign
    ):
        lead_data = LeadCreate(
            contact_id=sample_contact.id,
            campaign_id=sample_campaign.id,
            status=LeadStatus.COLD,
            source="manual",
            utm_source="test",
        )
        lead = await lead_service.create_lead(db_session, lead_data)
        
        assert lead.id is not None
        assert lead.contact_id == sample_contact.id
        assert lead.campaign_id == sample_campaign.id
        assert lead.status == LeadStatus.COLD
        assert lead.source == "manual"

    @pytest.mark.asyncio
    async def test_create_lead_creates_history_entry(
        self, db_session: AsyncSession, sample_contact: Contact
    ):
        lead_data = LeadCreate(
            contact_id=sample_contact.id,
            status=LeadStatus.WARM,
            source="landing_page",
        )
        lead = await lead_service.create_lead(db_session, lead_data)
        await db_session.commit()
        
        result = await db_session.execute(
            select(ContactHistory).where(
                ContactHistory.contact_id == sample_contact.id,
                ContactHistory.type == HistoryType.LEAD_CREATED,
            )
        )
        history = result.scalar_one_or_none()
        assert history is not None
        assert "Lead" in history.title


class TestUpdateLead:
    @pytest.mark.asyncio
    async def test_update_lead_success(
        self, db_session: AsyncSession, sample_lead: Lead
    ):
        update_data = LeadUpdate(
            status=LeadStatus.WARM,
            notes="Erstkontakt durchgeführt",
        )
        lead = await lead_service.update_lead(db_session, sample_lead.id, update_data)
        
        assert lead is not None
        assert lead.status == LeadStatus.WARM
        assert lead.notes == "Erstkontakt durchgeführt"

    @pytest.mark.asyncio
    async def test_update_lead_not_exists(self, db_session: AsyncSession):
        update_data = LeadUpdate(status=LeadStatus.HOT)
        lead = await lead_service.update_lead(db_session, 99999, update_data)
        assert lead is None

    @pytest.mark.asyncio
    async def test_update_lead_status_creates_history(
        self, db_session: AsyncSession, sample_lead: Lead
    ):
        update_data = LeadUpdate(status=LeadStatus.HOT)
        
        lead = await lead_service.update_lead(db_session, sample_lead.id, update_data)
        await db_session.commit()
        
        result = await db_session.execute(
            select(ContactHistory).where(
                ContactHistory.contact_id == sample_lead.contact_id,
                ContactHistory.type == HistoryType.STATUS_CHANGE,
            )
        )
        history = result.scalar_one_or_none()
        assert history is not None
        assert "Status" in history.title


class TestImportLeadsFromFile:
    @pytest.mark.asyncio
    async def test_import_csv_success(
        self, db_session: AsyncSession, sample_campaign: Campaign
    ):
        csv_content = b"vorname,nachname,email,telefon,firma\nHans,Gruber,hans@test.at,+43123456,TestFirma\nKlara,Klein,klara@test.at,+43654321,\n"
        
        result = await lead_service.import_leads_from_file(
            db_session, csv_content, "test.csv", sample_campaign.id
        )
        
        assert result.total_rows == 2
        assert result.imported == 2
        assert result.failed == 0
        assert len(result.errors) == 0

    @pytest.mark.asyncio
    async def test_import_csv_missing_column(self, db_session: AsyncSession):
        csv_content = b"email,telefon\ntest@test.at,123456\n"
        
        result = await lead_service.import_leads_from_file(
            db_session, csv_content, "test.csv"
        )
        
        assert result.imported == 0

    @pytest.mark.asyncio
    async def test_import_csv_with_english_columns(self, db_session: AsyncSession):
        csv_content = b"first_name,last_name,email\nJohn,Doe,john@test.at\n"
        
        result = await lead_service.import_leads_from_file(
            db_session, csv_content, "test.csv"
        )
        
        assert result.imported == 1
        assert result.failed == 0

    @pytest.mark.asyncio
    async def test_import_invalid_file_format(self, db_session: AsyncSession):
        result = await lead_service.import_leads_from_file(
            db_session, b"some content", "test.txt"
        )
        
        assert result.imported == 0

    @pytest.mark.asyncio
    async def test_import_creates_company(
        self, db_session: AsyncSession
    ):
        csv_content = b"vorname,nachname,email,firma\nMax,Mustermann,max@test.at,Neue Firma GmbH\n"
        
        result = await lead_service.import_leads_from_file(
            db_session, csv_content, "test.csv"
        )
        
        assert result.imported == 1
        
        from src.models.company import Company
        company_result = await db_session.execute(
            select(Company).where(Company.name == "Neue Firma GmbH")
        )
        company = company_result.scalar_one_or_none()
        assert company is not None

    @pytest.mark.asyncio
    async def test_import_reuses_existing_contact(
        self, db_session: AsyncSession, sample_contact: Contact
    ):
        csv_content = f"vorname,nachname,email\nNeuer,Name,{sample_contact.email}\n".encode()
        
        result = await lead_service.import_leads_from_file(
            db_session, csv_content, "test.csv"
        )
        
        assert result.imported == 1
        
        from sqlalchemy import func
        count_result = await db_session.execute(
            select(func.count(Contact.id)).where(Contact.email == sample_contact.email)
        )
        count = count_result.scalar()
        assert count == 1
