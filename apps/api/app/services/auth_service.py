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
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models.teacher import Teacher
from app.repositories.teacher_repository import TeacherRepository
from app.services.email_service import send_verification_email

logger = structlog.get_logger(__name__)

VERIFICATION_TOKEN_TTL = timedelta(hours=24)

# Hash bcrypt « bidon » utilisé pour conserver un coût constant côté
# ``login_teacher`` même quand le compte demandé n'existe pas. Sans cela,
# un attaquant peut distinguer « email inconnu » (réponse rapide) de
# « mot de passe erroné » (réponse bcrypt lente) et énumérer les comptes.
# Format valide bcrypt ($2b$12$...) — ne correspond à aucun mot de passe réel.
_TIMING_DUMMY_HASH = (
    "$2b$12$abcdefghijklmnopqrstuuJ8ZQ3oUNQHbJoDxRiR0FFXfMFkUmYHi"
)

_EMAIL_ALREADY_REGISTERED = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail={
        "error": {
            "code": "EMAIL_ALREADY_REGISTERED",
            "message": "Cet email est déjà utilisé.",
        }
    },
)

_INVALID_CREDENTIALS = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail={
        "error": {
            "code": "INVALID_CREDENTIALS",
            "message": "Email ou mot de passe incorrect.",
        }
    },
)

_ACCOUNT_NOT_ACTIVE = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail={
        "error": {
            "code": "ACCOUNT_NOT_ACTIVE",
            "message": (
                "Votre compte n'est pas encore activé. "
                "Vérifiez votre boîte mail pour confirmer votre adresse."
            ),
        }
    },
)


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

        Lève ``HTTPException(409)`` si l'email est déjà utilisé. La contrainte
        ``UNIQUE`` côté DB est l'autorité finale : entre le ``get_by_email``
        et le ``commit``, une autre requête peut avoir inséré le même email,
        auquel cas le ``IntegrityError`` est capté et traduit en 409 — la
        réponse vue par le client reste identique au cas séquentiel
        (AC2 : « aucune donnée n'est créée ni modifiée »).

        L'email de vérification est envoyé via ``BackgroundTasks`` (asynchrone).
        """
        normalized_email = email.lower().strip()
        existing = await self._repo.get_by_email(normalized_email)
        if existing is not None:
            raise _EMAIL_ALREADY_REGISTERED

        password_hash = hash_password(password)
        token = self._generate_verification_token()
        expires_at = datetime.now(UTC) + VERIFICATION_TOKEN_TTL

        try:
            teacher = await self._repo.create(
                email=normalized_email,
                password_hash=password_hash,
                verification_token=token,
                verification_token_expires_at=expires_at,
            )
            await self._session.commit()
        except IntegrityError:
            await self._session.rollback()
            logger.info(
                "auth.register_race_condition_email_taken",
                email=normalized_email,
            )
            raise _EMAIL_ALREADY_REGISTERED from None

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

    async def login_teacher(self, *, email: str, password: str) -> Teacher:
        """Authentifie un enseignant.

        Story 1.4. Renvoie le ``Teacher`` si les credentials sont valides et
        le compte ``active``. Lève :

        - ``HTTPException(401, INVALID_CREDENTIALS)`` si l'email est inconnu
          OU si le mot de passe est incorrect — même code/message dans les
          deux cas pour empêcher l'énumération d'utilisateurs.
        - ``HTTPException(403, ACCOUNT_NOT_ACTIVE)`` si le compte existe
          mais reste en statut ``pending`` (email non confirmé) — la
          vérification du statut est faite APRÈS celle du mot de passe pour
          éviter qu'un attaquant déduise l'existence d'un compte ``pending``
          via la différence de code HTTP (401 vs 403).

        Comportement timing-constant : si le compte n'existe pas, on appelle
        ``verify_password`` sur un hash bidon afin de payer le même coût bcrypt
        que dans le chemin nominal. Cela neutralise une attaque par observation
        du temps de réponse (qui distinguerait sinon « email inconnu » d'« email
        connu, mot de passe erroné »).
        """
        normalized_email = email.lower().strip()
        teacher = await self._repo.get_by_email(normalized_email)

        if teacher is None:
            verify_password(password, _TIMING_DUMMY_HASH)
            logger.info(
                "auth.login_unknown_email",
                email=normalized_email,
            )
            raise _INVALID_CREDENTIALS

        if not verify_password(password, teacher.password_hash):
            logger.info(
                "auth.login_wrong_password",
                teacher_id=str(teacher.id),
            )
            raise _INVALID_CREDENTIALS

        if teacher.status != "active":
            logger.info(
                "auth.login_inactive_account",
                teacher_id=str(teacher.id),
                teacher_status=teacher.status,
            )
            raise _ACCOUNT_NOT_ACTIVE

        logger.info(
            "auth.teacher_logged_in",
            teacher_id=str(teacher.id),
        )
        return teacher
