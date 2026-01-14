"""Unit tests for setting_service and seed_service."""
import pytest
from sqlalchemy import select

from src.models.setting import Setting
from src.models.lookup_value import LookupValue
from src.schemas.setting import (
    SettingCreate,
    SettingUpdate,
    LookupValueCreate,
    LookupValueUpdate,
)
from src.services import setting_service
from src.services.seed_service import seed_lookup_values, get_seed_statistics, DEFAULT_LOOKUP_VALUES


class TestSettingService:
    """Tests for Setting service functions."""

    @pytest.mark.asyncio
    async def test_get_all_settings(self, db_session):
        """Test get_all_settings returns list."""
        # Create some settings
        s1 = Setting(key="test.key1", category="general", value="val1", value_type="string")
        s2 = Setting(key="test.key2", category="email", value="val2", value_type="string")
        db_session.add_all([s1, s2])
        await db_session.commit()

        settings = await setting_service.get_all_settings(db_session)
        assert len(settings) >= 2

    @pytest.mark.asyncio
    async def test_get_all_settings_by_category(self, db_session):
        """Test get_all_settings filters by category."""
        s1 = Setting(key="cat.test1", category="catA", value="v1", value_type="string")
        s2 = Setting(key="cat.test2", category="catB", value="v2", value_type="string")
        db_session.add_all([s1, s2])
        await db_session.commit()

        settings = await setting_service.get_all_settings(db_session, category="catA")
        assert len(settings) == 1
        assert settings[0].key == "cat.test1"

    @pytest.mark.asyncio
    async def test_get_setting(self, db_session):
        """Test get_setting returns correct setting."""
        setting = Setting(key="find.me", category="test", value="found", value_type="string")
        db_session.add(setting)
        await db_session.commit()

        result = await setting_service.get_setting(db_session, "find.me")
        assert result is not None
        assert result.value == "found"

    @pytest.mark.asyncio
    async def test_get_setting_not_found(self, db_session):
        """Test get_setting returns None for missing key."""
        result = await setting_service.get_setting(db_session, "nonexistent.key")
        assert result is None

    @pytest.mark.asyncio
    async def test_create_setting(self, db_session):
        """Test create_setting creates and returns new setting."""
        data = SettingCreate(
            key="new.setting",
            category="test",
            value="new_value",
            value_type="string",
        )
        setting = await setting_service.create_setting(db_session, data)
        
        assert setting.id is not None
        assert setting.key == "new.setting"
        assert setting.value == "new_value"

    @pytest.mark.asyncio
    async def test_update_setting(self, db_session):
        """Test update_setting persists change."""
        setting = Setting(key="update.me", category="test", value="old", value_type="string")
        db_session.add(setting)
        await db_session.commit()

        update_data = SettingUpdate(value="new")
        updated = await setting_service.update_setting(db_session, "update.me", update_data)
        
        assert updated is not None
        assert updated.value == "new"

    @pytest.mark.asyncio
    async def test_update_setting_not_found(self, db_session):
        """Test update_setting returns None for missing key."""
        update_data = SettingUpdate(value="new")
        result = await setting_service.update_setting(db_session, "missing.key", update_data)
        assert result is None

    @pytest.mark.asyncio
    async def test_upsert_setting_create(self, db_session):
        """Test upsert_setting creates new setting."""
        setting = await setting_service.upsert_setting(
            db_session, "upsert.new", "test", "created", "string"
        )
        assert setting.id is not None
        assert setting.value == "created"

    @pytest.mark.asyncio
    async def test_upsert_setting_update(self, db_session):
        """Test upsert_setting updates existing setting."""
        existing = Setting(key="upsert.existing", category="test", value="old", value_type="string")
        db_session.add(existing)
        await db_session.commit()

        setting = await setting_service.upsert_setting(
            db_session, "upsert.existing", "test", "updated", "string"
        )
        assert setting.value == "updated"

    @pytest.mark.asyncio
    async def test_delete_setting(self, db_session):
        """Test delete_setting removes setting."""
        setting = Setting(key="delete.me", category="test", value="bye", value_type="string")
        db_session.add(setting)
        await db_session.commit()

        result = await setting_service.delete_setting(db_session, "delete.me")
        assert result is True
        await db_session.commit()  # Commit the delete

        # Expire the session to force a fresh query
        db_session.expire_all()
        
        # Verify deleted
        check = await setting_service.get_setting(db_session, "delete.me")
        assert check is None

    @pytest.mark.asyncio
    async def test_delete_setting_not_found(self, db_session):
        """Test delete_setting returns False for missing key."""
        result = await setting_service.delete_setting(db_session, "nonexistent")
        assert result is False


