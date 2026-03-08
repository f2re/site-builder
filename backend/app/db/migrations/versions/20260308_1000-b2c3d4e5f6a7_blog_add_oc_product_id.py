"""blog: add oc_product_id to blog_posts

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-03-08 10:00:00.000000+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'blog_posts',
        sa.Column('oc_product_id', sa.Integer(), nullable=True),
    )
    op.create_index(
        op.f('ix_blog_posts_oc_product_id'),
        'blog_posts',
        ['oc_product_id'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_blog_posts_oc_product_id'), table_name='blog_posts')
    op.drop_column('blog_posts', 'oc_product_id')
