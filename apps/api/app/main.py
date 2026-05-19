"""Point d'entrée FastAPI — Kopie API."""
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.core.openapi import load_openapi_schema
from app.core.rate_limit import limiter

configure_logging()

app = FastAPI(
    title="Kopie API",
    version="0.2.0",
    description=(
        "Plateforme d'évaluation sécurisée — API REST. "
        "Contrat versionné dans `contracts/openapi.yaml` (source de vérité unique)."
    ),
)

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(
    request: Request, exc: RateLimitExceeded
) -> JSONResponse:
    """Réponse 429 au format ``Error`` du contrat OpenAPI."""
    return JSONResponse(
        status_code=429,
        content={
            "error": {
                "code": "RATE_LIMIT_EXCEEDED",
                "message": (
                    "Trop de requêtes — veuillez réessayer dans quelques instants."
                ),
                "details": {"limit": str(exc.detail)},
            }
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request, exc: HTTPException
) -> JSONResponse:
    """Normalise les HTTPException au format ``Error``.

    Si ``detail`` est déjà un dict ``{"error": {...}}`` (cas des services),
    on le sert tel quel. Sinon on l'enveloppe.
    """
    detail = exc.detail
    if isinstance(detail, dict) and "error" in detail:
        return JSONResponse(status_code=exc.status_code, content=detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "HTTP_ERROR",
                "message": str(detail),
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Réponse 422 au format ``Error`` du contrat OpenAPI."""
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Les données fournies sont invalides.",
                "details": {"errors": exc.errors()},
            }
        },
    )


def _custom_openapi() -> dict[str, Any]:
    """Sert le contenu de contracts/openapi.yaml (source de vérité unique)."""
    if app.openapi_schema:
        return app.openapi_schema
    app.openapi_schema = load_openapi_schema()
    return app.openapi_schema


app.openapi = _custom_openapi  # type: ignore[method-assign]
