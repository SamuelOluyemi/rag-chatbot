
"""add users and document chunks

Revision ID: b60d6686f415
Revises: 9fba0034ab5d
Create Date: 2026-11-18 14:10:09.300860

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = "b60d6686f415"
down_revision: Union[str, Sequence[str], None] = "9fba0034ab5d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Ensure the PostgreSQL vector extension exists.
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Create users table.
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    # Add user_id temporarily as nullable.
    op.add_column(
        "documents",
        sa.Column("user_id", sa.Integer(), nullable=True),
    )

    # Create a local development user.
    op.execute(
        sa.text(
            """
            INSERT INTO users (email, created_at)
            VALUES ('local@ragchatbot.local', CURRENT_TIMESTAMP)
            ON CONFLICT (email) DO NOTHING
            """
        )
    )

    # Assign existing documents to the local development user.
    op.execute(
        sa.text(
            """
            UPDATE documents
            SET user_id = (
                SELECT id
                FROM users
                WHERE email = 'local@ragchatbot.local'
            )
            WHERE user_id IS NULL
            """
        )
    )

    # Every document must now have an owner.
    op.alter_column(
        "documents",
        "user_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    # Add a named foreign key for reliable migrations.
    op.create_foreign_key(
        "fk_documents_user_id_users",
        "documents",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.create_index(
        "ix_documents_user_id",
        "documents",
        ["user_id"],
        unique=False,
    )

    # Create document chunks table.
    op.create_table(
        "document_chunks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(384), nullable=False),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["documents.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "document_id",
            "chunk_index",
            name="uq_document_chunk_index",
        ),
    )

    op.create_index(
        "ix_document_chunks_document_id",
        "document_chunks",
        ["document_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        "ix_document_chunks_document_id",
        table_name="document_chunks",
    )

    op.drop_table("document_chunks")

    op.drop_index(
        "ix_documents_user_id",
        table_name="documents",
    )

    op.drop_constraint(
        "fk_documents_user_id_users",
        "documents",
        type_="foreignkey",
    )

    op.drop_column("documents", "user_id")

    op.drop_table("users")
