from typing import Optional, Sequence
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import pandas as pd
from io import BytesIO

from src.models.lead import Lead, LeadStatus
from src.models.contact import Contact
from src.models.company import Company
from src.models.campaign import Campaign
from src.models.contact_history import ContactHistory, HistoryType
from src.schemas.lead import LeadCreate, LeadUpdate, LeadCreateFromForm, LeadImportResult
from src.services import contact_service, company_service


async def get_leads(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    status: Optional[LeadStatus] = None,
    campaign_id: Optional[int] = None,
) -> tuple[Sequence[Lead], int]:
    query = (
        select(Lead)
        .options(
            selectinload(Lead.contact).selectinload(Contact.company),
            selectinload(Lead.campaign),
        )
    )
    count_query = select(func.count(Lead.id))
    
    filters = []
    if status:
        filters.append(Lead.status == status)
    if campaign_id:
        filters.append(Lead.campaign_id == campaign_id)
    
    if filters:
        query = query.where(*filters)
        count_query = count_query.where(*filters)
    
    query = query.order_by(Lead.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    leads = result.scalars().all()
    
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0
    
    return leads, total


async def get_lead(db: AsyncSession, lead_id: int) -> Optional[Lead]:
    result = await db.execute(
        select(Lead)
        .options(
            selectinload(Lead.contact).selectinload(Contact.company),
            selectinload(Lead.campaign),
        )
        .where(Lead.id == lead_id)
    )
    return result.scalar_one_or_none()


async def create_lead(db: AsyncSession, lead_data: LeadCreate) -> Lead:
    lead = Lead(**lead_data.model_dump())
    db.add(lead)
    await db.flush()
    
    history = ContactHistory(
        contact_id=lead.contact_id,
        type=HistoryType.LEAD_CREATED,
        title="Lead created",
        content=f"New lead from source: {lead.source or 'unknown'}",
    )
    db.add(history)
    
    await db.flush()
    return await get_lead(db, lead.id)


async def create_lead_from_form(
    db: AsyncSession, form_data: LeadCreateFromForm
) -> Lead:
    company_id = None
    if form_data.company_name:
        company = await company_service.get_company_by_name(db, form_data.company_name)
        if not company:
            from src.schemas.company import CompanyCreate
            company = await company_service.create_company(
                db, CompanyCreate(name=form_data.company_name)
            )
        company_id = company.id
    
    contact, _ = await contact_service.get_or_create_contact_by_email(
        db,
        email=form_data.email,
        first_name=form_data.first_name,
        last_name=form_data.last_name,
        phone=form_data.phone,
        company_id=company_id,
    )
    
    lead = Lead(
        contact_id=contact.id,
        campaign_id=form_data.campaign_id,
        source="landing_page",
        utm_source=form_data.utm_source,
        utm_medium=form_data.utm_medium,
        utm_campaign=form_data.utm_campaign,
        status=LeadStatus.COLD,
    )
    db.add(lead)
    await db.flush()
    
    history = ContactHistory(
        contact_id=contact.id,
        type=HistoryType.LEAD_CREATED,
        title="Lead from landing page",
        content="New lead captured via form submission",
    )
    db.add(history)
    
    await db.refresh(lead)
    return lead


async def update_lead(
    db: AsyncSession, lead_id: int, lead_data: LeadUpdate
) -> Optional[Lead]:
    lead = await get_lead(db, lead_id)
    if not lead:
        return None
    
    old_status = lead.status
    update_data = lead_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lead, field, value)
    
    if "status" in update_data and old_status != lead.status:
        history = ContactHistory(
            contact_id=lead.contact_id,
            type=HistoryType.STATUS_CHANGE,
            title="Lead status changed",
            content=f"Status changed from '{old_status.value}' to '{lead.status.value}'",
        )
        db.add(history)
    
    await db.flush()
    await db.refresh(lead)
    return lead


async def import_leads_from_file(
    db: AsyncSession, file_content: bytes, filename: str, campaign_id: Optional[int] = None
) -> LeadImportResult:
    errors: list[str] = []
    imported = 0
    
    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(BytesIO(file_content))
        elif filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(BytesIO(file_content))
        else:
            return LeadImportResult(
                total_rows=0, imported=0, failed=0,
                errors=["Invalid file format. Allowed: CSV, XLSX, XLS"],
            )
        
        total_rows = len(df)
        df.columns = df.columns.str.lower().str.strip()
        
        # Support both German and English column names
        col_mapping = {
            "vorname": "first_name", "nachname": "last_name",
            "telefon": "phone", "firma": "company"
        }
        df = df.rename(columns={k: v for k, v in col_mapping.items() if k in df.columns})
        
        if "first_name" not in df.columns or "last_name" not in df.columns:
            return LeadImportResult(
                total_rows=total_rows, imported=0, failed=total_rows,
                errors=["Required columns: first_name, last_name (or vorname, nachname)"],
            )
        
        for idx, row in df.iterrows():
            try:
                first_name = str(row.get("first_name", "")).strip()
                last_name = str(row.get("last_name", "")).strip()
                email = str(row.get("email", row.get("e-mail", ""))).strip() or None
                phone = str(row.get("phone", "")).strip() or None
                company_name = str(row.get("company", "")).strip() or None
                
                if not first_name or not last_name:
                    errors.append(f"Row {idx + 2}: Missing first_name or last_name")
                    continue
                
                comp_id = None
                if company_name:
                    company = await company_service.get_company_by_name(db, company_name)
                    if not company:
                        from src.schemas.company import CompanyCreate
                        company = await company_service.create_company(
                            db, CompanyCreate(name=company_name)
                        )
                    comp_id = company.id
                
                if email:
                    contact, _ = await contact_service.get_or_create_contact_by_email(
                        db, email=email, first_name=first_name, last_name=last_name,
                        phone=phone, company_id=comp_id,
                    )
                else:
                    from src.schemas.contact import ContactCreate
                    contact = await contact_service.create_contact(
                        db, ContactCreate(
                            first_name=first_name, last_name=last_name,
                            phone=phone, company_id=comp_id,
                        ),
                    )
                
                lead = Lead(
                    contact_id=contact.id, campaign_id=campaign_id,
                    source="import", status=LeadStatus.COLD,
                )
                db.add(lead)
                imported += 1
                
            except Exception as e:
                errors.append(f"Row {idx + 2}: {str(e)}")
        
        await db.flush()
        
        return LeadImportResult(
            total_rows=total_rows, imported=imported,
            failed=total_rows - imported, errors=errors[:10],
        )
        
    except Exception as e:
        return LeadImportResult(
            total_rows=0, imported=0, failed=0,
            errors=[f"Error reading file: {str(e)}"],
        )
