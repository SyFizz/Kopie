"""Modèle ORM Teacher — compte enseignant Kopie.

Story 1.3 : Inscription enseignant avec validation email.

Notes de conception :
- ``status`` est une ``String`` (pas un Enum PostgreSQL) — facilite les
  migrations futures sans contrainte de type côté base.
- ``email_verification_token`` est stocké en clair (secret court-terme,
  TTL 24 h) ; il est mis à ``NULL`` dès que le compte est activé.
- ``Uuid`` (SQLAlchemy 2.0) est dialect-agnostic : ``UUID`` natif sur
  PostgreSQL, ``CHAR(32)`` sur SQLite — permet d'exécuter les tests sur
  ``sqlite+aiosqlite`` sans modifier le modèle.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Index, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Teacher(Base):
    """Compte enseignant Kopie."""

    __tablename__ = "teachers"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(
        String(100), nullable=False, default=""
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending"
    )
    email_verification_token: Mapped[str | None] = mapped_column(
        String(64), nullable=True, index=True
    )
    email_verification_token_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (Index("ix_teachers_email", "email"),)

    def __repr__(self) -> str:
        return f"<Teacher id={self.id!s} email={self.email!r} status={self.status!r}>"
