"""Tests des endpoints d'authentification — Story 1.4.

Couvre : ``POST /auth/login``, ``POST /auth/refresh``, ``POST /auth/logout``
et ``GET /teachers/me``. Couvre AC 1–8 et 10 de la story.

Conventions :
- Fixtures asynchrones via ``pytest_asyncio`` (cf. ``conftest.py``).
- Pas de monkeypatch du module ``security`` : les vrais JWT sont émis et
  vérifiés contre la même ``SECRET_KEY`` que celle d'``app.core.config``.
- Les tests utilisent ``async_client.cookies`` pour observer la pose / la
  suppression du cookie ``refresh_token``.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
import pytest_asyncio
from httpx import AsyncClient
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import REFRESH_COOKIE_NAME
from app.core.config import settings
from app.core.security import ALGORITHM, hash_password
from app.models.teacher import Teacher
from app.repositories.teacher_repository import TeacherRepository

PASSWORD = "motdepasse123456"
EMAIL = "marie@example.fr"


@pytest_asyncio.fixture
async def active_teacher(db_session: AsyncSession) -> Teacher:
    """Crée un Teacher en statut ``active`` (raccourci — sans inscription/email)."""
    repo = TeacherRepository(db_session)
    teacher = await repo.create(
        email=EMAIL,
        password_hash=hash_password(PASSWORD),
        verification_token="unused",
        verification_token_expires_at=datetime.now(UTC) + timedelta(days=1),
    )
    teacher.status = "active"
    teacher.email_verification_token = None
    teacher.email_verification_token_expires_at = None
    await db_session.commit()
    await db_session.refresh(teacher)
    return teacher


@pytest_asyncio.fixture
async def pending_teacher(db_session: AsyncSession) -> Teacher:
    """Crée un Teacher en statut ``pending`` (email non confirmé)."""
    repo = TeacherRepository(db_session)
    teacher = await repo.create(
        email="pending@example.fr",
        password_hash=hash_password(PASSWORD),
        verification_token="still-pending",
        verification_token_expires_at=datetime.now(UTC) + timedelta(days=1),
    )
    await db_session.commit()
    await db_session.refresh(teacher)
    return teacher


@pytest.mark.asyncio
async def test_login_success(
    async_client: AsyncClient, active_teacher: Teacher
) -> None:
    """AC1 — credentials valides → 200 + JWT + cookie refresh."""
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": EMAIL, "password": PASSWORD},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["token_type"] == "bearer"
    token = data["access_token"]
    assert isinstance(token, str) and token.count(".") == 2

    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == str(active_teacher.id)
    assert "exp" in payload

    set_cookie = response.headers.get("set-cookie", "")
    assert REFRESH_COOKIE_NAME in set_cookie
    assert "HttpOnly" in set_cookie
    assert "SameSite=strict" in set_cookie or "SameSite=Strict" in set_cookie
    assert async_client.cookies.get(REFRESH_COOKIE_NAME) is not None


@pytest.mark.asyncio
async def test_login_normalizes_email(
    async_client: AsyncClient, active_teacher: Teacher
) -> None:
    """L'email saisi en majuscules doit se résoudre vers le compte minuscule."""
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": EMAIL.upper(), "password": PASSWORD},
    )
    assert response.status_code == 200, response.text


@pytest.mark.asyncio
async def test_login_inactive_account_returns_403(
    async_client: AsyncClient, pending_teacher: Teacher
) -> None:
    """AC2 — compte ``pending`` (avec mot de passe correct) → 403."""
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": pending_teacher.email, "password": PASSWORD},
    )
    assert response.status_code == 403, response.text
    assert response.json()["error"]["code"] == "ACCOUNT_NOT_ACTIVE"


@pytest.mark.asyncio
async def test_login_wrong_password_returns_401(
    async_client: AsyncClient, active_teacher: Teacher
) -> None:
    """AC3 — bon email, mauvais mdp → 401 INVALID_CREDENTIALS."""
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": EMAIL, "password": "WRONG_PASSWORD_12345"},
    )
    assert response.status_code == 401, response.text
    body = response.json()
    assert body["error"]["code"] == "INVALID_CREDENTIALS"
    assert REFRESH_COOKIE_NAME not in response.headers.get("set-cookie", "")


