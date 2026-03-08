"""add type to product_option_groups

Revision ID: f3a4b5c6d7e8
Revises: de2e19023b3b
Create Date: 2026-03-08 16:02:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f3a4b5c6d7e8'
down_revision: Union[str, None] = 'de2e19023b3b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('product_option_groups', sa.Column('type', sa.String(length=50), server_default='radio', nullable=False))


def downgrade() -> None:
    op.drop_column('product_option_groups', 'type')
