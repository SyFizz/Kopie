"""Tests des endpoints d'inscription / vérification email — Story 1.3."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.teacher import Teacher

PASSWORD = "motdepasse123456"


@pytest.fixture(autouse=True)
def _patch_send_email(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Empêche les tests d'appeler réellement smtplib."""
    mock = MagicMock()
    monkeypatch.setattr(
        "app.services.auth_service.send_verification_email", mock
    )
    return mock


async def _get_teacher_by_email(
    session: AsyncSession, email: str
) -> Teacher | None:
    result = await session.execute(
        select(Teacher).where(Teacher.email == email)
    )
    return result.scalar_one_or_none()


@pytest.mark.asyncio
async def test_register_success(
    async_client: AsyncClient, db_session: AsyncSession
) -> None:
    """AC1 — POST valide retourne 201 et crée un compte ``pending``."""
    payload: dict[str, Any] = {
        "email": "marie.dupont@example.fr",
        "password": PASSWORD,
    }
    response = await async_client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["email"] == payload["email"]
    assert body["status"] == "pending"
    assert "id" in body

    teacher = await _get_teacher_by_email(db_session, payload["email"])
    assert teacher is not None
    assert teacher.status == "pending"
    assert teacher.email_verification_token is not None
    assert teacher.email_verification_token_expires_at is not None
    assert teacher.password_hash != PASSWORD  # bcrypt hash


@pytest.mark.asyncio
async def test_register_sends_verification_email_background(
    async_client: AsyncClient, _patch_send_email: MagicMock
) -> None:
    """AC1 — l'email de vérification est planifié via BackgroundTasks."""
    response = await async_client.post(
        "/api/v1/auth/register",
        json={"email": "background@example.fr", "password": PASSWORD},
    )
    assert response.status_code == 201
    assert _patch_send_email.called
    args, _ = _patch_send_email.call_args
    assert args[0] == "background@example.fr"
    assert isinstance(args[1], str) and len(args[1]) >= 32


@pytest.mark.asyncio
async def test_register_duplicate_email(async_client: AsyncClient) -> None:
    """AC2 — second POST avec le même email → 409 EMAIL_ALREADY_REGISTERED."""
    payload = {"email": "duplicate@example.fr", "password": PASSWORD}
    r1 = await async_client.post("/api/v1/auth/register", json=payload)
    assert r1.status_code == 201

    r2 = await async_client.post("/api/v1/auth/register", json=payload)
    assert r2.status_code == 409
    body = r2.json()
    assert body["error"]["code"] == "EMAIL_ALREADY_REGISTERED"


@pytest.mark.asyncio
async def test_register_invalid_password(async_client: AsyncClient) -> None:
    """AC1 — mot de passe < 12 caractères → 422."""
    response = await async_client.post(
        "/api/v1/auth/register",
        json={"email": "short@example.fr", "password": "trop_court"},
    )
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_register_invalid_email(async_client: AsyncClient) -> None:
    """AC1 — email malformé → 422."""
    response = await async_client.post(
        "/api/v1/auth/register",
        json={"email": "pas-un-email", "password": PASSWORD},
    )
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_register_normalizes_email_lowercase(
    async_client: AsyncClient, db_session: AsyncSession
) -> None:
    """L'email est normalisé en minuscules (idempotence)."""
    response = await async_client.post(
        "/api/v1/auth/register",
        json={"email": "Mixed.Case@Example.FR", "password": PASSWORD},
    )
    assert response.status_code == 201
    teacher = await _get_teacher_by_email(db_session, "mixed.case@example.fr")
    assert teacher is not None
    assert teacher.email == "mixed.case@example.fr"


@pytest.mark.asyncio
async def test_verify_email_success(
    async_client: AsyncClient, db_session: AsyncSession
) -> None:
    """AC3 — token valide → 200 et compte ``active``."""
    await async_client.post(
        "/api/v1/auth/register",
        json={"email": "verify@example.fr", "password": PASSWORD},
    )
    teacher = await _get_teacher_by_email(db_session, "verify@example.fr")
    assert teacher is not None
    token = teacher.email_verification_token
    assert token is not None

    response = await async_client.get(
        "/api/v1/auth/verify-email", params={"token": token}
    )
    assert response.status_code == 200, response.text
    assert response.json() == {"message": "Email confirmé."}

    await db_session.refresh(teacher)
    assert teacher.status == "active"
    assert teacher.email_verification_token is None


@pytest.mark.asyncio
async def test_verify_email_expired(
    async_client: AsyncClient, db_session: AsyncSession
) -> None:
    """AC4 — token expiré → 400 INVALID_OR_EXPIRED_TOKEN."""
    await async_client.post(
        "/api/v1/auth/register",
        json={"email": "expired@example.fr", "password": PASSWORD},
    )
    teacher = await _get_teacher_by_email(db_session, "expired@example.fr")
    assert teacher is not None
    teacher.email_verification_token_expires_at = datetime.now(
        UTC
    ) - timedelta(hours=1)
    await db_session.commit()
    token = teacher.email_verification_token
    assert token is not None

    response = await async_client.get(
        "/api/v1/auth/verify-email", params={"token": token}
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_OR_EXPIRED_TOKEN"

    await db_session.refresh(teacher)
    assert teacher.status == "pending"


@pytest.mark.asyncio
async def test_verify_email_invalid_token(async_client: AsyncClient) -> None:
    """AC4 — token inconnu → 400 INVALID_OR_EXPIRED_TOKEN."""
    response = await async_client.get(
        "/api/v1/auth/verify-email",
        params={"token": "totalement-bidon-1234567890"},
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_OR_EXPIRED_TOKEN"


@pytest.mark.asyncio
async def test_verify_email_missing_token(async_client: AsyncClient) -> None:
    """Le paramètre ``token`` est obligatoire (422 si absent)."""
    response = await async_client.get("/api/v1/auth/verify-email")
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_register_rate_limit(async_client: AsyncClient) -> None:
    """AC5 — le 11ème POST /register dans la fenêtre doit renvoyer 429."""
    for i in range(10):
        r = await async_client.post(
            "/api/v1/auth/register",
            json={"email": f"rl{i}@example.fr", "password": PASSWORD},
        )
        assert r.status_code in (201, 409), (i, r.status_code, r.text)

    r11 = await async_client.post(
        "/api/v1/auth/register",
        json={"email": "rl11@example.fr", "password": PASSWORD},
    )
    assert r11.status_code == 429
    body = r11.json()
    assert body["error"]["code"] == "RATE_LIMIT_EXCEEDED"
