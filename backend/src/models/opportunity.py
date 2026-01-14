from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, Text, ForeignKey, Enum, Integer, Numeric, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date
import enum

from src.core.database import Base
from src.models.base import TimestampMixin

if TYPE_CHECKING:
    from src.models.company import Company
    from src.models.contact import Contact
    from src.models.lead import Lead
    from src.models.task import Task


class OpportunityStage(str, enum.Enum):
    QUALIFICATION = "qualification"
    DISCOVERY = "discovery"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


STAGE_DEFAULT_PROBABILITY = {
    OpportunityStage.QUALIFICATION: 10,
    OpportunityStage.DISCOVERY: 25,
    OpportunityStage.PROPOSAL: 50,
    OpportunityStage.NEGOTIATION: 75,
    OpportunityStage.CLOSED_WON: 100,
    OpportunityStage.CLOSED_LOST: 0,
}


class Opportunity(Base, TimestampMixin):
    __tablename__ = "opportunities"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    stage: Mapped[OpportunityStage] = mapped_column(
        Enum(OpportunityStage, values_callable=lambda x: [e.value for e in x]), 
        default=OpportunityStage.QUALIFICATION, 
        nullable=False, 
        index=True
    )
    expected_value: Mapped[Optional[float]] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    probability: Mapped[int] = mapped_column(
        Integer, default=10, nullable=False
    )
    expected_close_date: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, index=True
    )
    actual_close_date: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True
    )
    close_reason: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    company_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("companies.id", ondelete="SET NULL"), nullable=True, index=True
    )
    contact_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("contacts.id", ondelete="SET NULL"), nullable=True, index=True
    )
    lead_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("leads.id", ondelete="SET NULL"), nullable=True, unique=True
    )
    
    company: Mapped[Optional["Company"]] = relationship(
        "Company", back_populates="opportunities"
    )
    contact: Mapped[Optional["Contact"]] = relationship(
        "Contact", back_populates="opportunities"
    )
    lead: Mapped[Optional["Lead"]] = relationship(
        "Lead", back_populates="opportunity"
    )
    tasks: Mapped[list["Task"]] = relationship(
        "Task", back_populates="opportunity", cascade="all, delete-orphan"
    )
    
    @property
    def weighted_value(self) -> float:
        if self.expected_value is None:
            return 0.0
        return float(self.expected_value) * (self.probability / 100)
    
    @property
    def is_closed(self) -> bool:
        return self.stage in (OpportunityStage.CLOSED_WON, OpportunityStage.CLOSED_LOST)
    
    @property
    def is_won(self) -> bool:
        return self.stage == OpportunityStage.CLOSED_WON
    
    def __repr__(self) -> str:
        return f"<Opportunity(id={self.id}, name='{self.name}', stage='{self.stage.value}')>"
