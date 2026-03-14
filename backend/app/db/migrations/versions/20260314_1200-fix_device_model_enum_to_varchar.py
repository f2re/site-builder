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
    # 1. Drop the default value first because it depends on the enum type
    op.execute("ALTER TABLE user_devices ALTER COLUMN model DROP DEFAULT")
    
    # 2. Convert from native pg enum to varchar, preserving values
    op.execute("""
        ALTER TABLE user_devices
        ALTER COLUMN model TYPE VARCHAR(50)
        USING model::text
    """)
    
    # 3. Drop the now-unused pg enum type
    op.execute("DROP TYPE IF EXISTS devicemodel")
    
    # 4. Restore the default value (now as a string)
    op.execute("ALTER TABLE user_devices ALTER COLUMN model SET DEFAULT 'wifi_obd2'")


def downgrade() -> None:
    # 1. Recreate the pg enum type
    op.execute("CREATE TYPE devicemodel AS ENUM ('wifi_obd2', 'wifi_obd2_advanced')")
    
    # 2. Drop the string default
    op.execute("ALTER TABLE user_devices ALTER COLUMN model DROP DEFAULT")
    
    # 3. Convert back to enum
    op.execute("""
        ALTER TABLE user_devices
        ALTER COLUMN model TYPE devicemodel
        USING model::devicemodel
    """)
    
    # 4. Restore the enum default
    op.execute("ALTER TABLE user_devices ALTER COLUMN model SET DEFAULT 'wifi_obd2'::devicemodel")
