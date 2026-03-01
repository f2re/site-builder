"""opencart migration tables

Revision ID: 20260301_1230
Revises: 20260301_1105
Create Date: 2026-03-01 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260301_1230'
down_revision = '20260301_1105'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ─── migration_jobs ──────────────────────────────────────────────────────
    op.create_table(
        'migration_jobs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('entity', sa.Enum('USERS', 'CATEGORIES', 'PRODUCTS', 'IMAGES', 'ORDERS', 'BLOG', name='migrationentity'), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'RUNNING', 'PAUSED', 'DONE', 'FAILED', name='migrationstatus'), nullable=False),
        sa.Column('total', sa.Integer(), nullable=False),
        sa.Column('processed', sa.Integer(), nullable=False),
        sa.Column('skipped', sa.Integer(), nullable=False),
        sa.Column('failed', sa.Integer(), nullable=False),
        sa.Column('last_oc_id', sa.Integer(), nullable=True),
        sa.Column('errors', sa.JSON(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # ─── oc_*_id fields ──────────────────────────────────────────────────────
    op.add_column('categories', sa.Column('oc_category_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_categories_oc_category_id'), 'categories', ['oc_category_id'], unique=False)
    
    op.add_column('products', sa.Column('oc_product_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_products_oc_product_id'), 'products', ['oc_product_id'], unique=False)
    
    op.add_column('orders', sa.Column('oc_order_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_orders_oc_order_id'), 'orders', ['oc_order_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_orders_oc_order_id'), table_name='orders')
    op.drop_column('orders', 'oc_order_id')
    
    op.drop_index(op.f('ix_products_oc_product_id'), table_name='products')
    op.drop_column('products', 'oc_product_id')
    
    op.drop_index(op.f('ix_categories_oc_category_id'), table_name='categories')
    op.drop_column('categories', 'oc_category_id')
    
    op.drop_table('migration_jobs')
    # Note: Enums are not dropped here to avoid issues if they are shared, 
    # but in a clean downgrade you might want sa.Enum(...).drop(op.get_bind())
