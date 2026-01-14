"""
Tests for Contact Service.
"""
import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.contact import Contact
from src.models.company import Company
from src.schemas.contact import ContactCreate, ContactUpdate
from src.services import contact_service


class TestGetContacts:
    """Tests for get_contacts function."""

    @pytest.mark.asyncio
    async def test_get_contacts_empty(self, db_session: AsyncSession):
        """Test getting contacts when none exist."""
        contacts, total = await contact_service.get_contacts(db_session)
        assert contacts == []
        assert total == 0

    @pytest.mark.asyncio
    async def test_get_contacts_with_data(
        self, db_session: AsyncSession, sample_contact: Contact
    ):
        """Test getting contacts with existing data."""
        contacts, total = await contact_service.get_contacts(db_session)
        assert len(contacts) == 1
        assert total == 1
        assert contacts[0].id == sample_contact.id

    @pytest.mark.asyncio
    async def test_get_contacts_pagination(
        self, db_session: AsyncSession, multiple_contacts: list[Contact]
    ):
        """Test contacts pagination."""
        # Get first page (2 items)
        contacts, total = await contact_service.get_contacts(db_session, skip=0, limit=2)
        assert len(contacts) == 2
        assert total == 5

        # Get second page
        contacts, total = await contact_service.get_contacts(db_session, skip=2, limit=2)
        assert len(contacts) == 2
        assert total == 5

    @pytest.mark.asyncio
    async def test_get_contacts_search_by_name(
        self, db_session: AsyncSession, multiple_contacts: list[Contact]
    ):
        """Test searching contacts by name."""
        contacts, total = await contact_service.get_contacts(
            db_session, search="Anna"
        )
        assert total == 1
        assert contacts[0].first_name == "Anna"

    @pytest.mark.asyncio
    async def test_get_contacts_search_by_email(
        self, db_session: AsyncSession, multiple_contacts: list[Contact]
    ):
        """Test searching contacts by email."""
        contacts, total = await contact_service.get_contacts(
            db_session, search="peter.wagner"
        )
        assert total == 1
        assert contacts[0].first_name == "Peter"

    @pytest.mark.asyncio
    async def test_get_contacts_filter_by_company(
        self, db_session: AsyncSession, multiple_contacts: list[Contact], sample_company: Company
    ):
        """Test filtering contacts by company."""
        contacts, total = await contact_service.get_contacts(
            db_session, company_id=sample_company.id
        )
        # Anna and Peter have sample_company
        assert total == 2

    @pytest.mark.asyncio
    async def test_get_contacts_filter_by_active(
        self, db_session: AsyncSession, multiple_contacts: list[Contact]
    ):
        """Test filtering contacts by active status."""
        # Get only active contacts
        contacts, total = await contact_service.get_contacts(
            db_session, is_active=True
        )
        assert total == 4  # Thomas is inactive
        
        # Get only inactive contacts
        contacts, total = await contact_service.get_contacts(
            db_session, is_active=False
        )
        assert total == 1
        assert contacts[0].first_name == "Thomas"


class TestSearchContacts:
    """Tests for search_contacts function (autocomplete)."""

    @pytest.mark.asyncio
    async def test_search_contacts_empty_query(self, db_session: AsyncSession):
        """Test search with empty query returns empty list."""
        results = await contact_service.search_contacts(db_session, "")
        assert results == []

    @pytest.mark.asyncio
    async def test_search_contacts_short_query(self, db_session: AsyncSession):
        """Test search with query less than 2 chars returns empty list."""
        results = await contact_service.search_contacts(db_session, "A")
        assert results == []

    @pytest.mark.asyncio
    async def test_search_contacts_by_first_name(
        self, db_session: AsyncSession, multiple_contacts: list[Contact]
    ):
        """Test searching contacts by first name."""
        results = await contact_service.search_contacts(db_session, "Anna")
        assert len(results) == 1
        assert "Anna" in results[0].full_name

    @pytest.mark.asyncio
    async def test_search_contacts_by_last_name(
        self, db_session: AsyncSession, multiple_contacts: list[Contact]
    ):
        """Test searching contacts by last name."""
        results = await contact_service.search_contacts(db_session, "Schmidt")
        assert len(results) == 1
        assert "Schmidt" in results[0].full_name

    @pytest.mark.asyncio
    async def test_search_contacts_by_email(
        self, db_session: AsyncSession, multiple_contacts: list[Contact]
    ):
        """Test searching contacts by email."""
        results = await contact_service.search_contacts(db_session, "peter.wagner@test")
        assert len(results) == 1
        assert "peter.wagner" in results[0].email

    @pytest.mark.asyncio
    async def test_search_contacts_by_company(
        self, db_session: AsyncSession, multiple_contacts: list[Contact], sample_company: Company
    ):
        """Test searching contacts by company name."""
        results = await contact_service.search_contacts(db_session, "Test GmbH")
        assert len(results) == 2  # Anna and Peter

    @pytest.mark.asyncio
    async def test_search_contacts_excludes_inactive(
        self, db_session: AsyncSession, multiple_contacts: list[Contact]
    ):
        """Test that search excludes inactive contacts."""
        results = await contact_service.search_contacts(db_session, "Maier")
        assert len(results) == 0  # Thomas is inactive

    @pytest.mark.asyncio
    async def test_search_contacts_limit(
        self, db_session: AsyncSession, multiple_contacts: list[Contact]
    ):
        """Test search results limit."""
        results = await contact_service.search_contacts(db_session, "test.at", limit=2)
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_search_contacts_includes_title(
        self, db_session: AsyncSession, multiple_contacts: list[Contact]
    ):
        """Test that search results include title in full_name."""
        results = await contact_service.search_contacts(db_session, "Berger")
        assert len(results) == 1
        assert "Dr." in results[0].full_name


