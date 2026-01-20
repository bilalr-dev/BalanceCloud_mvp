"""Add cloud_accounts, encryption_keys, and storage_chunks tables

Revision ID: add_cloud_encryption_chunks
Revises: 73bcd62a83b2
Create Date: 2025-01-20 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "add_cloud_encryption_chunks"
down_revision = "73bcd62a83b2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create cloud_accounts table
    op.create_table(
        "cloud_accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("provider_account_id", sa.String(length=255), nullable=True),
        sa.Column("access_token_encrypted", sa.String(), nullable=False),
        sa.Column("refresh_token_encrypted", sa.String(), nullable=True),
        sa.Column("token_expires_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", "provider", name="uq_user_provider"),
    )
    op.create_index(op.f("ix_cloud_accounts_user_id"), "cloud_accounts", ["user_id"], unique=False)

    # Create encryption_keys table
    op.create_table(
        "encryption_keys",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("key_encrypted", sa.String(), nullable=False),
        sa.Column("salt", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", name="uq_encryption_keys_user_id"),
    )
    op.create_index(
        op.f("ix_encryption_keys_user_id"), "encryption_keys", ["user_id"], unique=False
    )

    # Create storage_chunks table
    op.create_table(
        "storage_chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("file_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("chunk_size", sa.Integer(), nullable=False),
        sa.Column("encrypted_size", sa.Integer(), nullable=False),
        sa.Column("iv", sa.LargeBinary(), nullable=False),
        sa.Column("encryption_key_encrypted", sa.String(), nullable=False),
        sa.Column("checksum", sa.String(length=64), nullable=False),
        sa.Column("storage_path", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["file_id"], ["files.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("file_id", "chunk_index", name="uq_file_chunk_index"),
    )
    op.create_index(op.f("ix_storage_chunks_file_id"), "storage_chunks", ["file_id"], unique=False)
    op.create_index(
        op.f("ix_storage_chunks_file_id_chunk_index"),
        "storage_chunks",
        ["file_id", "chunk_index"],
        unique=False,
    )

    # Update files table: make storage_path nullable for chunked storage
    op.alter_column("files", "storage_path", existing_type=sa.String(), nullable=True)


def downgrade() -> None:
    # Revert files table change
    op.alter_column("files", "storage_path", existing_type=sa.String(), nullable=False)

    # Drop storage_chunks table
    op.drop_index(op.f("ix_storage_chunks_file_id_chunk_index"), table_name="storage_chunks")
    op.drop_index(op.f("ix_storage_chunks_file_id"), table_name="storage_chunks")
    op.drop_table("storage_chunks")

    # Drop encryption_keys table
    op.drop_index(op.f("ix_encryption_keys_user_id"), table_name="encryption_keys")
    op.drop_table("encryption_keys")

    # Drop cloud_accounts table
    op.drop_index(op.f("ix_cloud_accounts_user_id"), table_name="cloud_accounts")
    op.drop_table("cloud_accounts")
