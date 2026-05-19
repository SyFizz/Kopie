"""Fixtures pytest globales — DB SQLite en mémoire + client ASGI async.

Story 1.3 — Inscription enseignant avec validation email.

Stratégie :
- Engine ``aiosqlite`` en mémoire **par test** (isolation totale).
- ``Base.metadata.create_all`` au lieu d'Alembic (plus rapide, suffisant
  pour les tests : la migration est testée séparément le cas échéant).
- ``app.dependency_overrides[get_db]`` pour injecter la session de test.
- ``limiter.reset()`` entre chaque test pour neutraliser le rate-limit
  in-memory de slowapi.
"""
from __future__ import annotations

from collections.abc import AsyncIterator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.database import get_db
from app.core.rate_limit import limiter
from app.main import app
from app.models import Base  # noqa: F401 — assure l'enregistrement des tables

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncIterator[AsyncSession]:
    """Engine SQLite en mémoire isolé par test (schema créé + droppé)."""
    engine = create_async_engine(TEST_DATABASE_URL, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def async_client(db_session: AsyncSession) -> AsyncIterator[AsyncClient]:
    """Client ASGI partageant la même session que les fixtures de test."""

    async def override_get_db() -> AsyncIterator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    limiter.reset()
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test"
    ) as client:
        yield client
    app.dependency_overrides.clear()
    limiter.reset()