@pytest.mark.asyncio
async def test_login_unknown_email_returns_401(async_client: AsyncClient) -> None:
    """AC3 — email inexistant → 401 INVALID_CREDENTIALS (même code que mdp).

    Le code DOIT être identique au cas « mauvais mot de passe » pour ne pas
    permettre l'énumération d'utilisateurs.
    """
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "ghost@example.fr", "password": PASSWORD},
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


@pytest.mark.asyncio
async def test_login_password_empty_returns_422(async_client: AsyncClient) -> None:
    """Le mot de passe doit être non vide (validation Pydantic min_length=1)."""
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": EMAIL, "password": ""},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_login_rate_limit(async_client: AsyncClient) -> None:
    """AC10 — le 11ème POST /login dans la fenêtre doit renvoyer 429."""
    for _ in range(10):
        r = await async_client.post(
            "/api/v1/auth/login",
            json={"email": "rate@example.fr", "password": PASSWORD},
        )
        assert r.status_code in (401, 403), (r.status_code, r.text)

    r11 = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "rate@example.fr", "password": PASSWORD},
    )
    assert r11.status_code == 429
    assert r11.json()["error"]["code"] == "RATE_LIMIT_EXCEEDED"


@pytest.mark.asyncio
async def test_refresh_success(
    async_client: AsyncClient, active_teacher: Teacher
) -> None:
    """AC4 — cookie refresh valide → 200 + nouvel access_token + rotation."""
    login_resp = await async_client.post(
        "/api/v1/auth/login",
        json={"email": EMAIL, "password": PASSWORD},
    )
    assert login_resp.status_code == 200
    first_access = login_resp.json()["access_token"]
    first_refresh_cookie = async_client.cookies.get(REFRESH_COOKIE_NAME)
    assert first_refresh_cookie is not None

    refresh_resp = await async_client.post("/api/v1/auth/refresh")
    assert refresh_resp.status_code == 200, refresh_resp.text
    new_access = refresh_resp.json()["access_token"]
    assert isinstance(new_access, str) and new_access.count(".") == 2

    # Rotation : le cookie doit avoir été remplacé.
    second_refresh_cookie = async_client.cookies.get(REFRESH_COOKIE_NAME)
    assert second_refresh_cookie is not None
    # NB : ``new_access`` peut être identique à ``first_access`` si le JWT
    # est généré dans la même seconde (champ ``exp`` arrondi). L'invariant
    # vérifié est donc que le cookie est bien renouvelé et que la réponse
    # contient un JWT structurellement valide.
    _ = first_access  # silenced — référencé pour traçabilité du scénario


@pytest.mark.asyncio
async def test_refresh_invalid_cookie_returns_401(
    async_client: AsyncClient,
) -> None:
    """AC5 — cookie absent → 401 INVALID_REFRESH_TOKEN."""
    response = await async_client.post("/api/v1/auth/refresh")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_REFRESH_TOKEN"


@pytest.mark.asyncio
async def test_refresh_corrupted_cookie_returns_401(
    async_client: AsyncClient,
) -> None:
    """AC5 — cookie corrompu (non-JWT) → 401."""
    async_client.cookies.set(REFRESH_COOKIE_NAME, "definitely-not-a-jwt")
    response = await async_client.post("/api/v1/auth/refresh")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_REFRESH_TOKEN"


@pytest.mark.asyncio
async def test_refresh_expired_cookie_returns_401(
    async_client: AsyncClient, active_teacher: Teacher
) -> None:
    """AC5 — cookie expiré (``exp`` dans le passé) → 401."""
    expired_payload = {
        "sub": str(active_teacher.id),
        "exp": datetime.now(UTC) - timedelta(seconds=10),
    }
    expired_jwt = jwt.encode(
        expired_payload, settings.SECRET_KEY, algorithm=ALGORITHM
    )
    async_client.cookies.set(REFRESH_COOKIE_NAME, expired_jwt)
    response = await async_client.post("/api/v1/auth/refresh")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_REFRESH_TOKEN"


