"""Integration tests for Settings API endpoints."""
import pytest
import uuid
from httpx import AsyncClient, ASGITransport

from src.main import app


def unique_id():
    """Generate a unique ID for test isolation."""
    return str(uuid.uuid4())[:8]


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    """Create test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


class TestSettingsAPI:
    """Integration tests for Settings endpoints."""

    @pytest.mark.asyncio
    async def test_list_settings(self, client):
        """GET /api/settings - returns 200, list of settings."""
        response = await client.get("/api/settings")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_list_settings_with_category_filter(self, client):
        """GET /api/settings?category=general - returns filtered results."""
        response = await client.get("/api/settings?category=general")
        assert response.status_code == 200
        data = response.json()
        # All returned settings should be in general category
        for setting in data:
            assert setting["category"] == "general"

    @pytest.mark.asyncio
    async def test_create_and_get_setting(self, client):
        """Test full CRUD cycle for settings."""
        # Create
        create_response = await client.post(
            "/api/settings",
            json={
                "key": "api.test.crud.setting",
                "category": "test",
                "value": "test_value",
                "value_type": "string",
            }
        )
        assert create_response.status_code == 201
        created = create_response.json()
        assert created["key"] == "api.test.crud.setting"
        assert "id" in created

        # Get
        get_response = await client.get("/api/settings/api.test.crud.setting")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["key"] == "api.test.crud.setting"
        assert data["value"] == "test_value"

        # Update
        update_response = await client.put(
            "/api/settings/api.test.crud.setting",
            json={"value": "updated_value"}
        )
        assert update_response.status_code == 200
        updated = update_response.json()
        assert updated["value"] == "updated_value"

        # Delete
        delete_response = await client.delete("/api/settings/api.test.crud.setting")
        assert delete_response.status_code == 204

        # Verify deleted
        verify_response = await client.get("/api/settings/api.test.crud.setting")
        assert verify_response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_setting_not_found(self, client):
        """GET /api/settings/{key} - returns 404 for missing."""
        response = await client.get("/api/settings/nonexistent.key.xyz123")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_setting_not_found(self, client):
        """PUT /api/settings/{key} - returns 404 for missing."""
        response = await client.put(
            "/api/settings/missing.api.key.xyz",
            json={"value": "new"}
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_setting_not_found(self, client):
        """DELETE /api/settings/{key} - returns 404 for missing."""
        response = await client.delete("/api/settings/missing.del.key.xyz")
        assert response.status_code == 404


class TestLookupValuesAPI:
    """Integration tests for Lookup Values endpoints."""

    @pytest.mark.asyncio
    async def test_list_lookup_categories(self, client):
        """GET /api/settings/lookups/categories - returns list of categories."""
        response = await client.get("/api/settings/lookups/categories")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_create_and_manage_lookup_value(self, client):
        """Test full CRUD cycle for lookup values."""
        uid = unique_id()
        category = f"api_test_category_{uid}"
        value = f"test_val_{uid}"
        
        # Create
        create_response = await client.post(
            "/api/settings/lookups",
            json={
                "category": category,
                "value": value,
                "label": "Test Label",
                "sort_order": 0,
            }
        )
        assert create_response.status_code == 201
        created = create_response.json()
        assert created["category"] == category
        assert created["value"] == value
        lookup_id = created["id"]

        # List
        list_response = await client.get(f"/api/settings/lookups/{category}")
        assert list_response.status_code == 200
        data = list_response.json()
        assert len(data) >= 1

        # Update
        update_response = await client.put(
            f"/api/settings/lookups/{lookup_id}",
            json={"label": "Updated Label"}
        )
        assert update_response.status_code == 200
        updated = update_response.json()
        assert updated["label"] == "Updated Label"

        # Delete (hard to clean up)
        delete_response = await client.delete(f"/api/settings/lookups/{lookup_id}?hard_delete=true")
        assert delete_response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_lookup_values_empty_category(self, client):
        """GET /api/settings/lookups/{category} - returns empty list for unknown category."""
        response = await client.get("/api/settings/lookups/nonexistent_category_xyz")
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_update_lookup_value_not_found(self, client):
        """PUT /api/settings/lookups/{id} - returns 404 for missing."""
        response = await client.put(
            "/api/settings/lookups/99999999",
            json={"label": "New"}
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_lookup_value_not_found(self, client):
        """DELETE /api/settings/lookups/{id} - returns 404 for missing."""
        response = await client.delete("/api/settings/lookups/99999999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_reorder_lookup_values(self, client):
        """POST /api/settings/lookups/{category}/reorder - returns 200."""
        uid = unique_id()
        category = f"reorder_test_{uid}"
        
        # Create two values
        resp1 = await client.post(
            "/api/settings/lookups",
            json={
                "category": category,
                "value": f"val1_{uid}",
                "label": "Label 1",
                "sort_order": 0,
            }
        )
        resp2 = await client.post(
            "/api/settings/lookups",
            json={
                "category": category,
                "value": f"val2_{uid}",
                "label": "Label 2",
                "sort_order": 1,
            }
        )
        assert resp1.status_code == 201
        assert resp2.status_code == 201
        id1 = resp1.json()["id"]
        id2 = resp2.json()["id"]

        # Reorder
        response = await client.post(
            f"/api/settings/lookups/{category}/reorder",
            json=[id2, id1]  # Reverse order
        )
        assert response.status_code == 200

        # Clean up
        await client.delete(f"/api/settings/lookups/{id1}?hard_delete=true")
        await client.delete(f"/api/settings/lookups/{id2}?hard_delete=true")
