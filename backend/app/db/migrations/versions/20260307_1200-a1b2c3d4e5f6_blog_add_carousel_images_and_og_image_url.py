"""blog: add carousel_images and og_image_url columns

Revision ID: a1b2c3d4e5f6
Revises: 6ad8390c4ab2
Create Date: 2026-03-07 12:00:00.000000+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '6ad8390c4ab2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'blog_posts',
        sa.Column(
            'carousel_images',
            postgresql.JSONB(astext_type=sa.Text()),
            server_default='[]',
            nullable=False,
        ),
    )
    op.add_column(
        'blog_posts',
        sa.Column('og_image_url', sa.String(length=1000), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('blog_posts', 'og_image_url')
    op.drop_column('blog_posts', 'carousel_images')
