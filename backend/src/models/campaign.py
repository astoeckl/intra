from typing import TYPE_CHECKING, Optional
from datetime import date
from sqlalchemy import String, Text, Date, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base
from src.models.base import TimestampMixin

if TYPE_CHECKING:
    from src.models.lead import Lead


class Campaign(Base, TimestampMixin):
    """Campaign/Kampagne model."""
    
    __tablename__ = "campaigns"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # social_media, email, landing_page
    source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # facebook, google, linkedin
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    landing_page_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    lead_magnet: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # File/resource name
    
    # Relationships
    leads: Mapped[list["Lead"]] = relationship(
        "Lead", back_populates="campaign"
    )
    
    def __repr__(self) -> str:
        return f"<Campaign(id={self.id}, name='{self.name}')>"
