"""add_full_name_normalized_to_users

Revision ID: 4254e8446d9d
Revises: 9a2b3c4d5e6f
Create Date: 2026-03-08 12:38:28.892315+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4254e8446d9d'
down_revision: Union[str, None] = '9a2b3c4d5e6f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('full_name_normalized', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('email_normalized', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('phone_normalized', sa.String(length=50), nullable=True))
    op.create_index(op.f('ix_users_full_name_normalized'), 'users', ['full_name_normalized'], unique=False)
    op.create_index(op.f('ix_users_email_normalized'), 'users', ['email_normalized'], unique=False)
    op.create_index(op.f('ix_users_phone_normalized'), 'users', ['phone_normalized'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_users_phone_normalized'), table_name='users')
    op.drop_index(op.f('ix_users_email_normalized'), table_name='users')
    op.drop_index(op.f('ix_users_full_name_normalized'), table_name='users')
    op.drop_column('users', 'phone_normalized')
    op.drop_column('users', 'email_normalized')
    op.drop_column('users', 'full_name_normalized')
