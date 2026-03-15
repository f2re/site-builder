"""devices: add user_device_complectations m2m table

Revision ID: 20260315_0910
Revises: 20260314_1200
Create Date: 2026-03-15 09:10:00.000000+00:00

Creates the M2M association table between user_devices and module_complectations.
"""
import sqlalchemy as sa
from alembic import op

revision = "20260315_0910"
down_revision = "20260314_1200"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_device_complectations",
        sa.Column("user_device_id", sa.Uuid(), nullable=False),
        sa.Column("complectation_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_device_id"],
            ["user_devices.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["complectation_id"],
            ["module_complectations.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("user_device_id", "complectation_id"),
    )


def downgrade() -> None:
    op.drop_table("user_device_complectations")
