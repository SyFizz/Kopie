"""Endpoint /health — vérification de santé de l'API."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    """Retourne le statut opérationnel de l'API."""
    return {"status": "ok"}
