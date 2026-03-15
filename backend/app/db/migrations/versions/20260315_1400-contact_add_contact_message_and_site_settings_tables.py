"""contact: add contact_message and site_settings tables

Revision ID: 20260315_1400
Revises: 85f3807151f3
Create Date: 2026-03-15 14:00:00.000000+00:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260315_1400"
down_revision: Union[str, None] = "85f3807151f3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create contactstatus ENUM type
    contactstatus = sa.Enum("NEW", "READ", "REPLIED", name="contactstatus")
    contactstatus.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "contact_message",
        sa.Column("id", sa.UUID(), nullable=False, default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("phone", sa.Text(), nullable=True),
        sa.Column("subject", sa.String(length=500), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("NEW", "READ", "REPLIED", name="contactstatus"),
            nullable=False,
            server_default="NEW",
        ),
        sa.Column("ip_address", sa.String(length=45), nullable=False, server_default=""),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "site_settings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("key", sa.String(length=255), nullable=False),
        sa.Column("value", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key", name="uq_site_settings_key"),
    )
    op.create_index("ix_site_settings_key", "site_settings", ["key"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_site_settings_key", table_name="site_settings")
    op.drop_table("site_settings")
    op.drop_table("contact_message")

    # Drop the ENUM type
    contactstatus = sa.Enum("NEW", "READ", "REPLIED", name="contactstatus")
    contactstatus.drop(op.get_bind(), checkfirst=True)
