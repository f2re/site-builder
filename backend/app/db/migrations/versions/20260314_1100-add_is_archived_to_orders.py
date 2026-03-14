"""add_is_archived_to_orders

Revision ID: 20260314_1100
Revises: 20260314_1000
Create Date: 2026-03-14 11:00:00.000000+00:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20260314_1100'
down_revision = '20260314_1000'
branch_labels = None
depends_on = None


def upgrade():
    # Add is_archived column with default False
    op.add_column('orders', sa.Column('is_archived', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    # Create index for is_archived
    op.create_index(op.f('ix_orders_is_archived'), 'orders', ['is_archived'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_orders_is_archived'), table_name='orders')
    op.drop_column('orders', 'is_archived')
