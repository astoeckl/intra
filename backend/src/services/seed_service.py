"""Seed service for populating default lookup values."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.lookup_value import LookupValue


# Default lookup values for all categories
DEFAULT_LOOKUP_VALUES = {
    "lead_status": [
        {"value": "new", "label": "Neu", "sort_order": 0},
        {"value": "contacted", "label": "Kontaktiert", "sort_order": 1},
        {"value": "qualified", "label": "Qualifiziert", "sort_order": 2},
        {"value": "converted", "label": "Konvertiert", "sort_order": 3},
        {"value": "disqualified", "label": "Disqualifiziert", "sort_order": 4},
    ],
    "potential_category": [
        {"value": "A", "label": "A - >20 Mitarbeiter", "sort_order": 0},
        {"value": "B", "label": "B - 10-20 Mitarbeiter", "sort_order": 1},
        {"value": "C", "label": "C - <10 Mitarbeiter", "sort_order": 2},
        {"value": "D", "label": "D - Einzelpraktiker", "sort_order": 3},
    ],
    "industry": [
        {"value": "tax_advisor", "label": "Steuerberater", "sort_order": 0},
        {"value": "lawyer", "label": "Rechtsanwalt", "sort_order": 1},
        {"value": "accountant", "label": "Wirtschaftsprüfer", "sort_order": 2},
        {"value": "notary", "label": "Notar", "sort_order": 3},
        {"value": "consultant", "label": "Unternehmensberater", "sort_order": 4},
        {"value": "other", "label": "Sonstige", "sort_order": 99},
    ],
    "country": [
        {"value": "AT", "label": "Österreich", "sort_order": 0},
        {"value": "DE", "label": "Deutschland", "sort_order": 1},
        {"value": "CH", "label": "Schweiz", "sort_order": 2},
        {"value": "LI", "label": "Liechtenstein", "sort_order": 3},
    ],
    "salutation": [
        {"value": "herr", "label": "Herr", "sort_order": 0},
        {"value": "frau", "label": "Frau", "sort_order": 1},
    ],
    "title": [
        {"value": "dr", "label": "Dr.", "sort_order": 0},
        {"value": "mag", "label": "Mag.", "sort_order": 1},
        {"value": "di", "label": "DI", "sort_order": 2},
        {"value": "prof", "label": "Prof.", "sort_order": 3},
        {"value": "mba", "label": "MBA", "sort_order": 4},
    ],
    "contact_lead_status": [
        {"value": "warm", "label": "Warm", "sort_order": 0},
        {"value": "cold", "label": "Cold", "sort_order": 1},
        {"value": "open", "label": "Offen", "sort_order": 2},
    ],
    "task_priority": [
        {"value": "low", "label": "Niedrig", "sort_order": 0},
        {"value": "medium", "label": "Mittel", "sort_order": 1},
        {"value": "high", "label": "Hoch", "sort_order": 2},
        {"value": "urgent", "label": "Dringend", "sort_order": 3},
    ],
    "campaign_type": [
        {"value": "social_media", "label": "Social Media", "sort_order": 0},
        {"value": "email", "label": "E-Mail", "sort_order": 1},
        {"value": "landing_page", "label": "Landing Page", "sort_order": 2},
        {"value": "event", "label": "Event", "sort_order": 3},
        {"value": "webinar", "label": "Webinar", "sort_order": 4},
    ],
    "campaign_source": [
        {"value": "facebook", "label": "Facebook", "sort_order": 0},
        {"value": "google", "label": "Google", "sort_order": 1},
        {"value": "linkedin", "label": "LinkedIn", "sort_order": 2},
        {"value": "instagram", "label": "Instagram", "sort_order": 3},
        {"value": "website", "label": "Website", "sort_order": 4},
        {"value": "referral", "label": "Empfehlung", "sort_order": 5},
    ],
}


async def seed_lookup_values(db: AsyncSession) -> dict[str, int]:
    """
    Seed default lookup values for all categories.
    
    This function is idempotent - it will only create values that don't exist.
    
    Returns:
        A dictionary mapping category names to the number of values created.
    """
    created_counts = {}
    
    for category, values in DEFAULT_LOOKUP_VALUES.items():
        created_count = 0
        
        for value_data in values:
            # Check if this lookup value already exists
            existing = await db.execute(
                select(LookupValue).where(
                    LookupValue.category == category,
                    LookupValue.value == value_data["value"],
                )
            )
            
            if existing.scalar_one_or_none() is None:
                # Create new lookup value
                lookup = LookupValue(
                    category=category,
                    value=value_data["value"],
                    label=value_data["label"],
                    sort_order=value_data["sort_order"],
                    is_active=True,
                )
                db.add(lookup)
                created_count += 1
        
        created_counts[category] = created_count
    
    await db.flush()
    return created_counts


async def get_seed_statistics(db: AsyncSession) -> dict[str, int]:
    """
    Get statistics about existing lookup values.
    
    Returns:
        A dictionary mapping category names to the number of values in each category.
    """
    stats = {}
    
    for category in DEFAULT_LOOKUP_VALUES.keys():
        result = await db.execute(
            select(LookupValue).where(LookupValue.category == category)
        )
        values = result.scalars().all()
        stats[category] = len(values)
    
    return stats
