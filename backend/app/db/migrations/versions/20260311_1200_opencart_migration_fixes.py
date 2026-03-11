"""opencart_migration_fixes

Revision ID: c2d3e4f5g6h7
Revises: b1c2d3e4f5g6
Create Date: 2026-03-11 12:00:00.000000+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c2d3e4f5g6h7'
down_revision: Union[str, None] = 'b1c2d3e4f5g6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Update migration_jobs
    op.add_column('migration_jobs', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.add_column('migration_jobs', sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True))
    
    # 2. Add new values to MigrationEntity enum
    # PostgreSQL specific: ALTER TYPE ... ADD VALUE ...
    # We use a try/except or execute because if it's already there it might fail
    op.execute("ALTER TYPE migrationentity ADD VALUE IF NOT EXISTS 'devices'")
    op.execute("ALTER TYPE migrationentity ADD VALUE IF NOT EXISTS 'addresses'")

    # 3. Update user_devices
    op.add_column('user_devices', sa.Column('module_device_id', sa.Uuid(), nullable=True))
    op.create_foreign_key('fk_user_devices_module_device_id', 'user_devices', 'module_devices', ['module_device_id'], ['id'], ondelete='SET NULL')
    op.create_unique_constraint('uq_user_devices_oc_device_id', 'user_devices', ['oc_device_id'])

    # 4. Create migration_logs table
    op.create_table(
        'migration_logs',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('job_id', sa.Uuid(), nullable=False),
        sa.Column('level', sa.String(length=10), server_default='INFO', nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('oc_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['job_id'], ['migration_jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_migration_logs_job_id'), 'migration_logs', ['job_id'], unique=False)


def downgrade() -> None:
    # 4. Drop migration_logs
    op.drop_index(op.f('ix_migration_logs_job_id'), table_name='migration_logs')
    op.drop_table('migration_logs')

    # 3. Revert user_devices
    op.drop_constraint('uq_user_devices_oc_device_id', 'user_devices', type_='unique')
    op.drop_constraint('fk_user_devices_module_device_id', 'user_devices', type_='foreignkey')
    op.drop_column('user_devices', 'module_device_id')

    # 2. Enum values cannot be easily removed in PostgreSQL downgrade without dropping the type.
    # Usually we leave them or recreate the type if necessary.
    
    # 1. Revert migration_jobs
    op.drop_column('migration_jobs', 'completed_at')
    op.drop_column('migration_jobs', 'created_at')
