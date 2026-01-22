"""Add storage quota to users

Revision ID: add_storage_quota
Revises: add_performance_indexes
Create Date: 2026-01-22 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import os

# revision identifiers, used by Alembic.
revision = 'add_storage_quota'
down_revision = 'perf_indexes'
branch_labels = None
depends_on = None

# Get storage quota from environment variable (required)
DEFAULT_STORAGE_QUOTA_BYTES = int(os.getenv('DEFAULT_STORAGE_QUOTA_BYTES', 0))
if DEFAULT_STORAGE_QUOTA_BYTES <= 0:
    raise ValueError(
        "DEFAULT_STORAGE_QUOTA_BYTES environment variable is required for migration. "
        "Set it in .env file. Example: DEFAULT_STORAGE_QUOTA_BYTES=10737418240 (for 10 GB)"
    )


def upgrade() -> None:
    # Add storage_quota_bytes column to users table
    op.add_column(
        'users',
        sa.Column(
            'storage_quota_bytes',
            sa.BigInteger(),
            nullable=False,
            server_default=str(DEFAULT_STORAGE_QUOTA_BYTES)
        )
    )


def downgrade() -> None:
    # Remove storage_quota_bytes column
    op.drop_column('users', 'storage_quota_bytes')
