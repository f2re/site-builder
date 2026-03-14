"""fix_device_model_enum_to_varchar

Revision ID: 20260314_1200
Revises: 20260314_1100
Create Date: 2026-03-14 12:00:00.000000+00:00

Convert user_devices.model from native PostgreSQL enum (devicemodel)
to VARCHAR so SQLAlchemy native_enum=False can map values correctly.
"""
from alembic import op

revision = '20260314_1200'
down_revision = '20260314_1100'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Convert from native pg enum to varchar, preserving values
    op.execute("""
        ALTER TABLE user_devices
        ALTER COLUMN model TYPE VARCHAR(50)
        USING model::text
    """)
    # Drop the now-unused pg enum type
    op.execute("DROP TYPE IF EXISTS devicemodel")


def downgrade() -> None:
    # Recreate the pg enum type and convert back
    op.execute("CREATE TYPE devicemodel AS ENUM ('wifi_obd2', 'wifi_obd2_advanced')")
    op.execute("""
        ALTER TABLE user_devices
        ALTER COLUMN model TYPE devicemodel
        USING model::devicemodel
    """)
