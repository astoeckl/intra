from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.schemas.email_template import (
    EmailTemplateCreate,
    EmailTemplateUpdate,
    EmailTemplateResponse,
    EmailSend,
    EmailPreview,
    EmailPreviewResponse,
)
from src.schemas.base import PaginatedResponse
from src.services import email_service
import json

router = APIRouter()


@router.get("", response_model=PaginatedResponse)
async def list_templates(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_active: bool = Query(None),
    category: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Get all email templates with pagination."""
    skip = (page - 1) * page_size
    templates, total = await email_service.get_templates(
        db, skip=skip, limit=page_size, is_active=is_active, category=category
    )
    
    items = []
    for t in templates:
        response = EmailTemplateResponse.model_validate(t)
        if t.variables:
            response.variables = json.loads(t.variables)
        items.append(response)
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/{template_id}", response_model=EmailTemplateResponse)
async def get_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a single email template by ID."""
    template = await email_service.get_template(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    response = EmailTemplateResponse.model_validate(template)
    if template.variables:
        response.variables = json.loads(template.variables)
    return response


@router.post("", response_model=EmailTemplateResponse, status_code=201)
async def create_template(
    template_data: EmailTemplateCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new email template."""
    template = await email_service.create_template(db, template_data)
    return EmailTemplateResponse.model_validate(template)


@router.put("/{template_id}", response_model=EmailTemplateResponse)
async def update_template(
    template_id: int,
    template_data: EmailTemplateUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing email template."""
    template = await email_service.update_template(db, template_id, template_data)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return EmailTemplateResponse.model_validate(template)


@router.post("/preview", response_model=EmailPreviewResponse)
async def preview_email(
    preview_data: EmailPreview,
    db: AsyncSession = Depends(get_db),
):
    """Preview an email with replaced variables."""
    result = await email_service.preview_email(
        db, preview_data.template_id, preview_data.contact_id
    )
    if not result:
        raise HTTPException(status_code=404, detail="Template or contact not found")
    return EmailPreviewResponse(**result)


@router.post("/send")
async def send_email(
    send_data: EmailSend,
    db: AsyncSession = Depends(get_db),
):
    """Send an email using a template."""
    # TODO: Get actual user from auth context
    current_user = "current_user"
    
    success = await email_service.send_email(
        db,
        send_data.template_id,
        send_data.contact_id,
        send_data.subject_override,
        created_by=current_user,
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to send email")
    
    return {"status": "sent"}
