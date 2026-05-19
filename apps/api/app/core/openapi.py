"""Chargement et exposition du contrat OpenAPI versionné (source de vérité unique)."""
from pathlib import Path
from typing import Any, cast

import yaml

from app.core.config import settings


def load_openapi_schema() -> dict[str, Any]:
    """Charge le contrat OpenAPI depuis le fichier YAML versionné.

    Retourne le dict OpenAPI utilisable par FastAPI (consommé par `/openapi.json`
    et `/docs`). Le YAML est la source de vérité unique ; aucune génération depuis
    les modèles Pydantic.
    """
    path = Path(settings.OPENAPI_CONTRACT_PATH).resolve()
    if not path.is_file():
        raise FileNotFoundError(
            f"OpenAPI contract not found at {path}. "
            "Set OPENAPI_CONTRACT_PATH or mount contracts/ in Docker."
        )
    with path.open("r", encoding="utf-8") as f:
        schema = yaml.safe_load(f)
    if not isinstance(schema, dict):
        raise ValueError(f"Invalid OpenAPI YAML at {path}: expected mapping at root")
    return cast(dict[str, Any], schema)
