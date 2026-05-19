"""Endpoints d'authentification — Story 1.3.

Routes :
- ``POST /auth/register`` (rate-limité — ``RATE_LIMIT_AUTH``)
- ``GET /auth/verify-email`` (porteur du token, pas d'auth)
"""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.rate_limit import limiter
from app.schemas.teacher import (
    RegisterRequest,
    TeacherCreated,
    VerifyEmailResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth")

DbSession = Annotated[AsyncSession, Depends(get_db)]

# Le paramètre ``token`` est obligatoire — FastAPI renvoie 422 s'il est absent.
# Aucune contrainte de longueur côté Query : un token *fourni* mais malformé
# (trop court, trop long, caractères invalides) ne peut par construction
# matcher aucune ligne en DB ; on délègue donc à ``AuthService.verify_email``
# qui retourne 400 ``INVALID_OR_EXPIRED_TOKEN`` (cf. AC4) — c'est sémantiquement
# correct et indistinguable d'un token expiré côté client.
VerificationToken = Annotated[
    str, Query(description="Token de vérification reçu par email.")
]


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
