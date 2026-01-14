# Pydantic Schemas module
from src.schemas.base import BaseSchema, TimestampSchema, PaginationParams, PaginatedResponse
from src.schemas.company import (
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
    CompanyListResponse,
)
from src.schemas.contact import (
    ContactCreate,
    ContactUpdate,
    ContactResponse,
    ContactListResponse,
    ContactSearchResult,
)
from src.schemas.campaign import (
    CampaignCreate,
    CampaignUpdate,
    CampaignResponse,
    CampaignListResponse,
)
from src.schemas.lead import (
    LeadCreate,
    LeadCreateFromForm,
    LeadUpdate,
    LeadImportRow,
    LeadImportResult,
    LeadResponse,
    LeadListResponse,
)
from src.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskComplete,
    TaskResponse,
    TaskListResponse,
)
from src.schemas.contact_history import (
    ContactHistoryResponse,
    NoteCreate,
    CallCreate,
)
from src.schemas.email_template import (
    EmailTemplateCreate,
    EmailTemplateUpdate,
    EmailTemplateResponse,
    EmailSend,
    EmailPreview,
    EmailPreviewResponse,
)
from src.schemas.setting import (
    SettingCreate,
    SettingUpdate,
    SettingResponse,
    LookupValueCreate,
    LookupValueUpdate,
    LookupValueResponse,
    LOOKUP_CATEGORIES,
)

__all__ = [
    # Base
    "BaseSchema",
    "TimestampSchema",
    "PaginationParams",
    "PaginatedResponse",
    # Company
    "CompanyCreate",
    "CompanyUpdate",
    "CompanyResponse",
    "CompanyListResponse",
    # Contact
    "ContactCreate",
    "ContactUpdate",
    "ContactResponse",
    "ContactListResponse",
    "ContactSearchResult",
    # Campaign
    "CampaignCreate",
    "CampaignUpdate",
    "CampaignResponse",
    "CampaignListResponse",
    # Lead
    "LeadCreate",
    "LeadCreateFromForm",
    "LeadUpdate",
    "LeadImportRow",
    "LeadImportResult",
    "LeadResponse",
    "LeadListResponse",
    # Task
    "TaskCreate",
    "TaskUpdate",
    "TaskComplete",
    "TaskResponse",
    "TaskListResponse",
    # Contact History
    "ContactHistoryResponse",
    "NoteCreate",
    "CallCreate",
    # Email Template
    "EmailTemplateCreate",
    "EmailTemplateUpdate",
    "EmailTemplateResponse",
    "EmailSend",
    "EmailPreview",
    "EmailPreviewResponse",
    # Setting
    "SettingCreate",
    "SettingUpdate",
    "SettingResponse",
    "LookupValueCreate",
    "LookupValueUpdate",
    "LookupValueResponse",
    "LOOKUP_CATEGORIES",
]
