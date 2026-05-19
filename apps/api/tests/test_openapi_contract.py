"""Tests d'alignement entre contracts/openapi.yaml et l'API FastAPI."""
from pathlib import Path
from typing import Any

import pytest
import yaml
from httpx import ASGITransport, AsyncClient

from app.main import app


def _load_expected_schema() -> dict[str, Any]:
    """Charge le YAML versionné depuis n'importe quel CWD de pytest."""
    candidates = [
        Path("../../contracts/openapi.yaml"),
        Path("contracts/openapi.yaml"),
        Path(__file__).resolve().parents[3] / "contracts" / "openapi.yaml",
    ]
    for candidate in candidates:
        if candidate.is_file():
            with candidate.open("r", encoding="utf-8") as f:
                schema = yaml.safe_load(f)
            assert isinstance(schema, dict)
            return schema
    raise FileNotFoundError(
        "contracts/openapi.yaml introuvable depuis les candidats : "
        + ", ".join(str(c) for c in candidates)
    )


@pytest.fixture
def expected_schema() -> dict[str, Any]:
    return _load_expected_schema()


@pytest.fixture(autouse=True)
def _reset_openapi_cache() -> None:
    """Reset du cache `app.openapi_schema` entre tests (recharge le YAML disque)."""
    app.openapi_schema = None


@pytest.mark.asyncio
async def test_openapi_json_serves_yaml_contract(
    expected_schema: dict[str, Any],
) -> None:
    """`/openapi.json` doit servir exactement le contenu de contracts/openapi.yaml."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/openapi.json")

    assert response.status_code == 200
    body = response.json()

    assert body["info"]["title"] == "Kopie API"
    assert body["info"]["version"] == "0.1.0"
    assert body["openapi"] == "3.1.0"

    assert "Teacher" in body["components"]["schemas"]
    assert "Error" in body["components"]["schemas"]
    assert "/api/v1/health" in body["paths"]

    assert body == expected_schema


@pytest.mark.asyncio
async def test_docs_endpoint_returns_swagger_ui() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/docs")

    assert response.status_code == 200
    assert "Kopie API" in response.text or "swagger" in response.text.lower()


@pytest.mark.asyncio
async def test_teacher_schema_required_fields(
    expected_schema: dict[str, Any],
) -> None:
    """Le schéma Teacher doit avoir les champs MVP requis."""
    teacher = expected_schema["components"]["schemas"]["Teacher"]
    assert teacher["type"] == "object"
    required = set(teacher["required"])
    assert {
        "id",
        "email",
        "display_name",
        "status",
        "created_at",
        "updated_at",
    } <= required
    assert teacher["properties"]["id"]["format"] == "uuid"
    assert teacher["properties"]["email"]["format"] == "email"
    assert teacher["properties"]["status"]["enum"] == ["pending", "active"]
