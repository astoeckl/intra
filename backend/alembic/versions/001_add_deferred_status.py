"""Add deferred status to taskstatus enum

Revision ID: 001_add_deferred
Revises:
Create Date: 2026-01-14

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = '001_add_deferred'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if the enum type exists and add 'DEFERRED' value if it does
    # This must run outside of a transaction for PostgreSQL enum ALTER
    connection = op.get_bind()

    # Check if taskstatus enum exists
    result = connection.execute(text(
        "SELECT 1 FROM pg_type WHERE typname = 'taskstatus'"
    ))
    if result.fetchone():
        # Check if 'DEFERRED' already exists in the enum
        result = connection.execute(text(
            "SELECT 1 FROM pg_enum WHERE enumtypid = "
            "(SELECT oid FROM pg_type WHERE typname = 'taskstatus') "
            "AND enumlabel = 'DEFERRED'"
        ))
        if not result.fetchone():
            # Commit current transaction and add enum value outside transaction
            connection.execute(text("COMMIT"))
            connection.execute(text(
                "ALTER TYPE taskstatus ADD VALUE 'DEFERRED' AFTER 'IN_PROGRESS'"
            ))


def downgrade() -> None:
    # PostgreSQL doesn't support removing enum values directly
    # For simplicity, we leave this as a no-op
    pass
