from fastapi import APIRouter

from src.api.routes import (
    health,
    companies,
    contacts,
    campaigns,
    leads,
    tasks,
    contact_history,
    email_templates,
    public,
)

api_router = APIRouter()

# Include route modules
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(companies.router, prefix="/companies", tags=["Companies"])
api_router.include_router(contacts.router, prefix="/contacts", tags=["Contacts"])
api_router.include_router(contact_history.router, prefix="/contacts", tags=["Contact History"])
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["Campaigns"])
api_router.include_router(leads.router, prefix="/leads", tags=["Leads"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(email_templates.router, prefix="/email-templates", tags=["Email Templates"])
api_router.include_router(public.router, prefix="/public", tags=["Public"])