class TestLookupValueService:
    """Tests for LookupValue service functions."""

    @pytest.mark.asyncio
    async def test_get_lookup_values(self, db_session):
        """Test get_lookup_values returns filtered list."""
        lv1 = LookupValue(category="testcat", value="v1", label="Label 1", sort_order=0)
        lv2 = LookupValue(category="testcat", value="v2", label="Label 2", sort_order=1)
        lv3 = LookupValue(category="other", value="v3", label="Label 3", sort_order=0)
        db_session.add_all([lv1, lv2, lv3])
        await db_session.commit()

        lookups = await setting_service.get_lookup_values(db_session, "testcat")
        assert len(lookups) == 2

    @pytest.mark.asyncio
    async def test_get_lookup_values_excludes_inactive(self, db_session):
        """Test get_lookup_values excludes inactive by default."""
        lv1 = LookupValue(category="active_test", value="active", label="Active", is_active=True)
        lv2 = LookupValue(category="active_test", value="inactive", label="Inactive", is_active=False)
        db_session.add_all([lv1, lv2])
        await db_session.commit()

        lookups = await setting_service.get_lookup_values(db_session, "active_test")
        assert len(lookups) == 1
        assert lookups[0].value == "active"

    @pytest.mark.asyncio
    async def test_get_lookup_values_include_inactive(self, db_session):
        """Test get_lookup_values includes inactive when requested."""
        lv1 = LookupValue(category="inc_test", value="act", label="Active", is_active=True)
        lv2 = LookupValue(category="inc_test", value="inact", label="Inactive", is_active=False)
        db_session.add_all([lv1, lv2])
        await db_session.commit()

        lookups = await setting_service.get_lookup_values(db_session, "inc_test", include_inactive=True)
        assert len(lookups) == 2

    @pytest.mark.asyncio
    async def test_create_lookup_value(self, db_session):
        """Test create_lookup_value creates and returns new value."""
        data = LookupValueCreate(
            category="newcat",
            value="newval",
            label="New Label",
            sort_order=5,
        )
        lookup = await setting_service.create_lookup_value(db_session, data)
        
        assert lookup.id is not None
        assert lookup.category == "newcat"
        assert lookup.value == "newval"
        assert lookup.sort_order == 5

    @pytest.mark.asyncio
    async def test_update_lookup_value(self, db_session):
        """Test update_lookup_value updates existing value."""
        lv = LookupValue(category="upd_cat", value="upd_val", label="Old Label")
        db_session.add(lv)
        await db_session.commit()

        update_data = LookupValueUpdate(label="New Label")
        updated = await setting_service.update_lookup_value(db_session, lv.id, update_data)
        
        assert updated is not None
        assert updated.label == "New Label"

    @pytest.mark.asyncio
    async def test_update_lookup_value_not_found(self, db_session):
        """Test update_lookup_value returns None for missing ID."""
        update_data = LookupValueUpdate(label="New")
        result = await setting_service.update_lookup_value(db_session, 99999, update_data)
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_lookup_value_soft(self, db_session):
        """Test delete_lookup_value soft-deletes (sets is_active=False)."""
        lv = LookupValue(category="del_cat", value="del_val", label="Delete Me", is_active=True)
        db_session.add(lv)
        await db_session.commit()
        lv_id = lv.id

        result = await setting_service.delete_lookup_value(db_session, lv_id, soft_delete=True)
        assert result is True

        # Refresh and check
        await db_session.refresh(lv)
        assert lv.is_active is False

    @pytest.mark.asyncio
    async def test_delete_lookup_value_hard(self, db_session):
        """Test delete_lookup_value hard-deletes when requested."""
        lv = LookupValue(category="hard_del", value="hard", label="Hard Delete")
        db_session.add(lv)
        await db_session.commit()
        lv_id = lv.id

        result = await setting_service.delete_lookup_value(db_session, lv_id, soft_delete=False)
        assert result is True
        await db_session.commit()  # Commit the delete
        
        # Expire the session to force a fresh query
        db_session.expire_all()

        # Verify deleted
        check = await setting_service.get_lookup_value(db_session, lv_id)
        assert check is None

    @pytest.mark.asyncio
    async def test_delete_lookup_value_not_found(self, db_session):
        """Test delete_lookup_value returns False for missing ID."""
        result = await setting_service.delete_lookup_value(db_session, 99999)
        assert result is False

    @pytest.mark.asyncio
    async def test_get_all_lookup_categories(self, db_session):
        """Test get_all_lookup_categories returns distinct categories."""
        lv1 = LookupValue(category="cat_a", value="v1", label="L1")
        lv2 = LookupValue(category="cat_b", value="v2", label="L2")
        lv3 = LookupValue(category="cat_a", value="v3", label="L3")
        db_session.add_all([lv1, lv2, lv3])
        await db_session.commit()

        categories = await setting_service.get_all_lookup_categories(db_session)
        assert "cat_a" in categories
        assert "cat_b" in categories

    @pytest.mark.asyncio
    async def test_reorder_lookup_values(self, db_session):
        """Test reorder_lookup_values sets sort_order based on list position."""
        lv1 = LookupValue(category="reorder", value="v1", label="L1", sort_order=0)
        lv2 = LookupValue(category="reorder", value="v2", label="L2", sort_order=1)
        lv3 = LookupValue(category="reorder", value="v3", label="L3", sort_order=2)
        db_session.add_all([lv1, lv2, lv3])
        await db_session.commit()

        # Reorder: v3, v1, v2
        await setting_service.reorder_lookup_values(
            db_session, "reorder", [lv3.id, lv1.id, lv2.id]
        )

        # Refresh and check
        await db_session.refresh(lv1)
        await db_session.refresh(lv2)
        await db_session.refresh(lv3)

        assert lv3.sort_order == 0
        assert lv1.sort_order == 1
        assert lv2.sort_order == 2


