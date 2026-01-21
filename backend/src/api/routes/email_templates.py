"""
Email Template API Routes.

Provides CRUD operations for email templates, preview functionality
with variable substitution, and email sending capabilities.
"""

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
    """
    List email templates with filtering and pagination.

    Args:
        page: Page number (1-indexed).
        page_size: Number of items per page (max 100).
        is_active: Filter by active status. None returns all.
        category: Filter by template category.

    Returns:
        Paginated list of templates with parsed JSON variables.
    """
    skip = (page - 1) * page_size
    templates, total = await email_service.get_templates(
        db, skip=skip, limit=page_size, is_active=is_active, category=category
    )

    items = []
    for t in templates:
        response = EmailTemplateResponse.model_validate(t)
        # Variables are stored as JSON string in DB, parse for response
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
    """
    Retrieve a single email template by ID.

    Args:
        template_id: Unique identifier of the template.

    Returns:
        Template details with parsed variables.

    Raises:
        HTTPException 404: Template does not exist.
    """
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
    """
    Create a new email template.

    Args:
        template_data: Template name, subject, body, and optional variables.

    Returns:
        Created template with assigned ID.
    """
    template = await email_service.create_template(db, template_data)
    return EmailTemplateResponse.model_validate(template)


@router.put("/{template_id}", response_model=EmailTemplateResponse)
async def update_template(
    template_id: int,
    template_data: EmailTemplateUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update an existing email template.

    Args:
        template_id: Unique identifier of the template to update.
        template_data: Fields to update. Only provided fields are modified.

    Returns:
        Updated template.

    Raises:
        HTTPException 404: Template does not exist.
    """
    template = await email_service.update_template(db, template_id, template_data)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return EmailTemplateResponse.model_validate(template)


@router.post("/preview", response_model=EmailPreviewResponse)
async def preview_email(
    preview_data: EmailPreview,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate email preview with variable substitution.

    Replaces template placeholders with actual contact data
    to show how the final email will appear.

    Args:
        preview_data: Template ID and contact ID for variable resolution.

    Returns:
        Rendered subject and body with substituted values.

    Raises:
        HTTPException 404: Template or contact does not exist.
    """
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
    """
    Send an email using a template.

    Renders the template with contact data and dispatches the email.
    Subject can be overridden for one-off customization.

    Args:
        send_data: Template ID, contact ID, and optional subject override.

    Returns:
        Status confirmation on successful dispatch.

    Raises:
        HTTPException 400: Email dispatch failed (invalid data or service error).
    """
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
