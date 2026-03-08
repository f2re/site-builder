"""products: add option groups and values

Revision ID: d1e2f3a4b5c6
Revises: 6c70172e87c6
Create Date: 2026-03-08 16:00:00.000000+00:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "d1e2f3a4b5c6"
down_revision: Union[str, None] = "6c70172e87c6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "product_option_groups",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("product_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("is_required", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.ForeignKeyConstraint(
            ["product_id"], ["products.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_product_option_groups_product_id",
        "product_option_groups",
        ["product_id"],
        unique=False,
    )

    op.create_table(
        "product_option_values",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("group_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column(
            "price_modifier",
            sa.Numeric(10, 2),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("sku_suffix", sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(
            ["group_id"], ["product_option_groups.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_product_option_values_group_id",
        "product_option_values",
        ["group_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_product_option_values_group_id", table_name="product_option_values")
    op.drop_table("product_option_values")
    op.drop_index("ix_product_option_groups_product_id", table_name="product_option_groups")
    op.drop_table("product_option_groups")
