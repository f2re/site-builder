"""add_oc_information_id_to_blog_posts

Revision ID: 8f3095c9911b
Revises: 51b7b7931577
Create Date: 2026-03-08 11:21:06.554290+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8f3095c9911b'
down_revision: Union[str, None] = '51b7b7931577'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('blog_posts', sa.Column('oc_information_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_blog_posts_oc_information_id'), 'blog_posts', ['oc_information_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_blog_posts_oc_information_id'), table_name='blog_posts')
    op.drop_column('blog_posts', 'oc_information_id')
