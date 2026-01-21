"""Unit tests for contact_service."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.services import contact_service
from src.schemas.contact import ContactCreate, ContactUpdate
from src.models.contact import Contact

class TestContactService:
    """Unit tests for contact service functions."""

    @pytest.mark.unit
    async def test_should_get_contacts_with_pagination(self, mock_db, mock_query_result):
        # Arrange
        mock_contacts = [
            Contact(id=1, first_name="John", last_name="Doe", email="john@test.com"),
            Contact(id=2, first_name="Jane", last_name="Smith", email="jane@test.com"),
        ]
        mock_query_result.scalars = MagicMock(return_value=MagicMock(all=MagicMock(return_value=mock_contacts)))
        
        mock_count_result = MagicMock()
        mock_count_result.scalar = MagicMock(return_value=2)
        
        mock_db.execute = AsyncMock(side_effect=[mock_query_result, mock_count_result])
        
        # Act
        contacts, total = await contact_service.get_contacts(mock_db, skip=0, limit=20)
        
        # Assert
        assert len(contacts) == 2
        assert total == 2
        assert mock_db.execute.call_count == 2

    @pytest.mark.unit
    async def test_should_filter_contacts_by_search_query(self, mock_db, mock_query_result):
        # Arrange
        mock_contacts = [Contact(id=1, first_name="John", last_name="Doe", email="john@test.com")]
        mock_query_result.scalars = MagicMock(return_value=MagicMock(all=MagicMock(return_value=mock_contacts)))
        
        mock_count_result = MagicMock()
        mock_count_result.scalar = MagicMock(return_value=1)
        
        mock_db.execute = AsyncMock(side_effect=[mock_query_result, mock_count_result])
        
        # Act
        contacts, total = await contact_service.get_contacts(mock_db, search="John")
        
        # Assert
        assert len(contacts) == 1
        assert total == 1

    @pytest.mark.unit
    async def test_should_get_contact_by_id(self, mock_db):
        # Arrange
        expected_contact = Contact(id=1, first_name="John", last_name="Doe", email="john@test.com")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=expected_contact)
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        # Act
        contact = await contact_service.get_contact(mock_db, contact_id=1)
        
        # Assert
        assert contact is not None
        assert contact.id == 1
        assert contact.first_name == "John"

    @pytest.mark.unit
    async def test_should_return_none_when_contact_not_found(self, mock_db):
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        # Act
        contact = await contact_service.get_contact(mock_db, contact_id=999)
        
        # Assert
        assert contact is None

    @pytest.mark.unit
    async def test_should_create_contact(self, mock_db):
        # Arrange
        contact_data = ContactCreate(
            first_name="John",
            last_name="Doe",
            email="john@test.com"
        )
        
        # Act
        result = await contact_service.create_contact(mock_db, contact_data)
        
        # Assert
        mock_db.add.assert_called_once()
        mock_db.flush.assert_awaited_once()
        mock_db.refresh.assert_awaited_once()

    @pytest.mark.unit
    async def test_should_update_contact_fields(self, mock_db):
        # Arrange
        existing_contact = Contact(id=1, first_name="John", last_name="Doe", email="john@test.com")
        update_data = ContactUpdate(first_name="Jane")
        
        with patch('src.services.contact_service.get_contact', AsyncMock(return_value=existing_contact)):
            # Act
            result = await contact_service.update_contact(mock_db, contact_id=1, contact_data=update_data)
        
        # Assert
        assert result is not None
        assert result.first_name == "Jane"
        mock_db.flush.assert_awaited()

    @pytest.mark.unit
    async def test_should_return_none_when_updating_nonexistent_contact(self, mock_db):
        # Arrange
        update_data = ContactUpdate(first_name="Jane")
        
        with patch('src.services.contact_service.get_contact', AsyncMock(return_value=None)):
            # Act
            result = await contact_service.update_contact(mock_db, contact_id=999, contact_data=update_data)
        
        # Assert
        assert result is None

    @pytest.mark.unit
    async def test_should_soft_delete_contact(self, mock_db):
        # Arrange
        existing_contact = Contact(id=1, first_name="John", last_name="Doe", email="john@test.com", is_active=True)
        
        with patch('src.services.contact_service.get_contact', AsyncMock(return_value=existing_contact)):
            # Act
            result = await contact_service.delete_contact(mock_db, contact_id=1)
        
        # Assert
        assert result is True
        assert existing_contact.is_active is False
        mock_db.flush.assert_awaited()

    @pytest.mark.unit
    async def test_should_return_false_when_deleting_nonexistent_contact(self, mock_db):
        # Arrange
        with patch('src.services.contact_service.get_contact', AsyncMock(return_value=None)):
            # Act
            result = await contact_service.delete_contact(mock_db, contact_id=999)
        
        # Assert
        assert result is False

    @pytest.mark.unit
    async def test_should_return_existing_contact_by_email(self, mock_db):
        # Arrange
        existing_contact = Contact(id=1, first_name="John", last_name="Doe", email="john@test.com")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=existing_contact)
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        # Act
        contact, created = await contact_service.get_or_create_contact_by_email(
            mock_db, email="john@test.com", first_name="John", last_name="Doe"
        )
        
        # Assert
        assert contact is not None
        assert created is False
        assert contact.email == "john@test.com"
        mock_db.add.assert_not_called()

    @pytest.mark.unit
    async def test_should_create_new_contact_when_email_not_found(self, mock_db):
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        # Act
        contact, created = await contact_service.get_or_create_contact_by_email(
            mock_db, email="new@test.com", first_name="New", last_name="Person"
        )
        
        # Assert
        assert created is True
        mock_db.add.assert_called_once()
        mock_db.flush.assert_awaited()

    @pytest.mark.unit
    async def test_should_return_empty_list_for_short_search_query(self, mock_db):
        # Arrange - query too short
        
        # Act
        results = await contact_service.search_contacts(mock_db, query="a", limit=10)
        
        # Assert
        assert results == []
        mock_db.execute.assert_not_called()

    @pytest.mark.unit
    async def test_should_search_contacts_with_valid_query(self, mock_db):
        # Arrange
        mock_row = MagicMock()
        mock_row.id = 1
        mock_row.first_name = "John"
        mock_row.last_name = "Doe"
        mock_row.email = "john@test.com"
        mock_row.title = "Dr."
        mock_row.company_name = "Test Corp"
        
        mock_result = MagicMock()
        mock_result.all = MagicMock(return_value=[mock_row])
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        # Act
        results = await contact_service.search_contacts(mock_db, query="John", limit=10)
        
        # Assert
        assert len(results) == 1
        assert results[0].full_name == "Dr. John Doe"
        assert results[0].email == "john@test.com"
