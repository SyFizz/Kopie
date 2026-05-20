"""Endpoints enseignant authentifiés — Story 1.4.

Pour l'instant le seul endpoint est ``GET /teachers/me``, point d'entrée
canonique pour récupérer le profil de l'enseignant courant. Toutes les
routes ajoutées ici DOIVENT dépendre de ``CurrentTeacher`` afin que les
règles d'isolation (FR-3) soient appliquées de manière homogène.
"""
from __future__ import annotations

from fastapi import APIRouter

from app.core.dependencies import CurrentTeacher
from app.schemas.teacher import TeacherPublic

router = APIRouter(prefix="/teachers")


@router.get(
    "/me",
    response_model=TeacherPublic,
    summary="Profil de l'enseignant connecté",
)
async def get_me(teacher: CurrentTeacher) -> TeacherPublic:
    """Retourne le profil complet de l'enseignant identifié par le Bearer JWT.

    Les timestamps sont sérialisés au format ISO 8601 UTC pour s'aligner sur
    le contrat OpenAPI (`format: date-time`).
    """
    return TeacherPublic(
        id=teacher.id,
        email=teacher.email,
        display_name=teacher.display_name,
        status=teacher.status,
        created_at=teacher.created_at.isoformat(),
        updated_at=teacher.updated_at.isoformat(),
    )
