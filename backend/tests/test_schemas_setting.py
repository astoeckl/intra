"""Unit tests for Setting and LookupValue Pydantic schemas."""
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from src.schemas.setting import (
    SettingBase,
    SettingCreate,
    SettingUpdate,
    SettingResponse,
    LookupValueBase,
    LookupValueCreate,
    LookupValueUpdate,
    LookupValueResponse,
    LOOKUP_CATEGORIES,
)


class TestSettingCreate:
    """Tests for SettingCreate schema validation."""

    def test_setting_create_valid(self):
        """Test SettingCreate accepts valid data."""
        schema = SettingCreate(
            key="app.setting",
            category="general",
            value="test_value",
            value_type="string",
        )
        assert schema.key == "app.setting"
        assert schema.category == "general"
        assert schema.value == "test_value"
        assert schema.value_type == "string"

    def test_setting_create_value_type_default(self):
        """Test SettingCreate defaults value_type to 'string'."""
        schema = SettingCreate(
            key="app.setting",
            category="general",
            value="test",
        )
        assert schema.value_type == "string"

    def test_setting_create_value_optional(self):
        """Test SettingCreate allows None for value."""
        schema = SettingCreate(
            key="app.setting",
            category="general",
            value=None,
        )
        assert schema.value is None

    def test_setting_create_missing_key_raises(self):
        """Test SettingCreate raises error when key is missing."""
        with pytest.raises(ValidationError) as exc_info:
            SettingCreate(
                category="general",
                value="test",
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("key",) for e in errors)

    def test_setting_create_missing_category_raises(self):
        """Test SettingCreate raises error when category is missing."""
        with pytest.raises(ValidationError) as exc_info:
            SettingCreate(
                key="app.setting",
                value="test",
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("category",) for e in errors)

    def test_setting_create_key_empty_raises(self):
        """Test SettingCreate raises error for empty key."""
        with pytest.raises(ValidationError) as exc_info:
            SettingCreate(
                key="",
                category="general",
                value="test",
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("key",) for e in errors)

    def test_setting_create_category_empty_raises(self):
        """Test SettingCreate raises error for empty category."""
        with pytest.raises(ValidationError) as exc_info:
            SettingCreate(
                key="app.setting",
                category="",
                value="test",
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("category",) for e in errors)

    def test_setting_create_key_too_long_raises(self):
        """Test SettingCreate raises error when key exceeds 255 characters."""
        with pytest.raises(ValidationError) as exc_info:
            SettingCreate(
                key="x" * 256,
                category="general",
                value="test",
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("key",) for e in errors)

    def test_setting_create_key_max_length_valid(self):
        """Test SettingCreate accepts key at max length (255 characters)."""
        schema = SettingCreate(
            key="x" * 255,
            category="general",
            value="test",
        )
        assert len(schema.key) == 255

    def test_setting_create_category_too_long_raises(self):
        """Test SettingCreate raises error when category exceeds 100 characters."""
        with pytest.raises(ValidationError) as exc_info:
            SettingCreate(
                key="app.setting",
                category="x" * 101,
                value="test",
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("category",) for e in errors)

    def test_setting_create_category_max_length_valid(self):
        """Test SettingCreate accepts category at max length (100 characters)."""
        schema = SettingCreate(
            key="app.setting",
            category="x" * 100,
            value="test",
        )
        assert len(schema.category) == 100

    def test_setting_create_invalid_value_type_raises(self):
        """Test SettingCreate raises error for invalid value_type."""
        with pytest.raises(ValidationError) as exc_info:
            SettingCreate(
                key="app.setting",
                category="general",
                value="test",
                value_type="invalid",
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("value_type",) for e in errors)

    def test_setting_create_all_value_types_valid(self):
        """Test SettingCreate accepts all valid value_type options."""
        valid_types = ["string", "number", "boolean", "json"]
        for value_type in valid_types:
            schema = SettingCreate(
                key="app.setting",
                category="general",
                value="test",
                value_type=value_type,
            )
            assert schema.value_type == value_type


