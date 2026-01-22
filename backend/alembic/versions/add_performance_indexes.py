"""Add performance indexes

Revision ID: perf_indexes
Revises: add_cloud_file_id
Create Date: 2024-01-21 17:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "perf_indexes"
down_revision = "add_cloud_file_id"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Users table indexes
    op.create_index(
        "users_email_idx", "users", ["email"], unique=False, if_not_exists=True
    )

    # Files table indexes
    op.create_index(
        "files_user_id_idx", "files", ["user_id"], unique=False, if_not_exists=True
    )
    op.create_index(
        "files_user_id_parent_id_idx",
        "files",
        ["user_id", "parent_id"],
        unique=False,
        postgresql_where=sa.text("parent_id IS NOT NULL"),
        if_not_exists=True,
    )
    op.create_index(
        "files_user_id_path_idx",
        "files",
        ["user_id", "path"],
        unique=False,
        if_not_exists=True,
    )

    # Storage chunks table indexes
    op.create_index(
        "storage_chunks_file_id_idx",
        "storage_chunks",
        ["file_id"],
        unique=False,
        if_not_exists=True,
    )
    op.create_index(
        "storage_chunks_file_id_chunk_index_idx",
        "storage_chunks",
        ["file_id", "chunk_index"],
        unique=False,
        if_not_exists=True,
    )

    # Cloud accounts table indexes
    op.create_index(
        "cloud_accounts_user_id_provider_idx",
        "cloud_accounts",
        ["user_id", "provider"],
        unique=False,
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_index("cloud_accounts_user_id_provider_idx", table_name="cloud_accounts")
    op.drop_index(
        "storage_chunks_file_id_chunk_index_idx", table_name="storage_chunks"
    )
    op.drop_index("storage_chunks_file_id_idx", table_name="storage_chunks")
    op.drop_index("files_user_id_path_idx", table_name="files")
    op.drop_index("files_user_id_parent_id_idx", table_name="files")
    op.drop_index("files_user_id_idx", table_name="files")
    op.drop_index("users_email_idx", table_name="users")