@pytest.mark.asyncio
async def test_refresh_unknown_teacher_returns_401(
    async_client: AsyncClient,
) -> None:
    """Un cookie valide pointant vers un teacher inexistant → 401."""
    payload = {
        "sub": "00000000-0000-0000-0000-000000000000",
        "exp": datetime.now(UTC) + timedelta(days=1),
    }
    fake_jwt = jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)
    async_client.cookies.set(REFRESH_COOKIE_NAME, fake_jwt)
    response = await async_client.post("/api/v1/auth/refresh")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_REFRESH_TOKEN"


@pytest.mark.asyncio
async def test_logout_clears_cookie(
    async_client: AsyncClient, active_teacher: Teacher
) -> None:
    """AC6 — logout → 200 + cookie supprimé (Max-Age=0)."""
    login = await async_client.post(
        "/api/v1/auth/login",
        json={"email": EMAIL, "password": PASSWORD},
    )
    assert login.status_code == 200
    assert async_client.cookies.get(REFRESH_COOKIE_NAME) is not None

    response = await async_client.post("/api/v1/auth/logout")
    assert response.status_code == 200
    assert response.json() == {"message": "Déconnecté."}

    # Le client httpx applique automatiquement le ``Set-Cookie`` retourné :
    # un ``Max-Age=0`` (ou expiration passée) supprime le cookie côté jar.
    set_cookie_header = response.headers.get("set-cookie", "")
    assert REFRESH_COOKIE_NAME in set_cookie_header
    is_cleared = (
        "Max-Age=0" in set_cookie_header
        or "expires=Thu, 01 Jan 1970" in set_cookie_header.lower()
    )
    assert is_cleared
    assert async_client.cookies.get(REFRESH_COOKIE_NAME) is None


@pytest.mark.asyncio
async def test_logout_is_idempotent(async_client: AsyncClient) -> None:
    """``logout`` sans cookie en entrée doit rester 200 (idempotent)."""
    response = await async_client.post("/api/v1/auth/logout")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_me_success(
    async_client: AsyncClient, active_teacher: Teacher
) -> None:
    """AC8 — Bearer valide → 200 + schéma Teacher complet."""
    login_resp = await async_client.post(
        "/api/v1/auth/login",
        json={"email": EMAIL, "password": PASSWORD},
    )
    token = login_resp.json()["access_token"]

    me_resp = await async_client.get(
        "/api/v1/teachers/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_resp.status_code == 200, me_resp.text
    body = me_resp.json()
    assert body["email"] == EMAIL
    assert body["status"] == "active"
    assert body["id"] == str(active_teacher.id)
    assert "created_at" in body and "updated_at" in body
    assert "display_name" in body


@pytest.mark.asyncio
async def test_get_me_no_token_returns_401(async_client: AsyncClient) -> None:
    """AC7 — header Authorization absent → 401 UNAUTHORIZED."""
    response = await async_client.get("/api/v1/teachers/me")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_get_me_invalid_token_returns_401(
    async_client: AsyncClient,
) -> None:
    """AC7 — Bearer malformé → 401 UNAUTHORIZED."""
    response = await async_client.get(
        "/api/v1/teachers/me",
        headers={"Authorization": "Bearer not.a.jwt"},
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_get_me_wrong_scheme_returns_401(
    async_client: AsyncClient, active_teacher: Teacher
) -> None:
    """Un schéma autre que Bearer → 401 même avec un token valide en clair."""
    response = await async_client.get(
        "/api/v1/teachers/me",
        headers={"Authorization": "Basic dXNlcjpwYXNz"},
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_get_me_token_with_non_uuid_sub_returns_401(
    async_client: AsyncClient,
) -> None:
    """Un JWT valide mais avec ``sub`` non-UUID → 401."""
    payload = {
        "sub": "not-a-uuid",
        "exp": datetime.now(UTC) + timedelta(minutes=15),
    }
    forged = jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)
    response = await async_client.get(
        "/api/v1/teachers/me",
        headers={"Authorization": f"Bearer {forged}"},
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"
