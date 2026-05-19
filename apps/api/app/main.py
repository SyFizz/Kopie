"""Point d'entrée FastAPI — Kopie API."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging

configure_logging()

app = FastAPI(
    title="Kopie API",
    version="0.1.0",
    description=(
        "Plateforme d'évaluation sécurisée — API REST. "
        "Contrat versionné dans `contracts/openapi.yaml`."
    ),
)

# CORS : origines explicites uniquement (architecture §API, NFR-sécurité)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
