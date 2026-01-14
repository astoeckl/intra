"""Public endpoints for landing pages (no auth required)."""
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
    """Public endpoint for landing page form submissions."""
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
    """Get public campaign info for landing page."""
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
