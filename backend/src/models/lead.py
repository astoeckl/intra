from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, Text, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from src.core.database import Base
from src.models.base import TimestampMixin

if TYPE_CHECKING:
    from src.models.contact import Contact
    from src.models.campaign import Campaign


class LeadStatus(str, enum.Enum):
    COLD = "cold"
    WARM = "warm"
    HOT = "hot"
    TO_BE_DONE = "to_be_done"
    DISQUALIFIED = "disqualified"


class Lead(Base, TimestampMixin):
    __tablename__ = "leads"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    status: Mapped[LeadStatus] = mapped_column(
        Enum(LeadStatus, values_callable=lambda x: [e.value for e in x]),
        default=LeadStatus.COLD, nullable=False, index=True
    )
    source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    utm_source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    utm_medium: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    utm_campaign: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    contact_id: Mapped[int] = mapped_column(
        ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    campaign_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("campaigns.id", ondelete="SET NULL"), nullable=True
    )
    
    contact: Mapped["Contact"] = relationship("Contact", back_populates="leads")
    campaign: Mapped[Optional["Campaign"]] = relationship("Campaign", back_populates="leads")
    
    def __repr__(self) -> str:
        return f"<Lead(id={self.id}, status='{self.status.value}')>"
