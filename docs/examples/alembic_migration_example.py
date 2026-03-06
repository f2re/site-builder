"""
Эталонная Alembic-миграция.
Reference-by-example: используй как шаблон для новых миграций.

Правила:
- ENUM: всегда с IF NOT EXISTS в upgrade(), DROP TYPE в downgrade()
- Одна голова (1 head): не создавай ветки в истории миграций
- Идентификаторы: uuid4 из alembic revision --autogenerate
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'abc123def456'
down_revision = 'previous_revision_id'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- ENUM: создавать только с IF NOT EXISTS ---
    order_status = postgresql.ENUM(
        'pending', 'confirmed', 'shipped', 'delivered', 'cancelled',
        name='orderstatus',
        create_type=False,  # управляем вручную для IF NOT EXISTS
    )
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE orderstatus AS ENUM
                ('pending', 'confirmed', 'shipped', 'delivered', 'cancelled');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    # --- Таблица ---
    op.create_table(
        'orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('total_amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column(
            'status',
            postgresql.ENUM(
                'pending', 'confirmed', 'shipped', 'delivered', 'cancelled',
                name='orderstatus',
                create_type=False,
            ),
            nullable=False,
            server_default='pending',
        ),
        sa.Column(
            'created_at',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('NOW()'),
            nullable=False,
        ),
        sa.Column(
            'updated_at',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('NOW()'),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_orders_user_id', 'orders', ['user_id'])
    op.create_index('ix_orders_status', 'orders', ['status'])
    op.create_index('ix_orders_created_at', 'orders', ['created_at'])


def downgrade() -> None:
    op.drop_index('ix_orders_created_at', table_name='orders')
    op.drop_index('ix_orders_status', table_name='orders')
    op.drop_index('ix_orders_user_id', table_name='orders')
    op.drop_table('orders')

    # DROP TYPE только если таблица была единственным пользователем
    op.execute('DROP TYPE IF EXISTS orderstatus;')
