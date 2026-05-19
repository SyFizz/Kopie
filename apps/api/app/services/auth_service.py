"""Service d'authentification — Story 1.3 (inscription + validation email).

La logique métier vit ICI, pas dans les endpoints (architecture.md).
Le service est instancié à la demande avec une ``AsyncSession`` ; il
collabore avec ``TeacherRepository`` pour tout accès DB.
"""
from __future__ import annotations

import secrets
from datetime import UTC, datetime, timedelta

import structlog
from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.teacher import Teacher
from app.repositories.teacher_repository import TeacherRepository
from app.services.email_service import send_verification_email

logger = structlog.get_logger(__name__)

VERIFICATION_TOKEN_TTL = timedelta(hours=24)


class AuthService:
    """Inscription d'un enseignant + vérification de son adresse email."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = TeacherRepository(session)

    @staticmethod
    def _generate_verification_token() -> str:
        return secrets.token_urlsafe(32)

    async def register_teacher(
        self,
        *,
        email: str,
        password: str,
        background_tasks: BackgroundTasks,
    ) -> Teacher:
        """Crée un compte enseignant en statut ``pending``.

        Lève ``HTTPException(409)`` si l'email est déjà utilisé.
        L'email de vérification est envoyé via ``BackgroundTasks`` (asynchrone).
        """
        normalized_email = email.lower().strip()
        existing = await self._repo.get_by_email(normalized_email)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": {
                        "code": "EMAIL_ALREADY_REGISTERED",
                        "message": "Cet email est déjà utilisé.",
                    }
                },
            )

        password_hash = hash_password(password)
        token = self._generate_verification_token()
        expires_at = datetime.now(UTC) + VERIFICATION_TOKEN_TTL

        teacher = await self._repo.create(
            email=normalized_email,
            password_hash=password_hash,
            verification_token=token,
            verification_token_expires_at=expires_at,
        )
        await self._session.commit()

        background_tasks.add_task(send_verification_email, normalized_email, token)

        logger.info(
            "auth.teacher_registered",
            teacher_id=str(teacher.id),
            email=normalized_email,
        )
        return teacher

    async def verify_email(self, token: str) -> Teacher:
        """Active le compte associé au ``token`` si valide et non expiré.

        Lève ``HTTPException(400, INVALID_OR_EXPIRED_TOKEN)`` sinon.
        """
        teacher = await self._repo.get_by_verification_token(token)
        invalid = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "INVALID_OR_EXPIRED_TOKEN",
                    "message": "Ce lien est invalide ou expiré.",
                }
            },
        )

        if teacher is None:
            raise invalid

        expires_at = teacher.email_verification_token_expires_at
        if expires_at is None:
            raise invalid
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        if expires_at < datetime.now(UTC):
            raise invalid

        teacher = await self._repo.activate(teacher)
        await self._session.commit()

        logger.info(
            "auth.email_verified",
            teacher_id=str(teacher.id),
        )
        return teacher
