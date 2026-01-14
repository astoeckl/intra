from typing import Optional
from sqlalchemy import String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base
from src.models.base import TimestampMixin


class EmailTemplate(Base, TimestampMixin):
    """Email template model."""
    
    __tablename__ = "email_templates"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    variables: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON list of variables
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # confirmation, reminder, etc.
    
    def __repr__(self) -> str:
        return f"<EmailTemplate(id={self.id}, name='{self.name}')>"
