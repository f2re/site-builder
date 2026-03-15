"""blog: seed news and instructions categories

Revision ID: 85f3807151f3
Revises: 20260315_1000
Create Date: 2026-03-15 11:23:35.475754+00:00

"""
import uuid
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "85f3807151f3"
down_revision: Union[str, None] = "20260315_1000"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Pre-generated UUIDs so they are stable across runs
NEWS_ID = str(uuid.uuid4())
INSTRUCTIONS_ID = str(uuid.uuid4())


def upgrade() -> None:
    op.execute(
        f"""
        INSERT INTO blog_categories (id, name, slug, description, section)
        VALUES (
            '{NEWS_ID}'::uuid,
            'Новости',
            'novosti',
            'Новости компании и отрасли OBD2',
            'news'
        )
        ON CONFLICT (slug) DO NOTHING;
        """
    )
    op.execute(
        f"""
        INSERT INTO blog_categories (id, name, slug, description, section)
        VALUES (
            '{INSTRUCTIONS_ID}'::uuid,
            'Инструкции',
            'instrukcii',
            'Инструкции по установке и использованию OBD2 адаптеров',
            'instructions'
        )
        ON CONFLICT (slug) DO NOTHING;
        """
    )


def downgrade() -> None:
    op.execute(
        "DELETE FROM blog_categories WHERE slug IN ('novosti', 'instrukcii')"
    )
