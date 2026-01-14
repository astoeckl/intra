"""Unit tests for Setting and LookupValue models."""
import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.models.setting import Setting
from src.models.lookup_value import LookupValue


class TestSettingModel:
    """Tests for the Setting model."""

    @pytest.mark.asyncio
    async def test_create_setting(self, db_session):
        """Test creating a new setting."""
        setting = Setting(
            key="app.company_name",
            category="general",
            value="Test Company",
            value_type="string",
        )
        db_session.add(setting)
        await db_session.commit()
        await db_session.refresh(setting)

        assert setting.id is not None
        assert setting.key == "app.company_name"
        assert setting.category == "general"
        assert setting.value == "Test Company"
        assert setting.value_type == "string"
        assert setting.created_at is not None
        assert setting.updated_at is not None

    @pytest.mark.asyncio
    async def test_read_setting(self, db_session):
        """Test reading a setting from database."""
        # Create
        setting = Setting(
            key="smtp.host",
            category="email",
            value="smtp.example.com",
            value_type="string",
        )
        db_session.add(setting)
        await db_session.commit()

        # Read
        result = await db_session.execute(
            select(Setting).where(Setting.key == "smtp.host")
        )
        fetched = result.scalar_one()

        assert fetched.key == "smtp.host"
        assert fetched.category == "email"
        assert fetched.value == "smtp.example.com"

    @pytest.mark.asyncio
    async def test_update_setting(self, db_session):
        """Test updating a setting."""
        setting = Setting(
            key="app.timezone",
            category="general",
            value="Europe/Vienna",
            value_type="string",
        )
        db_session.add(setting)
        await db_session.commit()

        # Update
        setting.value = "Europe/Berlin"
        await db_session.commit()
        await db_session.refresh(setting)

        assert setting.value == "Europe/Berlin"

    @pytest.mark.asyncio
    async def test_delete_setting(self, db_session):
        """Test deleting a setting."""
        setting = Setting(
            key="temp.setting",
            category="general",
            value="temporary",
            value_type="string",
        )
        db_session.add(setting)
        await db_session.commit()
        setting_id = setting.id

        # Delete
        await db_session.delete(setting)
        await db_session.commit()

        # Verify deleted
        result = await db_session.execute(
            select(Setting).where(Setting.id == setting_id)
        )
        assert result.scalar_one_or_none() is None

    @pytest.mark.asyncio
    async def test_unique_key_constraint(self, db_session):
        """Test that duplicate keys raise an error."""
        setting1 = Setting(
            key="unique.key",
            category="general",
            value="first",
            value_type="string",
        )
        db_session.add(setting1)
        await db_session.commit()

        setting2 = Setting(
            key="unique.key",
            category="general",
            value="second",
            value_type="string",
        )
        db_session.add(setting2)

        with pytest.raises(IntegrityError):
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_setting_repr(self, db_session):
        """Test Setting string representation."""
        setting = Setting(
            key="test.repr",
            category="test",
            value="value",
            value_type="string",
        )
        db_session.add(setting)
        await db_session.commit()

        repr_str = repr(setting)
        assert "Setting" in repr_str
        assert "test.repr" in repr_str
        assert "test" in repr_str


class TestLookupValueModel:
    """Tests for the LookupValue model."""

    @pytest.mark.asyncio
    async def test_create_lookup_value(self, db_session):
        """Test creating a new lookup value."""
        lookup = LookupValue(
            category="country",
            value="AT",
            label="Österreich",
            sort_order=1,
            is_active=True,
        )
        db_session.add(lookup)
        await db_session.commit()
        await db_session.refresh(lookup)

        assert lookup.id is not None
        assert lookup.category == "country"
        assert lookup.value == "AT"
        assert lookup.label == "Österreich"
        assert lookup.sort_order == 1
        assert lookup.is_active is True
        assert lookup.created_at is not None
        assert lookup.updated_at is not None

    @pytest.mark.asyncio
    async def test_read_lookup_value(self, db_session):
        """Test reading a lookup value from database."""
        lookup = LookupValue(
            category="salutation",
            value="herr",
            label="Herr",
            sort_order=1,
        )
        db_session.add(lookup)
        await db_session.commit()

        result = await db_session.execute(
            select(LookupValue).where(LookupValue.value == "herr")
        )
        fetched = result.scalar_one()

        assert fetched.category == "salutation"
        assert fetched.label == "Herr"

    @pytest.mark.asyncio
    async def test_update_lookup_value(self, db_session):
        """Test updating a lookup value."""
        lookup = LookupValue(
            category="industry",
            value="tax_advisor",
            label="Tax Advisor",
            sort_order=1,
        )
        db_session.add(lookup)
        await db_session.commit()

        # Update
        lookup.label = "Steuerberater"
        await db_session.commit()
        await db_session.refresh(lookup)

        assert lookup.label == "Steuerberater"

    @pytest.mark.asyncio
    async def test_delete_lookup_value(self, db_session):
        """Test deleting a lookup value."""
        lookup = LookupValue(
            category="temp",
            value="temp_value",
            label="Temporary",
            sort_order=1,
        )
        db_session.add(lookup)
        await db_session.commit()
        lookup_id = lookup.id

        # Delete
        await db_session.delete(lookup)
        await db_session.commit()

        # Verify deleted
        result = await db_session.execute(
            select(LookupValue).where(LookupValue.id == lookup_id)
        )
        assert result.scalar_one_or_none() is None

    @pytest.mark.asyncio
    async def test_unique_category_value_constraint(self, db_session):
        """Test that duplicate category+value combinations raise an error."""
        lookup1 = LookupValue(
            category="country",
            value="DE",
            label="Deutschland",
            sort_order=1,
        )
        db_session.add(lookup1)
        await db_session.commit()

        lookup2 = LookupValue(
            category="country",
            value="DE",
            label="Germany",
            sort_order=2,
        )
        db_session.add(lookup2)

        with pytest.raises(IntegrityError):
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_same_value_different_category_allowed(self, db_session):
        """Test that same value is allowed in different categories."""
        lookup1 = LookupValue(
            category="category1",
            value="same_value",
            label="Label 1",
            sort_order=1,
        )
        lookup2 = LookupValue(
            category="category2",
            value="same_value",
            label="Label 2",
            sort_order=1,
        )
        db_session.add(lookup1)
        db_session.add(lookup2)
        await db_session.commit()

        assert lookup1.id is not None
        assert lookup2.id is not None
        assert lookup1.id != lookup2.id

    @pytest.mark.asyncio
    async def test_lookup_value_defaults(self, db_session):
        """Test default values for LookupValue."""
        lookup = LookupValue(
            category="test",
            value="test_value",
            label="Test Label",
        )
        db_session.add(lookup)
        await db_session.commit()
        await db_session.refresh(lookup)

        assert lookup.sort_order == 0
        assert lookup.is_active is True

    @pytest.mark.asyncio
    async def test_lookup_value_repr(self, db_session):
        """Test LookupValue string representation."""
        lookup = LookupValue(
            category="test",
            value="test_val",
            label="Test",
        )
        db_session.add(lookup)
        await db_session.commit()

        repr_str = repr(lookup)
        assert "LookupValue" in repr_str
        assert "test" in repr_str
        assert "test_val" in repr_str
