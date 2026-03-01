"""opencart migration tables

Revision ID: 20260301_1230
Revises: f07d615f2f2f
Create Date: 2026-03-01 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260301_1230'
down_revision = 'f07d615f2f2f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check and create migrationentity
    res = op.get_bind().execute(sa.text("SELECT 1 FROM pg_type WHERE typname = 'migrationentity'"))
    if not res.first():
        sa.Enum('USERS', 'CATEGORIES', 'PRODUCTS', 'IMAGES', 'ORDERS', 'BLOG', name='migrationentity').create(op.get_bind())

    # Check and create migrationstatus
    res = op.get_bind().execute(sa.text("SELECT 1 FROM pg_type WHERE typname = 'migrationstatus'"))
    if not res.first():
        sa.Enum('PENDING', 'RUNNING', 'PAUSED', 'DONE', 'FAILED', name='migrationstatus').create(op.get_bind())

    # ─── migration_jobs ──────────────────────────────────────────────────────
    op.create_table(
        'migration_jobs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('entity', postgresql.ENUM('USERS', 'CATEGORIES', 'PRODUCTS', 'IMAGES', 'ORDERS', 'BLOG', name='migrationentity', create_type=False), nullable=False),
        sa.Column('status', postgresql.ENUM('PENDING', 'RUNNING', 'PAUSED', 'DONE', 'FAILED', name='migrationstatus', create_type=False), nullable=False),
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
    
    op.execute("DROP TYPE IF EXISTS migrationentity")
    op.execute("DROP TYPE IF EXISTS migrationstatus")
