from typing import Optional, Sequence
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
import json
import re

from src.models.email_template import EmailTemplate
from src.models.contact import Contact
from src.models.company import Company
from src.schemas.email_template import EmailTemplateCreate, EmailTemplateUpdate
from src.services import history_service


async def get_templates(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    is_active: Optional[bool] = None,
    category: Optional[str] = None,
) -> tuple[Sequence[EmailTemplate], int]:
    """Get all email templates with pagination."""
    query = select(EmailTemplate)
    count_query = select(func.count(EmailTemplate.id))
    
    filters = []
    if is_active is not None:
        filters.append(EmailTemplate.is_active == is_active)
    if category:
        filters.append(EmailTemplate.category == category)
    
    if filters:
        query = query.where(*filters)
        count_query = count_query.where(*filters)
    
    query = query.order_by(EmailTemplate.name).offset(skip).limit(limit)
    
    result = await db.execute(query)
    templates = result.scalars().all()
    
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0
    
    return templates, total


async def get_template(db: AsyncSession, template_id: int) -> Optional[EmailTemplate]:
    """Get a single email template by ID."""
    result = await db.execute(
        select(EmailTemplate).where(EmailTemplate.id == template_id)
    )
    return result.scalar_one_or_none()


async def create_template(
    db: AsyncSession, template_data: EmailTemplateCreate
) -> EmailTemplate:
    """Create a new email template."""
    data = template_data.model_dump()
    if data.get("variables"):
        data["variables"] = json.dumps(data["variables"])
    
    template = EmailTemplate(**data)
    db.add(template)
    await db.flush()
    await db.refresh(template)
    return template


async def update_template(
    db: AsyncSession, template_id: int, template_data: EmailTemplateUpdate
) -> Optional[EmailTemplate]:
    """Update an existing email template."""
    template = await get_template(db, template_id)
    if not template:
        return None
    
    update_data = template_data.model_dump(exclude_unset=True)
    if "variables" in update_data and update_data["variables"]:
        update_data["variables"] = json.dumps(update_data["variables"])
    
    for field, value in update_data.items():
        setattr(template, field, value)
    
    await db.flush()
    await db.refresh(template)
    return template


def _replace_variables(text: str, contact: Contact, company: Optional[Company]) -> str:
    """Replace template variables with actual values."""
    replacements = {
        "{{contact.first_name}}": contact.first_name,
        "{{contact.last_name}}": contact.last_name,
        "{{contact.full_name}}": contact.full_name,
        "{{contact.email}}": contact.email or "",
        "{{contact.phone}}": contact.phone or "",
        "{{contact.position}}": contact.position or "",
        "{{contact.salutation}}": contact.salutation or "",
        "{{contact.title}}": contact.title or "",
        "{{company.name}}": company.name if company else "",
        "{{company.city}}": company.city if company else "",
        "{{company.website}}": company.website if company else "",
    }
    
    for var, value in replacements.items():
        text = text.replace(var, value)
    
    return text


async def preview_email(
    db: AsyncSession, template_id: int, contact_id: int
) -> Optional[dict]:
    """Generate email preview with replaced variables."""
    from src.services import contact_service
    
    template = await get_template(db, template_id)
    if not template:
        return None
    
    contact = await contact_service.get_contact(db, contact_id)
    if not contact:
        return None
    
    company = contact.company
    
    return {
        "subject": _replace_variables(template.subject, contact, company),
        "body": _replace_variables(template.body, contact, company),
        "to_email": contact.email or "",
        "to_name": contact.full_name,
    }


async def send_email(
    db: AsyncSession,
    template_id: int,
    contact_id: int,
    subject_override: Optional[str] = None,
    created_by: Optional[str] = None,
) -> bool:
    """Send an email using a template."""
    from src.services import contact_service
    from src.core.config import get_settings
    
    # Get template and contact
    template = await get_template(db, template_id)
    if not template:
        return False
    
    contact = await contact_service.get_contact(db, contact_id)
    if not contact or not contact.email:
        return False
    
    company = contact.company
    
    # Replace variables
    subject = subject_override or _replace_variables(template.subject, contact, company)
    body = _replace_variables(template.body, contact, company)
    
    # TODO: Actually send email via SMTP
    # settings = get_settings()
    # async with aiosmtplib.SMTP(hostname=settings.smtp_host, port=settings.smtp_port) as smtp:
    #     await smtp.login(settings.smtp_user, settings.smtp_password)
    #     message = MIMEText(body)
    #     message["Subject"] = subject
    #     message["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
    #     message["To"] = contact.email
    #     await smtp.send_message(message)
    
    # Log to history
    await history_service.add_email_sent(
        db, contact_id, subject, template.name, created_by
    )
    
    return True
