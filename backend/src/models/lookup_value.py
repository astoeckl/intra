from sqlalchemy import String, Integer, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base
from src.models.base import TimestampMixin


class LookupValue(Base, TimestampMixin):
    """Lookup values model for configurable dropdown options."""
    
    __tablename__ = "lookup_values"
    __table_args__ = (
        UniqueConstraint("category", "value", name="uq_lookup_category_value"),
    )
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    value: Mapped[str] = mapped_column(String(100), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    def __repr__(self) -> str:
        return f"<LookupValue(id={self.id}, category='{self.category}', value='{self.value}')>"
