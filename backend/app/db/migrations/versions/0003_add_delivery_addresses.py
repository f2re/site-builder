"""add delivery_addresses table

Revision ID: 0003
Revises: 0002
Create Date: 2026-03-08
"""
from typing import Sequence, Union
import uuid
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003"
down_revision: Union[str, None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create ENUMs
    res = op.get_bind().execute(sa.text("SELECT 1 FROM pg_type WHERE typname = 'address_type_enum'"))
    if not res.first():
        sa.Enum("home", "pickup", name="address_type_enum").create(op.get_bind())

    res = op.get_bind().execute(sa.text("SELECT 1 FROM pg_type WHERE typname = 'delivery_provider_enum'"))
    if not res.first():
        sa.Enum("cdek", "pochta", "ozon", "wb", name="delivery_provider_enum").create(op.get_bind())

    # Create table
    op.create_table(
        "delivery_addresses",
        sa.Column("id", sa.UUID(), primary_key=True, default=uuid.uuid4),
        sa.Column("user_id", sa.UUID(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("recipient_name", sa.Text(), nullable=False),
        sa.Column("recipient_phone", sa.Text(), nullable=False),
        sa.Column("recipient_phone_hash", sa.String(64), nullable=False, index=True),
        sa.Column("full_address", sa.Text(), nullable=False),
        sa.Column("address_type", postgresql.ENUM("home", "pickup", name="address_type_enum", create_type=False), nullable=False),
        sa.Column("city", sa.String(100), nullable=False),
        sa.Column("postal_code", sa.String(20), nullable=True),
        sa.Column("provider", postgresql.ENUM("cdek", "pochta", "ozon", "wb", name="delivery_provider_enum", create_type=False), nullable=False),
        sa.Column("pickup_point_code", sa.String(100), nullable=True),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default="false", index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("delivery_addresses")
    op.execute("DROP TYPE IF EXISTS address_type_enum")
    op.execute("DROP TYPE IF EXISTS delivery_provider_enum")
