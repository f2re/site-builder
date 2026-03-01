"""dashfirm initial tables

Revision ID: 20260301_1400
Revises: 20260301_1230
Create Date: 2026-03-01 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260301_1400'
down_revision = '20260301_1230'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ─── ModuleToken ──────────────────────────────────────────────────────────
    op.create_table(
        'module_tokens',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('token', sa.String(length=255), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_module_tokens_token'), 'module_tokens', ['token'], unique=True)

    # ─── ModuleDevice ─────────────────────────────────────────────────────────
    # Check if the enum type exists before creating
    bind = op.get_bind()
    has_type = bind.execute(
        sa.text("SELECT 1 FROM pg_type WHERE typname = 'device_type_enum'")
    ).scalar()
    
    if not has_type:
        device_type_enum = postgresql.ENUM('OBD', 'AFR', name='device_type_enum')
        device_type_enum.create(bind)

    op.create_table(
        'module_devices',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('token_id', sa.UUID(), nullable=False),
        sa.Column('serial', sa.String(length=255), nullable=False),
        sa.Column('device_type', postgresql.ENUM('OBD', 'AFR', name='device_type_enum', create_type=False), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['token_id'], ['module_tokens.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('serial')
    )
    op.create_index(op.f('ix_module_devices_serial'), 'module_devices', ['serial'], unique=True)

    # ─── ModuleComplectation ──────────────────────────────────────────────────
    op.create_table(
        'module_complectations',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('caption', sa.String(length=255), nullable=False),
        sa.Column('label', sa.String(length=255), nullable=False),
        sa.Column('code', sa.Integer(), nullable=False),
        sa.Column('simple', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_module_complectations_label'), 'module_complectations', ['label'], unique=False)

    # ─── device_complectations (Association) ──────────────────────────────────
    op.create_table(
        'device_complectations',
        sa.Column('device_serial', sa.String(length=255), nullable=False),
        sa.Column('complectation_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['complectation_id'], ['module_complectations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['device_serial'], ['module_devices.serial'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('device_serial', 'complectation_id')
    )


def downgrade() -> None:
    op.drop_table('device_complectations')
    op.drop_index(op.f('ix_module_complectations_label'), table_name='module_complectations')
    op.drop_table('module_complectations')
    op.drop_index(op.f('ix_module_devices_serial'), table_name='module_devices')
    op.drop_table('module_devices')
    
    # Drop enum safely
    bind = op.get_bind()
    has_type = bind.execute(
        sa.text("SELECT 1 FROM pg_type WHERE typname = 'device_type_enum'")
    ).scalar()
    if has_type:
        device_type_enum = postgresql.ENUM(name='device_type_enum')
        device_type_enum.drop(bind)

    op.drop_index(op.f('ix_module_tokens_token'), table_name='module_tokens')
    op.drop_table('module_tokens')
