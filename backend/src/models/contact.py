from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, Text, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base
from src.models.base import TimestampMixin

if TYPE_CHECKING:
    from src.models.company import Company
    from src.models.lead import Lead
    from src.models.task import Task
    from src.models.contact_history import ContactHistory


class Contact(Base, TimestampMixin):
    """Contact/Kontakt model."""
    
    __tablename__ = "contacts"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    mobile: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    position: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    salutation: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # Herr, Frau
    title: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # Dr., Mag., etc.
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Foreign Keys
    company_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("companies.id", ondelete="SET NULL"), nullable=True
    )
    
    # Relationships
    company: Mapped[Optional["Company"]] = relationship(
        "Company", back_populates="contacts"
    )
    leads: Mapped[list["Lead"]] = relationship(
        "Lead", back_populates="contact", cascade="all, delete-orphan"
    )
    tasks: Mapped[list["Task"]] = relationship(
        "Task", back_populates="contact", cascade="all, delete-orphan"
    )
    history: Mapped[list["ContactHistory"]] = relationship(
        "ContactHistory", back_populates="contact", cascade="all, delete-orphan"
    )
    
    @property
    def full_name(self) -> str:
        """Return full name with optional title."""
        parts = []
        if self.title:
            parts.append(self.title)
        parts.extend([self.first_name, self.last_name])
        return " ".join(parts)
    
    def __repr__(self) -> str:
        return f"<Contact(id={self.id}, name='{self.full_name}')>"