class TestSettingUpdate:
    """Tests for SettingUpdate schema validation."""

    def test_setting_update_partial(self):
        """Test SettingUpdate allows partial updates."""
        schema = SettingUpdate(value="new_value")
        assert schema.value == "new_value"
        assert schema.value_type is None

    def test_setting_update_value_type_only(self):
        """Test SettingUpdate allows updating only value_type."""
        schema = SettingUpdate(value_type="json")
        assert schema.value is None
        assert schema.value_type == "json"

    def test_setting_update_empty(self):
        """Test SettingUpdate allows empty update."""
        schema = SettingUpdate()
        assert schema.value is None
        assert schema.value_type is None

    def test_setting_update_both_fields(self):
        """Test SettingUpdate allows updating both fields."""
        schema = SettingUpdate(value="new_value", value_type="number")
        assert schema.value == "new_value"
        assert schema.value_type == "number"

    def test_setting_update_invalid_value_type_raises(self):
        """Test SettingUpdate raises error for invalid value_type."""
        with pytest.raises(ValidationError) as exc_info:
            SettingUpdate(value_type="invalid")
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("value_type",) for e in errors)


class TestSettingResponse:
    """Tests for SettingResponse schema validation."""

    def test_setting_response_valid(self):
        """Test SettingResponse accepts valid data."""
        now = datetime.now(timezone.utc)
        schema = SettingResponse(
            id=1,
            key="app.setting",
            category="general",
            value="test",
            value_type="string",
            created_at=now,
            updated_at=now,
        )
        assert schema.id == 1
        assert schema.key == "app.setting"
        assert schema.created_at == now
        assert schema.updated_at == now

    def test_setting_response_missing_id_raises(self):
        """Test SettingResponse raises error when id is missing."""
        now = datetime.now(timezone.utc)
        with pytest.raises(ValidationError) as exc_info:
            SettingResponse(
                key="app.setting",
                category="general",
                value="test",
                value_type="string",
                created_at=now,
                updated_at=now,
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("id",) for e in errors)

    def test_setting_response_missing_timestamps_raises(self):
        """Test SettingResponse raises error when timestamps are missing."""
        with pytest.raises(ValidationError) as exc_info:
            SettingResponse(
                id=1,
                key="app.setting",
                category="general",
                value="test",
                value_type="string",
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("created_at",) for e in errors)
        assert any(e["loc"] == ("updated_at",) for e in errors)

    def test_setting_response_from_attributes(self):
        """Test SettingResponse can be created from object attributes."""

        class MockSetting:
            id = 1
            key = "app.setting"
            category = "general"
            value = "test"
            value_type = "string"
            created_at = datetime.now(timezone.utc)
            updated_at = datetime.now(timezone.utc)

        schema = SettingResponse.model_validate(MockSetting())
        assert schema.id == 1
        assert schema.key == "app.setting"


