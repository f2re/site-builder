"""cart and order: add selected_options

Revision ID: e2f3a4b5c6d7
Revises: d1e2f3a4b5c6
Create Date: 2026-03-08 16:01:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e2f3a4b5c6d7'
down_revision: Union[str, None] = 'd1e2f3a4b5c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add to cart_items
    op.add_column('cart_items', sa.Column(
        'selected_options', 
        sa.JSON().with_variant(postgresql.JSONB(), 'postgresql'), 
        server_default='[]', 
        nullable=False
    ))
    # Add to order_items
    op.add_column('order_items', sa.Column(
        'selected_options', 
        sa.JSON().with_variant(postgresql.JSONB(), 'postgresql'), 
        server_default='[]', 
        nullable=False
    ))


def downgrade() -> None:
    op.drop_column('order_items', 'selected_options')
    op.drop_column('cart_items', 'selected_options')
