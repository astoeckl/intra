from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.setting import Setting
from src.models.lookup_value import LookupValue
from src.schemas.setting import (
    SettingCreate,
    SettingUpdate,
    LookupValueCreate,
    LookupValueUpdate,
)


# ============ Setting Service Functions ============

async def get_all_settings(
    db: AsyncSession,
    category: Optional[str] = None,
) -> Sequence[Setting]:
    """Get all settings, optionally filtered by category."""
    query = select(Setting)
    
    if category:
        query = query.where(Setting.category == category)
    
    query = query.order_by(Setting.category, Setting.key)
    result = await db.execute(query)
    return result.scalars().all()


async def get_setting(db: AsyncSession, key: str) -> Optional[Setting]:
    """Get a single setting by key."""
    result = await db.execute(select(Setting).where(Setting.key == key))
    return result.scalar_one_or_none()


async def get_setting_by_id(db: AsyncSession, setting_id: int) -> Optional[Setting]:
    """Get a single setting by ID."""
    result = await db.execute(select(Setting).where(Setting.id == setting_id))
    return result.scalar_one_or_none()


async def create_setting(db: AsyncSession, setting_data: SettingCreate) -> Setting:
    """Create a new setting."""
    setting = Setting(**setting_data.model_dump())
    db.add(setting)
    await db.flush()
    await db.refresh(setting)
    return setting


async def update_setting(
    db: AsyncSession,
    key: str,
    setting_data: SettingUpdate,
) -> Optional[Setting]:
    """Update an existing setting by key."""
    setting = await get_setting(db, key)
    if not setting:
        return None
    
    update_data = setting_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(setting, field, value)
    
    await db.flush()
    await db.refresh(setting)
    return setting


async def upsert_setting(
    db: AsyncSession,
    key: str,
    category: str,
    value: Optional[str],
    value_type: str = "string",
) -> Setting:
    """Create or update a setting by key."""
    setting = await get_setting(db, key)
    
    if setting:
        setting.value = value
        setting.value_type = value_type
        await db.flush()
        await db.refresh(setting)
        return setting
    else:
        new_setting = Setting(
            key=key,
            category=category,
            value=value,
            value_type=value_type,
        )
        db.add(new_setting)
        await db.flush()
        await db.refresh(new_setting)
        return new_setting


async def delete_setting(db: AsyncSession, key: str) -> bool:
    """Delete a setting by key."""
    setting = await get_setting(db, key)
    if not setting:
        return False
    
    await db.delete(setting)
    return True


# ============ LookupValue Service Functions ============

async def get_lookup_values(
    db: AsyncSession,
    category: str,
    include_inactive: bool = False,
) -> Sequence[LookupValue]:
    """Get all lookup values for a category."""
    query = select(LookupValue).where(LookupValue.category == category)
    
    if not include_inactive:
        query = query.where(LookupValue.is_active == True)
    
    query = query.order_by(LookupValue.sort_order, LookupValue.label)
    result = await db.execute(query)
    return result.scalars().all()


async def get_all_lookup_categories(db: AsyncSession) -> list[str]:
    """Get all unique lookup categories."""
    query = select(LookupValue.category).distinct().order_by(LookupValue.category)
    result = await db.execute(query)
    return [row[0] for row in result.all()]


async def get_lookup_value(db: AsyncSession, lookup_id: int) -> Optional[LookupValue]:
    """Get a single lookup value by ID."""
    result = await db.execute(
        select(LookupValue).where(LookupValue.id == lookup_id)
    )
    return result.scalar_one_or_none()


async def get_lookup_value_by_category_and_value(
    db: AsyncSession,
    category: str,
    value: str,
) -> Optional[LookupValue]:
    """Get a lookup value by category and value."""
    result = await db.execute(
        select(LookupValue).where(
            LookupValue.category == category,
            LookupValue.value == value,
        )
    )
    return result.scalar_one_or_none()


async def create_lookup_value(
    db: AsyncSession,
    lookup_data: LookupValueCreate,
) -> LookupValue:
    """Create a new lookup value."""
    lookup = LookupValue(**lookup_data.model_dump())
    db.add(lookup)
    await db.flush()
    await db.refresh(lookup)
    return lookup


async def update_lookup_value(
    db: AsyncSession,
    lookup_id: int,
    lookup_data: LookupValueUpdate,
) -> Optional[LookupValue]:
    """Update an existing lookup value."""
    lookup = await get_lookup_value(db, lookup_id)
    if not lookup:
        return None
    
    update_data = lookup_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lookup, field, value)
    
    await db.flush()
    await db.refresh(lookup)
    return lookup


async def delete_lookup_value(
    db: AsyncSession,
    lookup_id: int,
    soft_delete: bool = True,
) -> bool:
    """Delete a lookup value (soft delete by default)."""
    lookup = await get_lookup_value(db, lookup_id)
    if not lookup:
        return False
    
    if soft_delete:
        lookup.is_active = False
        await db.flush()
    else:
        await db.delete(lookup)
    
    return True


async def reorder_lookup_values(
    db: AsyncSession,
    category: str,
    ordered_ids: list[int],
) -> bool:
    """Reorder lookup values by setting sort_order based on list position."""
    for index, lookup_id in enumerate(ordered_ids):
        lookup = await get_lookup_value(db, lookup_id)
        if lookup and lookup.category == category:
            lookup.sort_order = index
    
    await db.flush()
    return True
