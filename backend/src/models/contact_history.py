"""
Contact History Model.

Stores the interaction timeline for contacts including notes,
calls, emails, and system-generated events.
"""

from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, Text, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from src.core.database import Base
from src.models.base import TimestampMixin

if TYPE_CHECKING:
    from src.models.contact import Contact


class HistoryType(str, enum.Enum):
    """
    Contact history entry type.

    Manual entries: note, call, email, meeting.
    System-generated: status_change, task_created, data_change, lead_created.
    """

    NOTE = "note"
    CALL = "call"
    EMAIL = "email"
    MEETING = "meeting"
    STATUS_CHANGE = "status_change"
    TASK_CREATED = "task_created"
    DATA_CHANGE = "data_change"
    LEAD_CREATED = "lead_created"


class ContactHistory(Base, TimestampMixin):
    """
    Contact interaction timeline entry.

    Tracks all interactions and changes for a contact in chronological order.
    Extra metadata can be stored as JSON in extra_data field.
    """

    __tablename__ = "contact_history"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    type: Mapped[HistoryType] = mapped_column(
        Enum(HistoryType), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extra_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON for additional data
    created_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Foreign Keys
    contact_id: Mapped[int] = mapped_column(
        ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Relationships
    contact: Mapped["Contact"] = relationship("Contact", back_populates="history")

    def __repr__(self) -> str:
        return f"<ContactHistory(id={self.id}, type='{self.type.value}')>"