class TestLookupValueCreate:
    """Tests for LookupValueCreate schema validation."""

    def test_lookup_value_create_valid(self):
        """Test LookupValueCreate accepts valid data."""
        schema = LookupValueCreate(
            category="lead_status",
            value="new",
            label="New Lead",
            sort_order=1,
            is_active=True,
        )
        assert schema.category == "lead_status"
        assert schema.value == "new"
        assert schema.label == "New Lead"
        assert schema.sort_order == 1
        assert schema.is_active is True

    def test_lookup_value_create_defaults(self):
        """Test LookupValueCreate applies default values."""
        schema = LookupValueCreate(
            category="lead_status",
            value="new",
            label="New Lead",
        )
        assert schema.sort_order == 0
        assert schema.is_active is True

    def test_lookup_value_create_missing_category_raises(self):
        """Test LookupValueCreate raises error when category is missing."""
        with pytest.raises(ValidationError) as exc_info:
            LookupValueCreate(
                value="new",
                label="New Lead",
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("category",) for e in errors)

    def test_lookup_value_create_missing_value_raises(self):
        """Test LookupValueCreate raises error when value is missing."""
        with pytest.raises(ValidationError) as exc_info:
            LookupValueCreate(
                category="lead_status",
                label="New Lead",
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("value",) for e in errors)

    def test_lookup_value_create_missing_label_raises(self):
        """Test LookupValueCreate raises error when label is missing."""
        with pytest.raises(ValidationError) as exc_info:
            LookupValueCreate(
                category="lead_status",
                value="new",
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("label",) for e in errors)

    def test_lookup_value_create_category_empty_raises(self):
        """Test LookupValueCreate raises error for empty category."""
        with pytest.raises(ValidationError) as exc_info:
            LookupValueCreate(
                category="",
                value="new",
                label="New Lead",
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("category",) for e in errors)

    def test_lookup_value_create_value_empty_raises(self):
        """Test LookupValueCreate raises error for empty value."""
        with pytest.raises(ValidationError) as exc_info:
            LookupValueCreate(
                category="lead_status",
                value="",
                label="New Lead",
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("value",) for e in errors)

    def test_lookup_value_create_label_empty_raises(self):
        """Test LookupValueCreate raises error for empty label."""
        with pytest.raises(ValidationError) as exc_info:
            LookupValueCreate(
                category="lead_status",
                value="new",
                label="",
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("label",) for e in errors)

    def test_lookup_value_create_category_too_long_raises(self):
        """Test LookupValueCreate raises error when category exceeds 100 characters."""
        with pytest.raises(ValidationError) as exc_info:
            LookupValueCreate(
                category="x" * 101,
                value="new",
                label="New Lead",
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("category",) for e in errors)

    def test_lookup_value_create_value_too_long_raises(self):
        """Test LookupValueCreate raises error when value exceeds 100 characters."""
        with pytest.raises(ValidationError) as exc_info:
            LookupValueCreate(
                category="lead_status",
                value="x" * 101,
                label="New Lead",
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("value",) for e in errors)

    def test_lookup_value_create_label_too_long_raises(self):
        """Test LookupValueCreate raises error when label exceeds 255 characters."""
        with pytest.raises(ValidationError) as exc_info:
            LookupValueCreate(
                category="lead_status",
                value="new",
                label="x" * 256,
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("label",) for e in errors)

    def test_lookup_value_create_max_lengths_valid(self):
        """Test LookupValueCreate accepts fields at max length."""
        schema = LookupValueCreate(
            category="x" * 100,
            value="y" * 100,
            label="z" * 255,
        )
        assert len(schema.category) == 100
        assert len(schema.value) == 100
        assert len(schema.label) == 255

    def test_lookup_value_create_sort_order_negative_raises(self):
        """Test LookupValueCreate raises error for negative sort_order."""
        with pytest.raises(ValidationError) as exc_info:
            LookupValueCreate(
                category="lead_status",
                value="new",
                label="New Lead",
                sort_order=-1,
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("sort_order",) for e in errors)

    def test_lookup_value_create_sort_order_zero_valid(self):
        """Test LookupValueCreate accepts sort_order of zero."""
        schema = LookupValueCreate(
            category="lead_status",
            value="new",
            label="New Lead",
            sort_order=0,
        )
        assert schema.sort_order == 0

    def test_lookup_value_create_is_active_false(self):
        """Test LookupValueCreate accepts is_active as False."""
        schema = LookupValueCreate(
            category="lead_status",
            value="new",
            label="New Lead",
            is_active=False,
        )
        assert schema.is_active is False


class TestLookupValueUpdate:
    """Tests for LookupValueUpdate schema validation."""

    def test_lookup_value_update_partial_value(self):
        """Test LookupValueUpdate allows updating only value."""
        schema = LookupValueUpdate(value="updated")
        assert schema.value == "updated"
        assert schema.label is None
        assert schema.sort_order is None
        assert schema.is_active is None

    def test_lookup_value_update_partial_label(self):
        """Test LookupValueUpdate allows updating only label."""
        schema = LookupValueUpdate(label="Updated Label")
        assert schema.label == "Updated Label"
        assert schema.value is None

    def test_lookup_value_update_partial_sort_order(self):
        """Test LookupValueUpdate allows updating only sort_order."""
        schema = LookupValueUpdate(sort_order=5)
        assert schema.sort_order == 5
        assert schema.value is None

    def test_lookup_value_update_partial_is_active(self):
        """Test LookupValueUpdate allows updating only is_active."""
        schema = LookupValueUpdate(is_active=False)
        assert schema.is_active is False
        assert schema.value is None

    def test_lookup_value_update_empty(self):
        """Test LookupValueUpdate allows empty update."""
        schema = LookupValueUpdate()
        assert schema.value is None
        assert schema.label is None
        assert schema.sort_order is None
        assert schema.is_active is None

    def test_lookup_value_update_all_fields(self):
        """Test LookupValueUpdate allows updating all fields."""
        schema = LookupValueUpdate(
            value="updated",
            label="Updated Label",
            sort_order=10,
            is_active=False,
        )
        assert schema.value == "updated"
        assert schema.label == "Updated Label"
        assert schema.sort_order == 10
        assert schema.is_active is False

    def test_lookup_value_update_value_too_long_raises(self):
        """Test LookupValueUpdate raises error when value exceeds 100 characters."""
        with pytest.raises(ValidationError) as exc_info:
            LookupValueUpdate(value="x" * 101)
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("value",) for e in errors)

    def test_lookup_value_update_label_too_long_raises(self):
        """Test LookupValueUpdate raises error when label exceeds 255 characters."""
        with pytest.raises(ValidationError) as exc_info:
            LookupValueUpdate(label="x" * 256)
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("label",) for e in errors)

    def test_lookup_value_update_sort_order_negative_raises(self):
        """Test LookupValueUpdate raises error for negative sort_order."""
        with pytest.raises(ValidationError) as exc_info:
            LookupValueUpdate(sort_order=-1)
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("sort_order",) for e in errors)

    def test_lookup_value_update_value_empty_raises(self):
        """Test LookupValueUpdate raises error for empty value when provided."""
        with pytest.raises(ValidationError) as exc_info:
            LookupValueUpdate(value="")
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("value",) for e in errors)

    def test_lookup_value_update_label_empty_raises(self):
        """Test LookupValueUpdate raises error for empty label when provided."""
        with pytest.raises(ValidationError) as exc_info:
            LookupValueUpdate(label="")
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("label",) for e in errors)


