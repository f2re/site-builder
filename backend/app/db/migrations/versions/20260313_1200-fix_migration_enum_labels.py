"""fix migration enum labels

Revision ID: 20260313_1200
Revises: 653e3317b26e
Create Date: 2026-03-13 12:00:00.000000+00:00

"""
from typing import Sequence, Union
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '20260313_1200'
down_revision: Union[str, None] = '653e3317b26e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Enum renames cannot be done in a transaction block in some Postgres versions
# But we can try it. If it fails, we might need to use a different approach.

def upgrade() -> None:
    # Fix migrationentity
    op.execute("COMMIT") # End the current transaction block to allow enum renames
    
    for old_val in ['USERS', 'CATEGORIES', 'PRODUCTS', 'IMAGES', 'ORDERS', 'BLOG']:
        op.execute(f"""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM pg_enum 
                    JOIN pg_type ON pg_enum.enumtypid = pg_type.oid 
                    WHERE pg_type.typname = 'migrationentity' AND pg_enum.enumlabel = '{old_val}'
                ) THEN
                    ALTER TYPE migrationentity RENAME VALUE '{old_val}' TO '{old_val.lower()}';
                END IF;
            END
            $$;
        """)
    
    # Fix migrationstatus just in case
    for old_val in ['PENDING', 'RUNNING', 'PAUSED', 'DONE', 'FAILED']:
        op.execute(f"""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM pg_enum 
                    JOIN pg_type ON pg_enum.enumtypid = pg_type.oid 
                    WHERE pg_type.typname = 'migrationstatus' AND pg_enum.enumlabel = '{old_val}'
                ) THEN
                    ALTER TYPE migrationstatus RENAME VALUE '{old_val}' TO '{old_val.lower()}';
                END IF;
            END
            $$;
        """)
    
    op.execute("BEGIN") # Restart the transaction block as Alembic expects one to be active

def downgrade() -> None:
    # Optional: revert to uppercase if needed, but the app expects lowercase.
    pass
