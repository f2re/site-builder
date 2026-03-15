"""blog: add doc_iframe_url to blog_posts

Revision ID: 20260315_1500
Revises: 20260315_1400
Create Date: 2026-03-15 15:00:00.000000+00:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260315_1500"
down_revision: Union[str, None] = "20260315_1400"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "blog_posts",
        sa.Column("doc_iframe_url", sa.String(length=2000), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("blog_posts", "doc_iframe_url")