class TestLookupValueResponse:
    """Tests for LookupValueResponse schema validation."""

    def test_lookup_value_response_valid(self):
        """Test LookupValueResponse accepts valid data."""
        now = datetime.now(timezone.utc)
        schema = LookupValueResponse(
            id=1,
            category="lead_status",
            value="new",
            label="New Lead",
            sort_order=1,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        assert schema.id == 1
        assert schema.category == "lead_status"
        assert schema.value == "new"
        assert schema.label == "New Lead"
        assert schema.sort_order == 1
        assert schema.is_active is True
        assert schema.created_at == now
        assert schema.updated_at == now

    def test_lookup_value_response_missing_id_raises(self):
        """Test LookupValueResponse raises error when id is missing."""
        now = datetime.now(timezone.utc)
        with pytest.raises(ValidationError) as exc_info:
            LookupValueResponse(
                category="lead_status",
                value="new",
                label="New Lead",
                sort_order=1,
                is_active=True,
                created_at=now,
                updated_at=now,
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("id",) for e in errors)

    def test_lookup_value_response_missing_timestamps_raises(self):
        """Test LookupValueResponse raises error when timestamps are missing."""
        with pytest.raises(ValidationError) as exc_info:
            LookupValueResponse(
                id=1,
                category="lead_status",
                value="new",
                label="New Lead",
                sort_order=1,
                is_active=True,
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("created_at",) for e in errors)
        assert any(e["loc"] == ("updated_at",) for e in errors)

    def test_lookup_value_response_from_attributes(self):
        """Test LookupValueResponse can be created from object attributes."""

        class MockLookupValue:
            id = 1
            category = "lead_status"
            value = "new"
            label = "New Lead"
            sort_order = 1
            is_active = True
            created_at = datetime.now(timezone.utc)
            updated_at = datetime.now(timezone.utc)

        schema = LookupValueResponse.model_validate(MockLookupValue())
        assert schema.id == 1
        assert schema.category == "lead_status"
        assert schema.value == "new"


class TestLookupCategories:
    """Tests for LOOKUP_CATEGORIES constant."""

    def test_lookup_categories_is_list(self):
        """Test LOOKUP_CATEGORIES is a list."""
        assert isinstance(LOOKUP_CATEGORIES, list)

    def test_lookup_categories_contains_expected_values(self):
        """Test LOOKUP_CATEGORIES contains expected category names."""
        expected = [
            "lead_status",
            "potential_category",
            "industry",
            "country",
            "salutation",
            "title",
            "contact_lead_status",
            "task_priority",
            "campaign_type",
            "campaign_source",
        ]
        for category in expected:
            assert category in LOOKUP_CATEGORIES

    def test_lookup_categories_not_empty(self):
        """Test LOOKUP_CATEGORIES is not empty."""
        assert len(LOOKUP_CATEGORIES) > 0
