"""user_devices: add comment and oc_device_id columns

Revision ID: a9b8c7d6e5f4
Revises: f6f189d8f825
Create Date: 2026-03-09 10:00:00.000000+00:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a9b8c7d6e5f4"
down_revision: Union[str, None] = "f6f189d8f825"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("user_devices", sa.Column("comment", sa.Text(), nullable=True))
    op.add_column(
        "user_devices",
        sa.Column("oc_device_id", sa.Integer(), nullable=True),
    )
    op.create_index(
        op.f("ix_user_devices_oc_device_id"),
        "user_devices",
        ["oc_device_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_user_devices_oc_device_id"), table_name="user_devices")
    op.drop_column("user_devices", "oc_device_id")
    op.drop_column("user_devices", "comment")
