"""order: add tracking fields and events table

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-03-08 12:07:00.000000+00:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add tracking fields to orders table
    op.add_column('orders', sa.Column('tracking_number', sa.String(100), nullable=True))
    op.add_column('orders', sa.Column('tracking_url', sa.String(500), nullable=True))
    op.add_column('orders', sa.Column('delivery_status', sa.String(50), nullable=True))
    op.add_column('orders', sa.Column('delivery_provider', sa.String(50), nullable=True))
    op.create_index(op.f('ix_orders_tracking_number'), 'orders', ['tracking_number'], unique=False)

    # Create order_tracking_events table
    op.create_table(
        'order_tracking_events',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('order_id', sa.UUID(), nullable=False),
        sa.Column('provider', sa.String(50), nullable=False),
        sa.Column('status', sa.String(100), nullable=False),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_order_tracking_events_order_id'), 'order_tracking_events', ['order_id'], unique=False)
    op.create_index(op.f('ix_order_tracking_events_timestamp'), 'order_tracking_events', ['timestamp'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_order_tracking_events_timestamp'), table_name='order_tracking_events')
    op.drop_index(op.f('ix_order_tracking_events_order_id'), table_name='order_tracking_events')
    op.drop_table('order_tracking_events')
    op.drop_index(op.f('ix_orders_tracking_number'), table_name='orders')
    op.drop_column('orders', 'delivery_provider')
    op.drop_column('orders', 'delivery_status')
    op.drop_column('orders', 'tracking_url')
    op.drop_column('orders', 'tracking_number')
