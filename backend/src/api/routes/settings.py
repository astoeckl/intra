from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.schemas.setting import (
    SettingCreate,
    SettingUpdate,
    SettingResponse,
    LookupValueCreate,
    LookupValueUpdate,
    LookupValueResponse,
)
from src.services import setting_service

router = APIRouter()


# ============ Lookup Values Endpoints ============
# NOTE: These MUST come before the /{key:path} routes to avoid being caught by the wildcard

@router.get("/lookups/categories", response_model=list[str])
async def list_lookup_categories(
    db: AsyncSession = Depends(get_db),
):
    """Get all available lookup categories."""
    categories = await setting_service.get_all_lookup_categories(db)
    return categories


@router.get("/lookups/{category}", response_model=list[LookupValueResponse])
async def list_lookup_values(
    category: str,
    include_inactive: bool = Query(False),
    db: AsyncSession = Depends(get_db),
):
    """Get all lookup values for a category."""
    lookups = await setting_service.get_lookup_values(
        db, category=category, include_inactive=include_inactive
    )
    return [LookupValueResponse.model_validate(lv) for lv in lookups]


@router.post("/lookups", response_model=LookupValueResponse, status_code=201)
async def create_lookup_value(
    lookup_data: LookupValueCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new lookup value."""
    existing = await setting_service.get_lookup_value_by_category_and_value(
        db, lookup_data.category, lookup_data.value
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Lookup value '{lookup_data.value}' already exists in category '{lookup_data.category}'",
        )
    
    lookup = await setting_service.create_lookup_value(db, lookup_data)
    return LookupValueResponse.model_validate(lookup)


@router.put("/lookups/{lookup_id}", response_model=LookupValueResponse)
async def update_lookup_value(
    lookup_id: int,
    lookup_data: LookupValueUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing lookup value."""
    lookup = await setting_service.update_lookup_value(db, lookup_id, lookup_data)
    if not lookup:
        raise HTTPException(status_code=404, detail="Lookup value not found")
    return LookupValueResponse.model_validate(lookup)


@router.delete("/lookups/{lookup_id}", status_code=200)
async def delete_lookup_value(
    lookup_id: int,
    hard_delete: bool = Query(False),
    db: AsyncSession = Depends(get_db),
):
    """Delete a lookup value (soft delete by default)."""
    deleted = await setting_service.delete_lookup_value(
        db, lookup_id, soft_delete=not hard_delete
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Lookup value not found")
    return {"message": "Lookup value deleted"}


@router.post("/lookups/{category}/reorder", status_code=200)
async def reorder_lookup_values(
    category: str,
    ordered_ids: list[int],
    db: AsyncSession = Depends(get_db),
):
    """Reorder lookup values by providing an ordered list of IDs."""
    await setting_service.reorder_lookup_values(db, category, ordered_ids)
    return {"message": "Lookup values reordered"}


# ============ Settings Endpoints ============

@router.get("", response_model=list[SettingResponse])
async def list_settings(
    category: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Get all settings, optionally filtered by category."""
    settings = await setting_service.get_all_settings(db, category=category)
    return [SettingResponse.model_validate(s) for s in settings]


@router.post("", response_model=SettingResponse, status_code=201)
async def create_setting(
    setting_data: SettingCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new setting."""
    existing = await setting_service.get_setting(db, setting_data.key)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Setting with key '{setting_data.key}' already exists",
        )
    
    setting = await setting_service.create_setting(db, setting_data)
    return SettingResponse.model_validate(setting)


@router.get("/{key:path}", response_model=SettingResponse)
async def get_setting(
    key: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a single setting by key."""
    setting = await setting_service.get_setting(db, key)
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return SettingResponse.model_validate(setting)


@router.put("/{key:path}", response_model=SettingResponse)
async def update_setting(
    key: str,
    setting_data: SettingUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing setting."""
    setting = await setting_service.update_setting(db, key, setting_data)
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return SettingResponse.model_validate(setting)


@router.delete("/{key:path}", status_code=204)
async def delete_setting(
    key: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a setting."""
    deleted = await setting_service.delete_setting(db, key)
    if not deleted:
        raise HTTPException(status_code=404, detail="Setting not found")