class TestSeedService:
    """Tests for seed_service functions."""

    @pytest.mark.asyncio
    async def test_seed_populates_all_categories(self, db_session):
        """Test seed function populates all expected categories."""
        created = await seed_lookup_values(db_session)
        await db_session.commit()
        
        # Check that all expected categories were created
        assert len(created) == len(DEFAULT_LOOKUP_VALUES)
        
        # Check specific categories have values
        for category in DEFAULT_LOOKUP_VALUES.keys():
            assert category in created
            # At least some values should be created
            assert created[category] >= 0

    @pytest.mark.asyncio
    async def test_seed_creates_expected_counts(self, db_session):
        """Test seed function creates expected number of values per category."""
        created = await seed_lookup_values(db_session)
        await db_session.commit()
        
        # Verify each category has the expected number of values
        for category, expected_values in DEFAULT_LOOKUP_VALUES.items():
            assert created[category] == len(expected_values)

    @pytest.mark.asyncio
    async def test_seed_idempotency(self, db_session):
        """Test running seed twice does not create duplicates."""
        # First seed
        created_first = await seed_lookup_values(db_session)
        await db_session.commit()
        
        # Second seed
        created_second = await seed_lookup_values(db_session)
        await db_session.commit()
        
        # Second run should create 0 new values
        for category in DEFAULT_LOOKUP_VALUES.keys():
            assert created_second[category] == 0

    @pytest.mark.asyncio
    async def test_seed_specific_values_lead_status(self, db_session):
        """Test seed creates expected lead_status values."""
        await seed_lookup_values(db_session)
        await db_session.commit()
        
        lookups = await setting_service.get_lookup_values(db_session, "lead_status")
        values = [lv.value for lv in lookups]
        
        assert "new" in values
        assert "contacted" in values
        assert "qualified" in values
        assert "converted" in values
        assert "disqualified" in values
        assert len(lookups) >= 5

    @pytest.mark.asyncio
    async def test_seed_specific_values_country(self, db_session):
        """Test seed creates expected country values."""
        await seed_lookup_values(db_session)
        await db_session.commit()
        
        lookups = await setting_service.get_lookup_values(db_session, "country")
        values = [lv.value for lv in lookups]
        
        assert "AT" in values
        assert "DE" in values
        assert "CH" in values
        assert len(lookups) >= 3

    @pytest.mark.asyncio
    async def test_seed_specific_values_task_priority(self, db_session):
        """Test seed creates expected task_priority values."""
        await seed_lookup_values(db_session)
        await db_session.commit()
        
        lookups = await setting_service.get_lookup_values(db_session, "task_priority")
        values = [lv.value for lv in lookups]
        
        assert "low" in values
        assert "medium" in values
        assert "high" in values
        assert "urgent" in values
        assert len(lookups) >= 4

    @pytest.mark.asyncio
    async def test_get_seed_statistics(self, db_session):
        """Test get_seed_statistics returns correct counts."""
        # First seed
        await seed_lookup_values(db_session)
        await db_session.commit()
        
        # Get statistics
        stats = await get_seed_statistics(db_session)
        
        # Check that all categories are present
        for category in DEFAULT_LOOKUP_VALUES.keys():
            assert category in stats
            assert stats[category] == len(DEFAULT_LOOKUP_VALUES[category])
