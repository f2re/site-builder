"""add orders and user_devices tables

Revision ID: 0002
Revises: 0001
Create Date: 2026-02-26
"""
from typing import Sequence, Union
import uuid
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Allowed order statuses
ORDER_STATUSES = ["pending", "paid", "processing", "shipped", "delivered", "cancelled", "refunded"]


def upgrade() -> None:
    # Check if orderstatus type exists
    res = op.get_bind().execute(sa.text("SELECT 1 FROM pg_type WHERE typname = 'orderstatus'"))
    if not res.first():
        sa.Enum(*ORDER_STATUSES, name="orderstatus").create(op.get_bind())

    # ── orders ────────────────────────────────────────────────────────────────
    op.create_table(
        "orders",
        sa.Column("id", sa.UUID(), primary_key=True, default=uuid.uuid4),
        sa.Column(
            "user_id",
            sa.UUID(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
        sa.Column(
            "status",
            postgresql.ENUM(*ORDER_STATUSES, name="orderstatus", create_type=False),
            nullable=False,
            server_default="pending",
            index=True,
        ),
        sa.Column("total_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="RUB"),
        sa.Column("shipping_address", sa.String(500), nullable=True),
        sa.Column("cdek_order_uuid", sa.String(100), nullable=True),
        sa.Column("payment_id", sa.String(100), nullable=True),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # ── user_devices ──────────────────────────────────────────────────────────
    op.create_table(
        "user_devices",
        sa.Column("id", sa.UUID(), primary_key=True, default=uuid.uuid4),
        sa.Column(
            "user_id",
            sa.UUID(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("device_uid", sa.String(100), nullable=False, unique=True, index=True),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("model", sa.String(100), nullable=True),
        sa.Column("firmware_version", sa.String(50), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "registered_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    op.drop_table("user_devices")
    op.drop_table("orders")
    op.execute("DROP TYPE IF EXISTS orderstatus")
