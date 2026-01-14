"""add_opportunities_table

Revision ID: 1f1edf84ce57
Revises: 
Create Date: 2026-01-14 13:47:27.532351

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1f1edf84ce57'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create opportunities table
    op.create_table(
        'opportunities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('stage', sa.Enum('qualification', 'discovery', 'proposal', 'negotiation', 'closed_won', 'closed_lost', name='opportunitystage'), nullable=False),
        sa.Column('expected_value', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('probability', sa.Integer(), nullable=False),
        sa.Column('expected_close_date', sa.Date(), nullable=True),
        sa.Column('actual_close_date', sa.Date(), nullable=True),
        sa.Column('close_reason', sa.String(length=255), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('company_id', sa.Integer(), nullable=True),
        sa.Column('contact_id', sa.Integer(), nullable=True),
        sa.Column('lead_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['lead_id'], ['leads.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_opportunities_company_id'), 'opportunities', ['company_id'], unique=False)
    op.create_index(op.f('ix_opportunities_contact_id'), 'opportunities', ['contact_id'], unique=False)
    op.create_index(op.f('ix_opportunities_expected_close_date'), 'opportunities', ['expected_close_date'], unique=False)
    op.create_index(op.f('ix_opportunities_id'), 'opportunities', ['id'], unique=False)
    op.create_index(op.f('ix_opportunities_name'), 'opportunities', ['name'], unique=False)
    op.create_index(op.f('ix_opportunities_stage'), 'opportunities', ['stage'], unique=False)
    op.create_unique_constraint('uq_opportunities_lead_id', 'opportunities', ['lead_id'])
    
    # Add opportunity_id column to tasks table
    op.add_column('tasks', sa.Column('opportunity_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_tasks_opportunity_id', 'tasks', 'opportunities', ['opportunity_id'], ['id'], ondelete='SET NULL')


def downgrade() -> None:
    # Remove opportunity_id from tasks
    op.drop_constraint('fk_tasks_opportunity_id', 'tasks', type_='foreignkey')
    op.drop_column('tasks', 'opportunity_id')
    
    # Drop opportunities table
    op.drop_constraint('uq_opportunities_lead_id', 'opportunities', type_='unique')
    op.drop_index(op.f('ix_opportunities_stage'), table_name='opportunities')
    op.drop_index(op.f('ix_opportunities_name'), table_name='opportunities')
    op.drop_index(op.f('ix_opportunities_id'), table_name='opportunities')
    op.drop_index(op.f('ix_opportunities_expected_close_date'), table_name='opportunities')
    op.drop_index(op.f('ix_opportunities_contact_id'), table_name='opportunities')
    op.drop_index(op.f('ix_opportunities_company_id'), table_name='opportunities')
    op.drop_table('opportunities')
    
    # Drop the enum type
    op.execute('DROP TYPE IF EXISTS opportunitystage')
