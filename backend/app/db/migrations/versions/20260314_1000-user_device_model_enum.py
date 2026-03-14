"""convert_device_model_to_enum

Revision ID: 20260314_1000
Revises: 20260313_1200
Create Date: 2026-03-14 10:00:00.000000+00:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20260314_1000'
down_revision = '20260313_1200'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Create the enum type if it doesn't exist
    op.execute("DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'devicemodel') THEN CREATE TYPE devicemodel AS ENUM ('wifi_obd2', 'wifi_obd2_advanced'); END IF; END $$;")
    
    # 2. Add the column with a temporary name
    op.add_column('user_devices', sa.Column('model_new', sa.Enum('wifi_obd2', 'wifi_obd2_advanced', name='devicemodel'), nullable=True))
    
    # 3. Perform conversion
    # Everything containing "Advanced" -> wifi_obd2_advanced, rest -> wifi_obd2
    op.execute("""
        UPDATE user_devices 
        SET model_new = CASE 
            WHEN model ILIKE '%Advanced%' THEN 'wifi_obd2_advanced'::devicemodel
            ELSE 'wifi_obd2'::devicemodel
        END
    """)
    
    # 4. Remove old column and rename new one
    op.drop_column('user_devices', 'model')
    op.rename_column('user_devices', 'model_new', 'model')  # type: ignore
    
    # 5. Set NOT NULL and DEFAULT
    op.alter_column('user_devices', 'model', nullable=False, server_default='wifi_obd2')

def downgrade() -> None:
    # 1. Add back the string column
    op.add_column('user_devices', sa.Column('model_old', sa.String(length=100), nullable=True))
    
    # 2. Copy data back
    op.execute("UPDATE user_devices SET model_old = model::text")
    
    # 3. Swap columns
    op.drop_column('user_devices', 'model')
    op.rename_column('user_devices', 'model_old', 'model')  # type: ignore
    
    # 4. Drop the enum type
    op.execute("DROP TYPE devicemodel")
