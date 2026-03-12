"""fix_migration_enum_case

Revision ID: 653e3317b26e
Revises: c2d3e4f5g6h7
Create Date: 2026-03-12 18:01:01.766632+00:00

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '653e3317b26e'
down_revision: Union[str, None] = 'c2d3e4f5g6h7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("UPDATE migration_jobs SET entity = LOWER(entity::text)::migrationentity WHERE entity IS NOT NULL")
    op.execute("UPDATE migration_jobs SET status = LOWER(status::text)::migrationstatus WHERE status IS NOT NULL")


def downgrade() -> None:
    op.execute("UPDATE migration_jobs SET entity = UPPER(entity::text)::migrationentity WHERE entity IS NOT NULL")
    op.execute("UPDATE migration_jobs SET status = UPPER(status::text)::migrationstatus WHERE status IS NOT NULL")
