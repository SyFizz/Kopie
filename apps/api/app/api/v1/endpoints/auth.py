"""Endpoints d'authentification — Stories 1.3 + 1.4.

Routes :

- ``POST /auth/register`` (Story 1.3) — rate-limité ``RATE_LIMIT_AUTH``.
- ``GET /auth/verify-email`` (Story 1.3) — porteur du token, pas d'auth.
- ``POST /auth/login`` (Story 1.4) — rate-limité ``RATE_LIMIT_AUTH``.
- ``POST /auth/refresh`` (Story 1.4) — rate-limité ``RATE_LIMIT_AUTH``.
- ``POST /auth/logout`` (Story 1.4) — pas d'auth requise (idempotent).

Le cookie ``refresh_token`` est posé/renouvelé/supprimé exclusivement par
les endpoints de cette story. Il est ``httpOnly``, ``SameSite=Strict``,
``Secure`` (selon ``settings.COOKIE_SECURE``) et son ``path`` est scopé à
``/api/v1/auth`` pour ne pas être envoyé sur les autres routes.
"""
from __future__ import annotations

import uuid
from typing import Annotated, Any

import structlog
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Cookie,
    Depends,
    HTTPException,
    Query,
    Request,
    Response,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.rate_limit import limiter
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.repositories.teacher_repository import TeacherRepository
from app.schemas.teacher import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    TeacherCreated,
    VerifyEmailResponse,
)
from app.services.auth_service import AuthService

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/auth")

DbSession = Annotated[AsyncSession, Depends(get_db)]

#: Nom du cookie de refresh — partagé avec les tests et le front.
REFRESH_COOKIE_NAME = "refresh_token"
#: ``path`` du cookie — restreint son envoi automatique aux routes d'auth.
REFRESH_COOKIE_PATH = "/api/v1/auth"

# Le paramètre ``token`` est obligatoire — FastAPI renvoie 422 s'il est absent.
# Aucune contrainte de longueur côté Query : un token *fourni* mais malformé
# (trop court, trop long, caractères invalides) ne peut par construction
# matcher aucune ligne en DB ; on délègue donc à ``AuthService.verify_email``
# qui retourne 400 ``INVALID_OR_EXPIRED_TOKEN`` (cf. AC4) — c'est sémantiquement
# correct et indistinguable d'un token expiré côté client.
VerificationToken = Annotated[
    str, Query(description="Token de vérification reçu par email.")
]


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    """Pose le cookie ``refresh_token`` avec les attributs sécurité requis.

    Centralisé pour garantir que ``login`` et ``refresh`` utilisent
    rigoureusement les mêmes attributs (path, samesite, httponly, secure,
    max_age) — toute divergence fragiliserait la rotation.
    """
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="strict",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86_400,
        path=REFRESH_COOKIE_PATH,
    )


def _invalid_refresh_token() -> HTTPException:
    """HTTPException 401 standardisée pour les échecs de refresh."""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "error": {
                "code": "INVALID_REFRESH_TOKEN",
                "message": "Token de rafraîchissement invalide ou expiré.",
            }
        },
    )


@router.post(
    "/register",
    response_model=TeacherCreated,
    status_code=201,
    summary="Inscription d'un nouvel enseignant",
)
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def register(
    request: Request,
    body: RegisterRequest,
    background_tasks: BackgroundTasks,
    db: DbSession,
) -> TeacherCreated:
    """Crée un compte ``pending`` et envoie l'email de confirmation."""
    service = AuthService(db)
    teacher = await service.register_teacher(
        email=body.email,
        password=body.password,
        background_tasks=background_tasks,
    )
    return TeacherCreated(
        id=teacher.id,
        email=teacher.email,
        status=teacher.status,
    )


@router.get(
    "/verify-email",
    response_model=VerifyEmailResponse,
    summary="Confirmation de l'email d'un enseignant via token",
)
async def verify_email(
    request: Request,
    token: VerificationToken,
    db: DbSession,
) -> VerifyEmailResponse:
    """Active le compte associé si le token est valide et non expiré."""
    service = AuthService(db)
    await service.verify_email(token)
    return VerifyEmailResponse(message="Email confirmé.")


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=200,
    summary="Connexion enseignant",
)
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def login(
    request: Request,
    body: LoginRequest,
    response: Response,
    db: DbSession,
) -> LoginResponse:
    """Authentifie un enseignant et renvoie un access token + cookie refresh.

    AC1-3 (story 1.4) : credentials corrects → 200, ``pending`` → 403,
    credentials erronés → 401 indistinguable. Le service applique le pattern
    timing-constant pour neutraliser l'énumération d'emails.
    """
    service = AuthService(db)
    teacher = await service.login_teacher(email=body.email, password=body.password)

    subject = str(teacher.id)
    access_token = create_access_token({"sub": subject})
    refresh_token = create_refresh_token({"sub": subject})
    _set_refresh_cookie(response, refresh_token)
    return LoginResponse(access_token=access_token)


@router.post(
    "/refresh",
    response_model=LoginResponse,
    status_code=200,
    summary="Rafraîchissement du token d'accès",
)
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def refresh(
    request: Request,
    response: Response,
    db: DbSession,
    refresh_token_cookie: Annotated[
        str | None, Cookie(alias=REFRESH_COOKIE_NAME)
    ] = None,
) -> LoginResponse:
    """Renouvelle l'access token et fait tourner le refresh token (cookie).

    AC4-5 (story 1.4) : cookie valide → 200 + nouveau couple, sinon → 401
    ``INVALID_REFRESH_TOKEN``. Rotation systématique : on régénère TOUJOURS
    le refresh_token côté cookie afin que le précédent soit caduc (même s'il
    n'a pas encore expiré côté JWT — la signature reste valide, mais le
    suivant attendu par le navigateur change).
    """
    if not refresh_token_cookie:
        raise _invalid_refresh_token()

    payload: dict[str, Any] | None = decode_token(refresh_token_cookie)
    if payload is None:
        raise _invalid_refresh_token()

    sub = payload.get("sub")
    if not isinstance(sub, str) or not sub:
        raise _invalid_refresh_token()

    try:
        teacher_id = uuid.UUID(sub)
    except ValueError:
        raise _invalid_refresh_token() from None

    repo = TeacherRepository(db)
    teacher = await repo.get_by_id(teacher_id)
    if teacher is None or teacher.status != "active":
        # Compte supprimé ou désactivé entre-temps : refus.
        raise _invalid_refresh_token()

    subject = str(teacher.id)
    new_access = create_access_token({"sub": subject})
    new_refresh = create_refresh_token({"sub": subject})
    _set_refresh_cookie(response, new_refresh)

    logger.info("auth.refreshed", teacher_id=subject)
    return LoginResponse(access_token=new_access)


@router.post(
    "/logout",
    status_code=200,
    summary="Déconnexion enseignant",
)
async def logout(response: Response) -> dict[str, str]:
    """Supprime le cookie ``refresh_token`` côté client (Max-Age=0).

    Endpoint idempotent (pas d'erreur si le cookie est déjà absent). Côté
    client, ``AuthContext.logout`` se charge en parallèle d'effacer l'access
    token en mémoire.
    """
    response.delete_cookie(
        key=REFRESH_COOKIE_NAME,
        path=REFRESH_COOKIE_PATH,
        httponly=True,
        samesite="strict",
        secure=settings.COOKIE_SECURE,
    )
    return {"message": "Déconnecté."}
