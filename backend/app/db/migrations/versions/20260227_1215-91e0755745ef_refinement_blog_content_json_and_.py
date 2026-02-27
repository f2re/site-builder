"""refinement: blog content_json and content_html

Revision ID: 91e0755745ef
Revises: 7e74df555ddc
Create Date: 2026-02-27 12:15:48.037169+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '91e0755745ef'
down_revision: Union[str, None] = '7e74df555ddc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Rename 'content' to 'content_json'
    op.alter_column('blog_posts', 'content', new_column_name='content_json')
    
    # 2. Change type of 'content_json' to JSONB
    # Using 'USING content_json::jsonb' to cast string to JSONB (if valid)
    op.execute("ALTER TABLE blog_posts ALTER COLUMN content_json TYPE jsonb USING content_json::jsonb")
    # Also set server default for JSONB
    op.alter_column('blog_posts', 'content_json', server_default='{}')

    # 3. Add 'content_html' (Text)
    op.add_column('blog_posts', sa.Column('content_html', sa.Text(), nullable=False, server_default=''))


def downgrade() -> None:
    # 1. Remove 'content_html'
    op.drop_column('blog_posts', 'content_html')
    
    # 2. Rename 'content_json' back to 'content'
    op.alter_column('blog_posts', 'content_json', new_column_name='content')
    
    # 3. Change type of 'content' back to Text
    op.execute("ALTER TABLE blog_posts ALTER COLUMN content TYPE text USING content::text")
