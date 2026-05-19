"""Point d'entrée FastAPI — Kopie API."""
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.core.openapi import load_openapi_schema

configure_logging()

app = FastAPI(
    title="Kopie API",
    version="0.1.0",
    description=(
        "Plateforme d'évaluation sécurisée — API REST. "
        "Contrat versionné dans `contracts/openapi.yaml` (source de vérité unique)."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


def _custom_openapi() -> dict[str, Any]:
    """Sert le contenu de contracts/openapi.yaml (source de vérité unique)."""
    if app.openapi_schema:
        return app.openapi_schema
    app.openapi_schema = load_openapi_schema()
    return app.openapi_schema


app.openapi = _custom_openapi  # type: ignore[method-assign]
