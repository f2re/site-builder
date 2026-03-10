"""add_image_variants_support

Revision ID: b1c2d3e4f5g6
Revises: 381fe83fb1e0
Create Date: 2026-03-11 00:00:00.000000+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b1c2d3e4f5g6'
down_revision: Union[str, None] = '381fe83fb1e0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns to product_images
    op.add_column('product_images', sa.Column('sequence', sa.Integer(), nullable=True))
    op.add_column('product_images', sa.Column('base_path', sa.String(length=500), nullable=True))
    op.add_column('product_images', sa.Column('formats', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False))

    # Add new columns to blog_post_media
    op.add_column('blog_post_media', sa.Column('sequence', sa.Integer(), nullable=True))
    op.add_column('blog_post_media', sa.Column('base_path', sa.String(length=500), nullable=True))
    op.add_column('blog_post_media', sa.Column('formats', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False))

    # Populate default values for existing records in product_images
    op.execute("""
        UPDATE product_images
        SET sequence = sort_order + 1,
            base_path = CASE
                WHEN url LIKE '%.%' THEN SUBSTRING(url FROM 1 FOR LENGTH(url) - POSITION('.' IN REVERSE(url)))
                ELSE url
            END,
            formats = '{}'::jsonb
        WHERE sequence IS NULL
    """)

    # Populate default values for existing records in blog_post_media
    op.execute("""
        UPDATE blog_post_media
        SET sequence = sort_order + 1,
            base_path = CASE
                WHEN url LIKE '%.%' THEN SUBSTRING(url FROM 1 FOR LENGTH(url) - POSITION('.' IN REVERSE(url)))
                ELSE url
            END,
            formats = '{}'::jsonb
        WHERE sequence IS NULL
    """)

    # Make sequence NOT NULL after populating data
    op.alter_column('product_images', 'sequence', nullable=False)
    op.alter_column('blog_post_media', 'sequence', nullable=False)


def downgrade() -> None:
    # Remove columns from blog_post_media
    op.drop_column('blog_post_media', 'formats')
    op.drop_column('blog_post_media', 'base_path')
    op.drop_column('blog_post_media', 'sequence')

    # Remove columns from product_images
    op.drop_column('product_images', 'formats')
    op.drop_column('product_images', 'base_path')
    op.drop_column('product_images', 'sequence')