class TestGetContact:
    """Tests for get_contact function."""

    @pytest.mark.asyncio
    async def test_get_contact_exists(
        self, db_session: AsyncSession, sample_contact: Contact
    ):
        """Test getting an existing contact."""
        contact = await contact_service.get_contact(db_session, sample_contact.id)
        assert contact is not None
        assert contact.id == sample_contact.id
        assert contact.company is not None

    @pytest.mark.asyncio
    async def test_get_contact_not_exists(self, db_session: AsyncSession):
        """Test getting a non-existent contact."""
        contact = await contact_service.get_contact(db_session, 99999)
        assert contact is None


class TestCreateContact:
    """Tests for create_contact function."""

    @pytest.mark.asyncio
    async def test_create_contact_minimal(self, db_session: AsyncSession):
        """Test creating a contact with minimal data."""
        contact_data = ContactCreate(
            first_name="Test",
            last_name="User",
        )
        contact = await contact_service.create_contact(db_session, contact_data)
        
        assert contact.id is not None
        assert contact.first_name == "Test"
        assert contact.last_name == "User"
        assert contact.is_active is True

    @pytest.mark.asyncio
    async def test_create_contact_full(
        self, db_session: AsyncSession, sample_company: Company
    ):
        """Test creating a contact with full data."""
        contact_data = ContactCreate(
            first_name="Klaus",
            last_name="Weber",
            email="klaus.weber@test.at",
            phone="+43 1 1111111",
            mobile="+43 664 2222222",
            position="Abteilungsleiter",
            department="Vertrieb",
            salutation="Herr",
            title="Dr.",
            notes="Wichtiger Kontakt",
            is_primary=True,
            company_id=sample_company.id,
        )
        contact = await contact_service.create_contact(db_session, contact_data)
        
        assert contact.id is not None
        assert contact.email == "klaus.weber@test.at"
        assert contact.title == "Dr."
        assert contact.company_id == sample_company.id


class TestUpdateContact:
    """Tests for update_contact function."""

    @pytest.mark.asyncio
    async def test_update_contact_success(
        self, db_session: AsyncSession, sample_contact: Contact
    ):
        """Test updating a contact successfully."""
        update_data = ContactUpdate(
            position="CEO",
            notes="Befördert",
        )
        contact = await contact_service.update_contact(
            db_session, sample_contact.id, update_data
        )
        
        assert contact is not None
        assert contact.position == "CEO"
        assert contact.notes == "Befördert"
        # Other fields should remain unchanged
        assert contact.first_name == sample_contact.first_name

    @pytest.mark.asyncio
    async def test_update_contact_not_exists(self, db_session: AsyncSession):
        """Test updating a non-existent contact."""
        update_data = ContactUpdate(position="Manager")
        contact = await contact_service.update_contact(db_session, 99999, update_data)
        assert contact is None

    @pytest.mark.asyncio
    async def test_update_contact_partial(
        self, db_session: AsyncSession, sample_contact: Contact
    ):
        """Test partial update (only specified fields)."""
        original_email = sample_contact.email
        update_data = ContactUpdate(phone="+43 1 9999999")
        
        contact = await contact_service.update_contact(
            db_session, sample_contact.id, update_data
        )
        
        assert contact.phone == "+43 1 9999999"
        assert contact.email == original_email  # Unchanged


class TestDeleteContact:
    """Tests for delete_contact function (soft delete)."""

    @pytest.mark.asyncio
    async def test_delete_contact_success(
        self, db_session: AsyncSession, sample_contact: Contact
    ):
        """Test soft deleting a contact."""
        result = await contact_service.delete_contact(db_session, sample_contact.id)
        assert result is True
        
        # Contact should still exist but be inactive
        contact = await contact_service.get_contact(db_session, sample_contact.id)
        assert contact is not None
        assert contact.is_active is False

    @pytest.mark.asyncio
    async def test_delete_contact_not_exists(self, db_session: AsyncSession):
        """Test deleting a non-existent contact."""
        result = await contact_service.delete_contact(db_session, 99999)
        assert result is False


class TestGetOrCreateContactByEmail:
    """Tests for get_or_create_contact_by_email function."""

    @pytest.mark.asyncio
    async def test_get_existing_contact(
        self, db_session: AsyncSession, sample_contact: Contact
    ):
        """Test getting existing contact by email."""
        contact, is_new = await contact_service.get_or_create_contact_by_email(
            db_session,
            email=sample_contact.email,
            first_name="Neuer",
            last_name="Name",
        )
        
        assert is_new is False
        assert contact.id == sample_contact.id
        # Original name should be preserved
        assert contact.first_name == sample_contact.first_name

    @pytest.mark.asyncio
    async def test_create_new_contact(self, db_session: AsyncSession):
        """Test creating new contact when email doesn't exist."""
        contact, is_new = await contact_service.get_or_create_contact_by_email(
            db_session,
            email="new.user@test.at",
            first_name="Neuer",
            last_name="Benutzer",
            phone="+43 1 5555555",
        )
        
        assert is_new is True
        assert contact.email == "new.user@test.at"
        assert contact.first_name == "Neuer"
        assert contact.phone == "+43 1 5555555"

    @pytest.mark.asyncio
    async def test_create_with_company(
        self, db_session: AsyncSession, sample_company: Company
    ):
        """Test creating new contact with company."""
        contact, is_new = await contact_service.get_or_create_contact_by_email(
            db_session,
            email="company.user@test.at",
            first_name="Firma",
            last_name="User",
            company_id=sample_company.id,
        )
        
        assert is_new is True
        assert contact.company_id == sample_company.id
