import pytest
from src.models.lead import Lead, LeadStatus


class TestLeadStatus:
    def test_status_values(self):
        assert LeadStatus.COLD.value == "cold"
        assert LeadStatus.WARM.value == "warm"
        assert LeadStatus.HOT.value == "hot"
        assert LeadStatus.TO_BE_DONE.value == "to_be_done"
        assert LeadStatus.DISQUALIFIED.value == "disqualified"

    def test_status_count(self):
        assert len(LeadStatus) == 5

    def test_status_is_string_enum(self):
        assert isinstance(LeadStatus.COLD.value, str)
        assert str(LeadStatus.COLD) == "LeadStatus.COLD"


class TestLeadModel:
    @pytest.mark.asyncio
    async def test_lead_creation(self, db_session, sample_contact):
        lead = Lead(
            contact_id=sample_contact.id,
            status=LeadStatus.COLD,
            source="test",
        )
        db_session.add(lead)
        await db_session.flush()
        
        assert lead.id is not None
        assert lead.status == LeadStatus.COLD
        assert lead.source == "test"
        assert lead.contact_id == sample_contact.id

    @pytest.mark.asyncio
    async def test_lead_default_status(self, db_session, sample_contact):
        lead = Lead(contact_id=sample_contact.id)
        db_session.add(lead)
        await db_session.flush()
        
        assert lead.status == LeadStatus.COLD

    @pytest.mark.asyncio
    async def test_lead_with_campaign(self, db_session, sample_contact, sample_campaign):
        lead = Lead(
            contact_id=sample_contact.id,
            campaign_id=sample_campaign.id,
        )
        db_session.add(lead)
        await db_session.flush()
        
        assert lead.campaign_id == sample_campaign.id

    @pytest.mark.asyncio
    async def test_lead_repr(self, sample_lead):
        repr_str = repr(sample_lead)
        assert "Lead" in repr_str
        assert str(sample_lead.id) in repr_str
        assert "cold" in repr_str
