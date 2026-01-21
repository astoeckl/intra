"""
Setting Model.

Key-value store for application configuration.
"""

from typing import Optional
from sqlalchemy import String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base
from src.models.base import TimestampMixin


class Setting(Base, TimestampMixin):
    """
    Application configuration setting.

    Stores key-value pairs organized by category. Value types (string, number,
    boolean, json) indicate how to parse the stored string value.
    """

    __tablename__ = "settings"
    __table_args__ = (
        UniqueConstraint("key", name="uq_settings_key"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    value_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="string"
    )  # string, number, boolean, json

    def __repr__(self) -> str:
        return f"<Setting(id={self.id}, key='{self.key}', category='{self.category}')>"
