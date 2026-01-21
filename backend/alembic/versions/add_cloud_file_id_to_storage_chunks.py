"""Add cloud_file_id and cloud_provider to storage_chunks

Revision ID: add_cloud_file_id_to_storage_chunks
Revises: add_cloud_encryption_chunks
Create Date: 2026-01-21 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "add_cloud_file_id_to_storage_chunks"
down_revision = "add_cloud_encryption_chunks"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add cloud_file_id and cloud_provider columns to storage_chunks
    op.add_column("storage_chunks", sa.Column("cloud_file_id", sa.String(), nullable=True))
    op.add_column("storage_chunks", sa.Column("cloud_provider", sa.String(length=50), nullable=True))


def downgrade() -> None:
    # Remove cloud_file_id and cloud_provider columns
    op.drop_column("storage_chunks", "cloud_provider")
    op.drop_column("storage_chunks", "cloud_file_id")
