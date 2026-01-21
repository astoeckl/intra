"""
Base Model Mixins.

Provides reusable SQLAlchemy model components.
"""

from datetime import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class TimestampMixin:
    """
    Mixin providing automatic timestamp fields.

    Adds created_at (set on insert) and updated_at (set on insert/update)
    columns with timezone-aware datetime values.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
