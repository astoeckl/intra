"""
Public API Routes.

Endpoints for landing pages and public-facing forms.
These endpoints do not require authentication.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.schemas.lead import LeadCreateFromForm
from src.services import lead_service

router = APIRouter()


@router.post("/leads")
async def submit_lead_form(
    lead_data: LeadCreateFromForm,
    db: AsyncSession = Depends(get_db),
):
    """
    Submit a lead capture form from landing page.

    Creates contact and lead records. Companies are created if not existing.
    Response messages are in German for end-user display.

    Args:
        lead_data: Form fields including name, email, and optional company.

    Returns:
        Success message in German.

    Raises:
        HTTPException 400: Processing error (generic message for security).
    """
    try:
        lead = await lead_service.create_lead_from_form(db, lead_data)

        # TODO: Send auto-email with lead magnet if campaign has one
        # if lead.campaign and lead.campaign.lead_magnet:
        #     await email_service.send_lead_magnet(db, lead.contact_id, lead.campaign.lead_magnet)

        return JSONResponse(
            status_code=201,
            content={
                "status": "success",
                "message": "Vielen Dank für Ihre Anfrage! Wir werden uns in Kürze bei Ihnen melden.",
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail="Fehler bei der Verarbeitung. Bitte versuchen Sie es erneut.",
        )


@router.get("/campaigns/{campaign_id}")
async def get_campaign_info(
    campaign_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve public campaign information for landing pages.

    Only returns active campaigns with limited public fields.

    Raises:
        HTTPException 404: Campaign not found or inactive.
    """
    from src.services import campaign_service

    campaign = await campaign_service.get_campaign(db, campaign_id)
    if not campaign or not campaign.is_active:
        raise HTTPException(status_code=404, detail="Campaign not found")

    return {
        "id": campaign.id,
        "name": campaign.name,
        "description": campaign.description,
        "lead_magnet": campaign.lead_magnet,
    }
