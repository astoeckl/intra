from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base
from src.models.base import TimestampMixin

if TYPE_CHECKING:
    from src.models.contact import Contact


class Company(Base, TimestampMixin):
    """Company/Firma model."""
    
    __tablename__ = "companies"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    street: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    zip_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country: Mapped[str] = mapped_column(String(100), default="Österreich")
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    employee_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    potential_category: Mapped[Optional[str]] = mapped_column(
        String(1), nullable=True
    )  # A, B, C, D
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    contacts: Mapped[list["Contact"]] = relationship(
        "Contact", back_populates="company", cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Company(id={self.id}, name='{self.name}')>"
