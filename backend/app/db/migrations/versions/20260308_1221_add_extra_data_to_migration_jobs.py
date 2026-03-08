"""add extra_data to migration_jobs

Revision ID: 9a2b3c4d5e6f
Revises: 8f3095c9911b
Create Date: 2026-03-08 12:21:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '9a2b3c4d5e6f'
down_revision = '8f3095c9911b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('migration_jobs', sa.Column('extra_data', postgresql.JSON(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    op.drop_column('migration_jobs', 'extra_data')
