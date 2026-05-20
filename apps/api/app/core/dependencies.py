"""Dépendances FastAPI partagées — authentification enseignant (Story 1.4).

Ce module expose la dépendance ``get_current_teacher`` à utiliser sur toutes
les routes protégées de l'API enseignant. Elle :

1. Lit le header ``Authorization: Bearer <token>`` (schéma ``HTTPBearer``
   avec ``auto_error=False`` pour qu'un en-tête absent nous renvoie ``None``
   plutôt qu'un 403 automatique).
2. Décode le JWT via ``decode_token`` (retourne ``None`` si invalide/expiré).
3. Vérifie que le ``sub`` est un UUID valide pointant vers un enseignant
   existant en base.

En cas d'échec à n'importe laquelle de ces étapes : ``HTTPException(401,
UNAUTHORIZED)``. L'enveloppe JSON respecte le contrat OpenAPI (schéma
``Error``).
"""
from __future__ import annotations

import uuid
from typing import Annotated

import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.models.teacher import Teacher
from app.repositories.teacher_repository import TeacherRepository

logger = structlog.get_logger(__name__)

# ``auto_error=False`` est essentiel : sans cette option FastAPI renvoie une
# 403 « Not authenticated » dès qu'il n'y a pas d'en-tête, ce qui détonne du
# format ``Error`` attendu par le contrat OpenAPI. On veut une 401 uniforme
# avec ``code: UNAUTHORIZED`` quel que soit le mode de défaillance.
_bearer_scheme = HTTPBearer(auto_error=False)


def _unauthorized() -> HTTPException:
    """Construit la HTTPException 401 standardisée pour la story 1.4.

    Instanciée dynamiquement (et non en constante module) pour éviter qu'un
    test (ou middleware) ne mute par mégarde l'instance partagée — chaque
    appel produit son propre objet, conforme au format ``Error``.
    """
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "error": {
                "code": "UNAUTHORIZED",
                "message": "Authentification requise.",
            }
        },
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_teacher(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)
    ],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Teacher:
    """Récupère l'enseignant authentifié depuis le Bearer token.

    Tout échec d'authentification — header absent, schéma autre que Bearer,
    token malformé/expiré, ``sub`` invalide, enseignant introuvable — est
    mappé à HTTP 401 ``UNAUTHORIZED``. Aucune distinction n'est faite côté
    réponse pour limiter les fuites d'information.
    """
    if credentials is None:
        raise _unauthorized()
    if credentials.scheme.lower() != "bearer":
        raise _unauthorized()

    payload = decode_token(credentials.credentials)
    if payload is None:
        raise _unauthorized()

    sub = payload.get("sub")
    if not isinstance(sub, str) or not sub:
        raise _unauthorized()

    try:
        teacher_id = uuid.UUID(sub)
    except ValueError:
        raise _unauthorized() from None

    repo = TeacherRepository(db)
    teacher = await repo.get_by_id(teacher_id)
    if teacher is None:
        logger.info("auth.unknown_teacher_id_in_token", teacher_id=str(teacher_id))
        raise _unauthorized()

    return teacher


# Alias pratique pour annoter les endpoints :
#   async def me(teacher: CurrentTeacher) -> ...
CurrentTeacher = Annotated[Teacher, Depends(get_current_teacher)]
