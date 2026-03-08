"""add_oc_address_id_and_extend_enums

Revision ID: 96f1ab236541
Revises: 4254e8446d9d
Create Date: 2026-03-08 12:43:27.664267+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '96f1ab236541'
down_revision: Union[str, None] = '4254e8446d9d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new enum values
    op.execute("ALTER TYPE address_type_enum ADD VALUE IF NOT EXISTS 'courier'")
    op.execute("ALTER TYPE delivery_provider_enum ADD VALUE IF NOT EXISTS 'manual'")

    # Add oc_address_id column
    op.add_column('delivery_addresses', sa.Column('oc_address_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_delivery_addresses_oc_address_id'), 'delivery_addresses', ['oc_address_id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_delivery_addresses_oc_address_id'), table_name='delivery_addresses')
    op.drop_column('delivery_addresses', 'oc_address_id')
    # Note: PostgreSQL does not support removing enum values
