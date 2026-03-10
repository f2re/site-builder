"""fix_awaiting_payment_status_data_migration

Revision ID: 381fe83fb1e0
Revises: a9b8c7d6e5f4
Create Date: 2026-03-10 17:09:21.200037+00:00

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '381fe83fb1e0'
down_revision: Union[str, None] = 'a9b8c7d6e5f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Data migration: replace legacy 'awaiting_payment' with 'pending_payment'
    # This fixes LookupError when SQLAlchemy tries to map DB values to Python enum

    # Step 1: Temporarily convert enum to VARCHAR to allow comparison with invalid enum value
    op.execute("ALTER TABLE orders ALTER COLUMN status TYPE VARCHAR USING status::TEXT")

    # Step 2: Update data
    op.execute(
        """
        UPDATE orders
        SET status = 'pending_payment'
        WHERE status = 'awaiting_payment'
        """
    )

    # Step 3: Restore enum type
    op.execute("ALTER TABLE orders ALTER COLUMN status TYPE orderstatus USING status::orderstatus")


def downgrade() -> None:
    # Reverse migration: restore 'awaiting_payment' if needed
    # Note: This is only for rollback scenarios; 'awaiting_payment' is not in Python enum

    # Step 1: Temporarily convert enum to VARCHAR
    op.execute("ALTER TABLE orders ALTER COLUMN status TYPE VARCHAR USING status::TEXT")

    # Step 2: Restore old value
    op.execute(
        """
        UPDATE orders
        SET status = 'awaiting_payment'
        WHERE status = 'pending_payment'
        """
    )

    # Step 3: Restore enum type (will fail if 'awaiting_payment' is not in enum, but that's expected)
    op.execute("ALTER TABLE orders ALTER COLUMN status TYPE orderstatus USING status::orderstatus")
