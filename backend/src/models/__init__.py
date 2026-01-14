# Models module - all models imported for Alembic
from src.models.base import TimestampMixin
from src.models.company import Company
from src.models.contact import Contact
from src.models.campaign import Campaign
from src.models.lead import Lead, LeadStatus
from src.models.task import Task, TaskStatus, TaskPriority
from src.models.contact_history import ContactHistory, HistoryType
from src.models.email_template import EmailTemplate
from src.models.setting import Setting
from src.models.lookup_value import LookupValue

__all__ = [
    "TimestampMixin",
    "Company",
    "Contact",
    "Campaign",
    "Lead",
    "LeadStatus",
    "Task",
    "TaskStatus",
    "TaskPriority",
    "ContactHistory",
    "HistoryType",
    "EmailTemplate",
    "Setting",
    "LookupValue",
]
