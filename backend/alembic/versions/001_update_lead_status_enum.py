"""Update lead status enum: new->cold, contacted->warm, qualified->hot, converted->to_be_done

Revision ID: 001_update_lead_status_enum
Revises: 
Create Date: 2026-01-14
"""
from typing import Sequence, Union
from alembic import op

revision: str = '001_update_lead_status_enum'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE leadstatus RENAME TO leadstatus_old")
    op.execute("CREATE TYPE leadstatus AS ENUM ('cold', 'warm', 'hot', 'to_be_done', 'disqualified')")
    op.execute("""
        ALTER TABLE leads 
        ALTER COLUMN status TYPE leadstatus 
        USING CASE 
            WHEN status::text = 'new' THEN 'cold'::leadstatus
            WHEN status::text = 'contacted' THEN 'warm'::leadstatus
            WHEN status::text = 'qualified' THEN 'hot'::leadstatus
            WHEN status::text = 'converted' THEN 'to_be_done'::leadstatus
            ELSE 'cold'::leadstatus
        END
    """)
    op.execute("DROP TYPE leadstatus_old")


def downgrade() -> None:
    op.execute("ALTER TYPE leadstatus RENAME TO leadstatus_new")
    op.execute("CREATE TYPE leadstatus AS ENUM ('new', 'contacted', 'qualified', 'converted', 'disqualified')")
    op.execute("""
        ALTER TABLE leads 
        ALTER COLUMN status TYPE leadstatus 
        USING CASE 
            WHEN status::text = 'cold' THEN 'new'::leadstatus
            WHEN status::text = 'warm' THEN 'contacted'::leadstatus
            WHEN status::text = 'hot' THEN 'qualified'::leadstatus
            WHEN status::text = 'to_be_done' THEN 'converted'::leadstatus
            ELSE 'new'::leadstatus
        END
    """)
    op.execute("DROP TYPE leadstatus_new")
