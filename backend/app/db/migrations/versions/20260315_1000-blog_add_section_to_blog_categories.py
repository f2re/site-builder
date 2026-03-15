"""blog: add section to blog_categories

Revision ID: 20260315_1000
Revises: 20260315_0910
Create Date: 2026-03-15 10:00:00.000000+00:00

Adds nullable VARCHAR(20) column `section` to blog_categories table.
Supports values: 'news', 'instructions' (enforced at application level).
"""
import sqlalchemy as sa
from alembic import op

revision = "20260315_1000"
down_revision = "20260315_0910"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "blog_categories",
        sa.Column("section", sa.String(length=20), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("blog_categories", "section")
