"""Add theme_preference column to users table

Revision ID: 001_add_theme_preference
Revises: 
Create Date: 2026-02-23 22:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_add_theme_preference'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add theme_preference column to users table."""
    # Check if column already exists (for idempotency)
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('users')]
    
    if 'theme_preference' not in columns:
        # Add the theme_preference column with default value 'system'
        # SQLite-compatible: keep server_default since SQLite doesn't support ALTER COLUMN DROP DEFAULT
        op.add_column(
            'users',
            sa.Column(
                'theme_preference',
                sa.String(length=20),
                nullable=False,
                server_default='system'
            )
        )


def downgrade() -> None:
    """Remove theme_preference column from users table."""
    # Check if column exists before dropping (for idempotency)
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('users')]
    
    if 'theme_preference' in columns:
        op.drop_column('users', 'theme_preference')
