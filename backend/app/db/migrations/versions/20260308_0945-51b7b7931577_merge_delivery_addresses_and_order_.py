"""merge delivery addresses and order tracking

Revision ID: 51b7b7931577
Revises: 0003, c3d4e5f6a7b8
Create Date: 2026-03-08 09:45:16.897326+00:00

"""
from typing import Sequence, Union



# revision identifiers, used by Alembic.
revision: str = '51b7b7931577'
down_revision: Union[str, Sequence[str], None] = ('0003', 'c3d4e5f6a7b8')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
