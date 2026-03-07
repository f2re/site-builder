"""
Example Alembic migration with TimescaleDB hypertable support.
Revision ID: 20260227_142000_iot_add_telemetry_hypertable
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260227_142000_iot_add_telemetry_hypertable'
down_revision = 'previous_revision_id'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Create the telemetry table
    op.create_table(
        'telemetry',
        sa.Column('device_id', sa.UUID(), nullable=False),
        sa.Column('ts', sa.DateTime(timezone=True), nullable=False),
        sa.Column('data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.PrimaryKeyConstraint('device_id', 'ts')
    )
    
    # 2. Convert to TimescaleDB hypertable
    # Required for the IoT module as per project contract
    op.execute(
        "SELECT create_hypertable('telemetry', 'ts', "
        "chunk_time_interval => INTERVAL '1 day')"
    )
    
    # 3. Add retention policy (e.g., 30 days)
    op.execute(
        "SELECT add_retention_policy('telemetry', "
        "INTERVAL '30 days')"
    )

def downgrade() -> None:
    op.drop_table('telemetry')
