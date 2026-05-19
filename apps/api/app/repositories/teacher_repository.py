"""Repository enseignant — accès DB isolé du métier (architecture.md).

Toutes les méthodes sont ``async`` (SQLAlchemy 2.x). Aucune logique métier
n'est implémentée ici : c'est le contrat d'accès données pour les services
``auth_service`` (Story 1.3), ``profile_service`` (Story 1.5), etc.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.teacher import Teacher


class TeacherRepository:
    """Accès CRUD au modèle ``Teacher``."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, teacher_id: uuid.UUID) -> Teacher | None:
        return await self._session.get(Teacher, teacher_id)

    async def get_by_email(self, email: str) -> Teacher | None:
        stmt = select(Teacher).where(Teacher.email == email)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_verification_token(self, token: str) -> Teacher | None:
        stmt = select(Teacher).where(Teacher.email_verification_token == token)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        email: str,
        password_hash: str,
        verification_token: str,
        verification_token_expires_at: datetime,
        display_name: str = "",
    ) -> Teacher:
        teacher = Teacher(
            email=email,
            password_hash=password_hash,
            display_name=display_name,
            status="pending",
            email_verification_token=verification_token,
            email_verification_token_expires_at=verification_token_expires_at,
        )
        self._session.add(teacher)
        await self._session.flush()
        await self._session.refresh(teacher)
        return teacher

    async def activate(self, teacher: Teacher) -> Teacher:
        """Passe le compte en ``active`` et purge le token."""
        teacher.status = "active"
        teacher.email_verification_token = None
        teacher.email_verification_token_expires_at = None
        await self._session.flush()
        await self._session.refresh(teacher)
        return teacher
