"""Unit tests for lead_service."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.services import lead_service
from src.schemas.lead import LeadCreate, LeadUpdate
from src.models.lead import Lead, LeadStatus

class TestLeadService:
    """Unit tests for lead service functions."""

    @pytest.mark.unit
    async def test_should_get_leads_with_pagination(self, mock_db, mock_query_result):
        # Arrange
        mock_leads = [
            Lead(id=1, contact_id=1, status=LeadStatus.COLD, source="import"),
            Lead(id=2, contact_id=2, status=LeadStatus.WARM, source="landing_page"),
        ]
        mock_query_result.scalars = MagicMock(return_value=MagicMock(all=MagicMock(return_value=mock_leads)))
        
        mock_count_result = MagicMock()
        mock_count_result.scalar = MagicMock(return_value=2)
        
        mock_db.execute = AsyncMock(side_effect=[mock_query_result, mock_count_result])
        
        # Act
        leads, total = await lead_service.get_leads(mock_db, skip=0, limit=20)
        
        # Assert
        assert len(leads) == 2
        assert total == 2
        assert mock_db.execute.call_count == 2

    @pytest.mark.unit
    async def test_should_filter_leads_by_status(self, mock_db, mock_query_result):
        # Arrange
        mock_leads = [Lead(id=1, contact_id=1, status=LeadStatus.HOT, source="import")]
        mock_query_result.scalars = MagicMock(return_value=MagicMock(all=MagicMock(return_value=mock_leads)))
        
        mock_count_result = MagicMock()
        mock_count_result.scalar = MagicMock(return_value=1)
        
        mock_db.execute = AsyncMock(side_effect=[mock_query_result, mock_count_result])
        
        # Act
        leads, total = await lead_service.get_leads(mock_db, status=LeadStatus.HOT)
        
        # Assert
        assert len(leads) == 1
        assert leads[0].status == LeadStatus.HOT
        assert total == 1

    @pytest.mark.unit
    async def test_should_get_lead_by_id(self, mock_db):
        # Arrange
        expected_lead = Lead(id=1, contact_id=1, status=LeadStatus.COLD, source="import")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=expected_lead)
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        # Act
        lead = await lead_service.get_lead(mock_db, lead_id=1)
        
        # Assert
        assert lead is not None
        assert lead.id == 1
        assert mock_db.execute.await_count == 1

    @pytest.mark.unit
    async def test_should_return_none_when_lead_not_found(self, mock_db):
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        # Act
        lead = await lead_service.get_lead(mock_db, lead_id=999)
        
        # Assert
        assert lead is None

    @pytest.mark.unit
    async def test_should_create_lead_with_history(self, mock_db):
        # Arrange
        lead_data = LeadCreate(
            contact_id=1,
            status=LeadStatus.COLD,
            source="landing_page"
        )
        created_lead = Lead(id=1, **lead_data.model_dump())
        
        # Mock get_lead to return the created lead
        with patch('src.services.lead_service.get_lead', AsyncMock(return_value=created_lead)):
            # Act
            result = await lead_service.create_lead(mock_db, lead_data)
        
        # Assert
        mock_db.add.assert_called()
        assert mock_db.add.call_count == 2  # Lead + History
        assert mock_db.flush.await_count >= 1
        assert result.id == 1

    @pytest.mark.unit
    async def test_should_update_lead_and_create_history_on_status_change(self, mock_db):
        # Arrange
        existing_lead = Lead(id=1, contact_id=1, status=LeadStatus.COLD, source="import")
        update_data = LeadUpdate(status=LeadStatus.HOT)
        
        with patch('src.services.lead_service.get_lead', AsyncMock(side_effect=[existing_lead, existing_lead])):
            # Act
            result = await lead_service.update_lead(mock_db, lead_id=1, lead_data=update_data)
        
        # Assert
        assert result is not None
        assert result.status == LeadStatus.HOT
        mock_db.add.assert_called()  # History entry added
        mock_db.flush.assert_awaited()

    @pytest.mark.unit
    async def test_should_update_lead_without_history_when_no_status_change(self, mock_db):
        # Arrange
        existing_lead = Lead(id=1, contact_id=1, status=LeadStatus.COLD, source="import")
        update_data = LeadUpdate(source="manual")
        
        with patch('src.services.lead_service.get_lead', AsyncMock(side_effect=[existing_lead, existing_lead])):
            # Act
            result = await lead_service.update_lead(mock_db, lead_id=1, lead_data=update_data)
        
        # Assert
        assert result is not None
        assert result.source == "manual"
        # Should not add history for non-status changes
        assert mock_db.add.call_count == 0

    @pytest.mark.unit
    async def test_should_return_none_when_updating_nonexistent_lead(self, mock_db):
        # Arrange
        update_data = LeadUpdate(status=LeadStatus.HOT)
        
        with patch('src.services.lead_service.get_lead', AsyncMock(return_value=None)):
            # Act
            result = await lead_service.update_lead(mock_db, lead_id=999, lead_data=update_data)
        
        # Assert
        assert result is None
