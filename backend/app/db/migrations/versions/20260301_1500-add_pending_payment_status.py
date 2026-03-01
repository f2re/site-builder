"""add pending_payment to orderstatus

Revision ID: 20260301_1500
Revises: 20260301_1400
Create Date: 2026-03-01 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260301_1500'
down_revision = '20260301_1400'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add pending_payment to orderstatus enum
    # PostgreSQL doesn't support adding enum values inside a transaction before v12,
    # but since we are likely on a newer version, we can use op.execute.
    # However, to be safe and follow best practices for Alembic + Postgres:
    op.execute("ALTER TYPE orderstatus ADD VALUE IF NOT EXISTS 'pending_payment'")


def downgrade() -> None:
    # Removing a value from an ENUM is not supported in PostgreSQL.
    # We would need to drop and recreate the type, which is dangerous.
    # So we leave it as is (no-op).
    pass
