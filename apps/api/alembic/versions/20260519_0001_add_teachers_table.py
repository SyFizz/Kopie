"""add teachers table

Revision ID: 20260519_0001
Revises:
Create Date: 2026-05-19

Story 1.3 — Inscription enseignant avec validation email.

Crée la table ``teachers`` avec :
- ``id`` UUID PK (générique SQLAlchemy ``Uuid`` : UUID natif sur PostgreSQL,
  CHAR(32) sur SQLite).
- ``email`` unique + index (lookups d'inscription / login fréquents).
- ``password_hash`` (bcrypt via passlib, Story 1.3).
- ``status`` String("pending" | "active") — pas un enum DB pour faciliter les
  futures migrations.
- ``email_verification_token`` indexé (lookup par token au GET /verify-email).
- timestamps ``created_at`` / ``updated_at`` server-side (``func.now()``).
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260519_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "teachers",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column(
            "display_name",
            sa.String(length=100),
            nullable=False,
            server_default="",
        ),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "email_verification_token", sa.String(length=64), nullable=True
        ),
        sa.Column(
            "email_verification_token_expires_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("email", name="uq_teachers_email"),
    )
    op.create_index("ix_teachers_email", "teachers", ["email"], unique=False)
    op.create_index(
        "ix_teachers_email_verification_token",
        "teachers",
        ["email_verification_token"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_teachers_email_verification_token", table_name="teachers")
    op.drop_index("ix_teachers_email", table_name="teachers")
    op.drop_table("teachers")
