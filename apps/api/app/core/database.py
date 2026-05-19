"""Session SQLAlchemy async + dépendance FastAPI ``get_db``.

Story 1.3 — Inscription enseignant.

L'engine utilise le ``DATABASE_URL`` injecté via ``Settings`` (driver
``asyncpg`` en prod, ``aiosqlite`` en tests). Le fixture ``conftest.py``
peut surcharger ``get_db`` via ``app.dependency_overrides``.
"""
from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield une session SQLAlchemy async — à utiliser via ``Depends(get_db)``.

    La session est commitée si aucune exception, sinon rollback automatique.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
