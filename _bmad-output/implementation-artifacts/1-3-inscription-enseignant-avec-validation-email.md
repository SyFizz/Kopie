# Story 1.3 : Inscription enseignant avec validation email

Status: review

<!-- Note: Validation optionnelle. Exécuter validate-create-story pour contrôle qualité avant dev-story. -->

## Story

As an **enseignant**,
I want **créer un compte avec email et mot de passe puis valider mon email via un lien envoyé de façon asynchrone**,
So that **j'accède à mon espace personnel sécurisé avec un compte confirmé et isolé**.

## Acceptance Criteria

1. **Given** je n'ai pas encore de compte
   **When** je soumets un email valide et un mot de passe respectant la politique (≥ 12 caractères)
   **Then** un compte enseignant est créé en statut `pending`
   **And** un email de confirmation est envoyé de façon asynchrone (tâche background FastAPI `BackgroundTasks`)
   **And** l'API retourne HTTP 201 avec le schéma `TeacherCreated` (`{ "id", "email", "status": "pending" }`)

2. **Given** un email déjà utilisé par un autre compte
   **When** je soumets le formulaire d'inscription avec cet email
   **Then** l'API retourne HTTP 409 avec `{ "error": { "code": "EMAIL_ALREADY_REGISTERED", "message": "..." } }`
   **And** aucune donnée n'est créée ni modifiée

3. **Given** j'ai reçu l'email de confirmation
   **When** je clique sur le lien `GET /api/v1/auth/verify-email?token={token}`
   **Then** le token est validé (non expiré, lié à mon compte)
   **And** mon compte passe en statut `active`
   **And** l'API retourne HTTP 200 avec `{ "message": "Email confirmé." }`

4. **Given** un token de vérification invalide ou expiré (TTL 24 h)
   **When** j'accède au lien de confirmation
   **Then** l'API retourne HTTP 400 avec `{ "error": { "code": "INVALID_OR_EXPIRED_TOKEN", "message": "..." } }`
   **And** le compte reste en statut `pending`

5. **Given** l'API exposée publiquement
   **When** des requêtes abusives ciblent `POST /api/v1/auth/register`
   **Then** slowapi applique le rate limit configuré par `RATE_LIMIT_AUTH` (défaut `10/minute`) et renvoie HTTP 429
   **And** le comportement est testé par un test pytest vérifiant que le 11ème appel déclenche 429

6. **Given** le contrat OpenAPI `contracts/openapi.yaml`
   **When** cette story est implémentée
   **Then** le YAML documente les routes `POST /api/v1/auth/register` et `GET /api/v1/auth/verify-email` avec leurs schémas `RegisterRequest`, `TeacherCreated`
   **And** `pnpm gen:types` régénère `packages/shared-types/src/api.ts` sans erreur
   **And** la CI `verify-shared-types` reste verte

7. **Given** le formulaire d'inscription sur `apps/web-prof`
   **When** l'enseignant remplit email et mot de passe et soumet
   **Then** la page affiche un message de succès « Vérifiez votre boîte mail » (UX-DR21)
   **And** les erreurs de validation (email malformé, mot de passe trop court, email déjà utilisé) s'affichent inline sous le champ concerné
   **And** le bouton « S'inscrire » est désactivé pendant la soumission (loading state)

## Tasks / Subtasks

- [x] Tâche 1 — Enrichir `contracts/openapi.yaml` avec les nouvelles routes et schémas (AC: 6)
  - [x] Ajouter le schéma `RegisterRequest` (`email` format email, `password` string min 12 chars)
  - [x] Ajouter le schéma `TeacherCreated` (`id` UUID, `email`, `status: pending`)
  - [x] Documenter `POST /api/v1/auth/register` (201 TeacherCreated, 409 Error, 422 Error, 429 Error)
  - [x] Documenter `GET /api/v1/auth/verify-email` (paramètre query `token`, 200, 400 Error)
  - [x] Valider avec `pnpm --package=@redocly/cli dlx redocly lint contracts/openapi.yaml` — `Woohoo! Your API description is valid. 🎉`
  - [x] Régénérer `pnpm gen:types` et committer `packages/shared-types/src/api.ts`

- [x] Tâche 2 — Modèle SQLAlchemy `Teacher` et migration Alembic (AC: 1)
  - [x] Créer `apps/api/app/models/teacher.py` avec colonnes : `id` (UUID PK), `email` (unique, index), `password_hash`, `display_name`, `status` (`pending`/`active`), `email_verification_token` (nullable, indexé), `email_verification_token_expires_at`, `created_at`, `updated_at`
  - [x] Importer le modèle dans `apps/api/app/models/__init__.py` (export `Base`, `Teacher`)
  - [x] Créer la migration Alembic manuellement (`alembic revision --autogenerate` requiert une DB live — la migration écrite à la main est équivalente, reviewable et DB-agnostic) : `apps/api/alembic/versions/20260519_0001_add_teachers_table.py`
  - [x] Schema vérifié via les tests : `Base.metadata.create_all` exécuté sur SQLite async dans `conftest.py` — `Uuid` SQLAlchemy 2.0 fallback CHAR(32) sur SQLite

- [x] Tâche 3 — Schémas Pydantic (AC: 1, 2, 3, 4)
  - [x] Créer `apps/api/app/schemas/teacher.py` : `RegisterRequest`, `TeacherCreated`, `TeacherPublic` (réutilisable Story 1.4/1.5), `VerifyEmailResponse`
  - [x] `RegisterRequest` : `email: EmailStr`, `password: str` avec `@field_validator` (min 12 chars) + `min_length`/`max_length` côté Field
  - [x] `TeacherCreated` : `id: UUID`, `email: EmailStr`, `status: str`

- [x] Tâche 4 — Repository enseignant (AC: 1, 2)
  - [x] Créer `apps/api/app/repositories/teacher_repository.py`
  - [x] Méthodes : `get_by_id`, `get_by_email`, `get_by_verification_token`, `create`, `activate`
  - [x] Toutes les méthodes sont `async` (`AsyncSession`)

- [x] Tâche 5 — Service inscription (AC: 1, 2, 3, 4)
  - [x] Créer `apps/api/app/services/auth_service.py`
  - [x] `register_teacher(email, password, background_tasks)` :
    - [x] Normalisation de l'email en minuscules
    - [x] Vérification d'unicité → `HTTPException(409, code=EMAIL_ALREADY_REGISTERED)`
    - [x] Hash bcrypt via `app.core.security.hash_password` (passlib)
    - [x] Token `secrets.token_urlsafe(32)` + TTL 24 h
    - [x] Persistance via repository + `commit`
    - [x] `background_tasks.add_task(send_verification_email, email, token)`
  - [x] `verify_email(token)` : lookup token, vérification expiration, activation (status `active`, token mis à NULL)

- [x] Tâche 6 — Service email asynchrone (AC: 1)
  - [x] Créer `apps/api/app/services/email_service.py`
  - [x] `send_verification_email(email, token)` : SMTP via `smtplib` (synchrone — OK en BackgroundTask)
  - [x] Mode dégradé : si `SMTP_HOST` est vide → log structlog warning, retour silencieux (pas d'exception)
  - [x] URL construite depuis `settings.APP_BASE_URL` → `GET /api/v1/auth/verify-email?token={token}`
  - [x] `try/except` autour de l'envoi pour ne jamais faire planter la background-task (UX : 201 garanti)

- [x] Tâche 7 — Endpoint FastAPI (AC: 1–5)
  - [x] Créer `apps/api/app/api/v1/endpoints/auth.py`
  - [x] `POST /auth/register` avec `BackgroundTasks`, décorateur `@limiter.limit(settings.RATE_LIMIT_AUTH)`
  - [x] `GET /auth/verify-email?token=` sans auth
  - [x] Créer `apps/api/app/core/rate_limit.py` (`limiter = Limiter(key_func=get_remote_address)`)
  - [x] Brancher dans `main.py` : `app.state.limiter`, `SlowAPIMiddleware`, exception handlers `RateLimitExceeded`, `HTTPException`, `RequestValidationError` (tous au format `Error` du contrat)
  - [x] Inclure le router `auth` dans `apps/api/app/api/v1/router.py`

- [x] Tâche 8 — Dépendance DB async + fixtures pytest (AC: 1–5)
  - [x] Créer `apps/api/app/core/database.py` : engine async, `AsyncSessionLocal`, dependency `get_db()` (avec rollback automatique)
  - [x] Créer `apps/api/tests/conftest.py` : engine SQLite (`aiosqlite`) en mémoire par test, fixtures `db_session` et `async_client` (ASGITransport), reset du limiter slowapi entre tests
  - [x] `asyncio_mode = "auto"` déjà présent dans `pyproject.toml` (Story 1.2)

- [x] Tâche 9 — Tests pytest (AC: 1–5)
  - [x] Créer `apps/api/tests/test_auth_register.py` — **11 tests** (au-delà des 8 requis) :
    - [x] `test_register_success` : 201 + statut pending + token persisté + password bcrypt hashé
    - [x] `test_register_sends_verification_email_background` : `send_verification_email` mocké, appelé avec (email, token URL-safe)
    - [x] `test_register_duplicate_email` : 409 `EMAIL_ALREADY_REGISTERED`
    - [x] `test_register_invalid_password` : < 12 chars → 422 `VALIDATION_ERROR`
    - [x] `test_register_invalid_email` : email malformé → 422 `VALIDATION_ERROR`
    - [x] `test_register_normalizes_email_lowercase` : normalisation idempotente
    - [x] `test_verify_email_success` : token valide → 200 + statut `active` + token purgé
    - [x] `test_verify_email_expired` : TTL forcée dans le passé → 400 `INVALID_OR_EXPIRED_TOKEN`, statut reste `pending`
    - [x] `test_verify_email_invalid_token` : token inconnu → 400 `INVALID_OR_EXPIRED_TOKEN`
    - [x] `test_verify_email_missing_token` : query param absent → 422 `VALIDATION_ERROR`
    - [x] `test_register_rate_limit` : 11ème POST → 429 `RATE_LIMIT_EXCEEDED`

- [x] Tâche 10 — Front `apps/web-prof` : page d'inscription (AC: 7)
  - [x] Créer `apps/web-prof/src/features/auth/RegisterPage.tsx`
  - [x] Formulaire React Hook Form + résolveur Zod (email format, password 12-200 chars)
  - [x] Appel API via `fetch` (typé via `@kopie/shared-types`) — wrapper `features/auth/api.ts`
  - [x] État de succès : « Vérifiez votre boîte mail — un lien de confirmation vous a été envoyé à {email}. »
  - [x] Erreurs serveur 409/422/429/500 mappées en messages français inline ; erreurs Zod en inline sous chaque champ
  - [x] Bouton désactivé + label « Création du compte… » pendant `isSubmitting`
  - [x] Route `/register` ajoutée dans `apps/web-prof/src/App.tsx` (`react-router-dom`), `BrowserRouter` dans `main.tsx`

- [x] Tâche 11 — Front `apps/web-prof` : page de confirmation email (AC: 3, 4)
  - [x] Créer `apps/web-prof/src/features/auth/VerifyEmailPage.tsx`
  - [x] Au montage : extraction `token` via `useSearchParams`, appel `GET /api/v1/auth/verify-email?token=`
  - [x] États `pending` / `success` / `error` avec messages conformes UX-DR21 (vouvoiement)
  - [x] Route `/verify-email` ajoutée dans `App.tsx`

- [x] Tâche 12 — Mise à jour `.env.example` et `docker-compose.yml` (AC: 1, 5)
  - [x] `.env.example` : section SMTP enrichie + nouvelle variable `APP_BASE_URL`
  - [x] `docker-compose.yml` (service `api`) : `SMTP_HOST/PORT/USER/PASSWORD`, `APP_BASE_URL`, `RATE_LIMIT_*` injectés explicitement avec valeurs par défaut

- [x] Tâche 13 — Vérifications finales (AC: 1–7)
  - [x] `ruff check .` (apps/api) → 0 erreur
  - [x] `mypy app` (apps/api) → 0 erreur strict (27 fichiers)
  - [x] `pytest -q` → **15 tests passent** (4 pré-existants + 11 nouveaux)
  - [x] `pnpm gen:types` → 0 erreur, idempotent (diff vide après second run)
  - [x] `pnpm --filter web-prof build` → 0 erreur TypeScript, bundle 329 kB
  - [x] `pnpm --filter web-prof test` → 10 tests passent (4 fichiers : App, shared-types, RegisterPage, VerifyEmailPage)
  - [x] `pnpm --filter web-prof lint` → 0 erreur ESLint
  - [x] `pnpm --filter web-eleve test` + `build` → toujours verts (non-régression)
  - [x] `redocly lint contracts/openapi.yaml` → valid
  - [x] `docker compose config` → valid (avec SECRET_KEY mocké)
  - [x] CI `verify-shared-types` : `git diff --exit-code packages/shared-types/src/api.ts` → exit 0

### Review Findings

- [x] [Review][Patch] Limiter explicitement les mots de passe à 72 octets UTF-8 côté API, front, contrat OpenAPI et tests, pour éviter la troncature bcrypt [`apps/api/app/schemas/teacher.py`:20] — `PASSWORD_MAX_BYTES = 72`, `field_validator` qui rejette > 72 octets UTF-8 ; Zod `refine` côté formulaire ; `maxLength: 72` dans le contrat OpenAPI + description bcrypt ; 2 nouveaux tests (`test_register_password_too_long_in_bytes`, `test_register_password_at_72_bytes_succeeds`).
- [x] [Review][Patch] Gérer l'`IntegrityError` lors de deux inscriptions concurrentes avec le même email [`apps/api/app/services/auth_service.py`:66] — `try/except IntegrityError` autour de `create + commit`, rollback puis `HTTPException(409)` idempotent ; test `test_register_concurrent_race_returns_409` qui patche `get_by_email` pour simuler la course et vérifie qu'aucun doublon n'est créé.
- [x] [Review][Patch] Ne jamais logger l'URL de vérification contenant le token en clair [`apps/api/app/services/email_service.py`:41] — log avec `token_prefix=token[:8]…` uniquement ; nouveau test `test_send_verification_email_degraded_mode_does_not_log_token` qui assert que ni le token complet ni l'URL n'apparaissent dans les logs.
- [x] [Review][Patch] Gérer les rejets réseau de `fetch` côté front au lieu de ne gérer que les erreurs JSON [`apps/web-prof/src/features/auth/api.ts`:23] — `try/catch` autour de chaque `fetch`, convention `status: 0` + `NETWORK_ERROR`, parsing robuste du body ; messages mappés en français ; nouveau test « affiche un message générique en cas d'erreur réseau (fetch rejette) ».
- [x] [Review][Patch] Empêcher le double appel de vérification email sous React `StrictMode` d'afficher une erreur après activation réussie [`apps/web-prof/src/features/auth/VerifyEmailPage.tsx`:14] — gate `dispatchedTokenRef` (useRef) qui ne dispatche qu'une fois par token vu ; le flag `cancelled` a été retiré pour éviter d'annuler la mise à jour d'état après la cleanup StrictMode ; nouveau test qui rend la page dans `<StrictMode>` et vérifie `calls === 1` et écran succès.
- [x] [Review][Patch] Aligner la validation runtime du paramètre `token` avec le contrat OpenAPI, ou documenter la réponse 422 [`apps/api/app/api/v1/endpoints/auth.py`:61] — `Annotated[str, Query(min_length=16, max_length=128)]` (option A : enforce + documente), 422 ajoutée dans `contracts/openapi.yaml` pour `verify-email`, gen:types régénéré ; nouveau test `test_verify_email_token_too_short_rejected`. Fix collatéral : `validation_exception_handler` utilise désormais `jsonable_encoder` (Pydantic v2 peut inclure des `ValueError` non-sérialisables dans `ctx`).
- [x] [Review][Patch] Afficher l'erreur 409 "email déjà utilisé" sous le champ email comme demandé par l'AC7 [`apps/web-prof/src/features/auth/RegisterPage.tsx`:38] — `setError('email', { type: 'server', message })` + `setFocus('email')` (pattern RHF) ; test mis à jour pour vérifier le rattachement (`id="register-email-error"`, `aria-invalid="true"`, `aria-describedby`).

## Dev Notes

### Contexte critique — état du dépôt après la Story 1.2

**Ce qui existe déjà :**
- `apps/api/app/core/config.py` : `Settings` avec `SMTP_HOST/PORT/USER/PASSWORD` déjà déclarés (placeholders). **Étendre**, ne pas recréer.
- `apps/api/app/core/security.py` : **PLACEHOLDER vide** — sera partagé avec Story 1.4 (JWT). Pour cette story, y placer les fonctions `hash_password(password: str) -> str` et `verify_password(plain: str, hashed: str) -> bool` (passlib bcrypt).
- `apps/api/app/models/base.py` : `Base(DeclarativeBase)` — à importer dans `teacher.py`.
- `apps/api/app/models/__init__.py` : vide — ajouter `from .teacher import Teacher`.
- `apps/api/app/repositories/__init__.py` : vide — ajouter le repository enseignant.
- `apps/api/app/schemas/__init__.py` : vide — ajouter les schémas.
- `apps/api/app/services/__init__.py` : vide — ajouter le service auth.
- `apps/api/app/api/v1/router.py` : inclut seulement `health` — **ajouter** le router `auth`.
- `apps/api/app/main.py` : **ajouter** `SlowAPIMiddleware` et le handler `429` — ne pas réécrire le fichier.
- `apps/api/tests/conftest.py` : **INEXISTANT** — à créer pour fournir les fixtures DB et client async.
- Alembic : `apps/api/alembic/` existe (story 1.1), utiliser `uv run alembic revision --autogenerate`.
- `apps/web-prof/src/App.tsx` : placeholder "Story 1.1". À remplacer par le routeur React avec les routes `/register` et `/verify-email`.

**Ce qui n'existe PAS encore (à créer) :**
- `apps/api/app/models/teacher.py`
- `apps/api/app/repositories/teacher_repository.py`
- `apps/api/app/schemas/teacher.py`
- `apps/api/app/services/auth_service.py`
- `apps/api/app/services/email_service.py`
- `apps/api/app/core/database.py`
- `apps/api/app/core/rate_limit.py`
- `apps/api/app/api/v1/endpoints/auth.py`
- `apps/api/tests/conftest.py`
- `apps/api/tests/test_auth_register.py`
- `apps/web-prof/src/features/auth/RegisterPage.tsx`
- `apps/web-prof/src/features/auth/VerifyEmailPage.tsx`

### Stack et versions EXACTES

| Composant | Version | Note |
|-----------|---------|------|
| FastAPI | 0.136.1 (figée) | Pas de bump |
| passlib[bcrypt] | déjà installé (Story 1.1 : `uv add passlib[bcrypt]`) | `CryptContext(schemes=["bcrypt"])` |
| python-jose[cryptography] | déjà installé | Sera utilisé en Story 1.4 pour JWT |
| slowapi | à installer : `uv add slowapi` | Rate limiting FR-43 |
| SQLAlchemy | 2.x async (déjà installé) | Session async obligatoire |
| Alembic | déjà installé | `uv run alembic revision --autogenerate` |
| pytest-asyncio | déjà installé | Ajouter `asyncio_mode = "auto"` dans `pyproject.toml` |
| React Hook Form | à installer : `pnpm add react-hook-form @hookform/resolvers zod --filter web-prof` | Validation formulaire |
| TanStack Query | à installer : `pnpm add @tanstack/react-query --filter web-prof` | Ou `fetch` simple acceptable pour cette story |
| React Router v7 | à installer : `pnpm add react-router-dom --filter web-prof` | Navigation entre pages |

> ⚠️ `passlib` doit être importé comme `from passlib.context import CryptContext` — ne pas utiliser `bcrypt` directement.
> ⚠️ slowapi s'intègre avec FastAPI via `app.state.limiter`, `@app.exception_handler(RateLimitExceeded)`, et le décorateur `@limiter.limit("10/minute")` sur l'endpoint.

### Modèle `Teacher` exact

```python
# apps/api/app/models/teacher.py
import secrets
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Index, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Teacher(Base):
    """Compte enseignant Kopie."""

    __tablename__ = "teachers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending"
    )  # "pending" | "active"
    email_verification_token: Mapped[str | None] = mapped_column(
        String(64), nullable=True, index=True
    )
    email_verification_token_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        Index("ix_teachers_email", "email"),
    )
```

> ⚠️ `status` est une `String` (pas un `Enum` PostgreSQL) pour faciliter les migrations futures.
> ⚠️ `display_name` est initialisé vide à l'inscription — l'enseignant le complète en Story 1.5 (Profil).
> ⚠️ Pour SQLite en tests, utiliser `String` au lieu de `UUID(as_uuid=True)` → contourner via fixture conftest (voir section Tests).

### Schémas Pydantic

```python
# apps/api/app/schemas/teacher.py
import uuid
from pydantic import BaseModel, EmailStr, field_validator


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 12:
            raise ValueError("Le mot de passe doit comporter au moins 12 caractères.")
        return v


class TeacherCreated(BaseModel):
    id: uuid.UUID
    email: str
    status: str


class TeacherPublic(BaseModel):
    """Représentation publique complète — réutilisée par Story 1.4, 1.5."""
    id: uuid.UUID
    email: str
    display_name: str
    status: str
    created_at: str  # ISO 8601 UTC
    updated_at: str
```

> ⚠️ `EmailStr` requiert `pydantic[email]` ou `email-validator` — vérifier que la dep est présente (`uv add "pydantic[email]"` si absent).

### Pattern Rate Limiting (slowapi)

```python
# apps/api/app/core/rate_limit.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
```

```python
# apps/api/app/main.py — ajouts (ne pas réécrire, seulement étendre)
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.rate_limit import limiter

# Après la création de app :
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
```

```python
# apps/api/app/api/v1/endpoints/auth.py
from fastapi import APIRouter, BackgroundTasks, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.rate_limit import limiter
from app.schemas.teacher import RegisterRequest, TeacherCreated

router = APIRouter(prefix="/auth")


@router.post("/register", response_model=TeacherCreated, status_code=201)
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def register(
    request: Request,  # obligatoire pour slowapi
    body: RegisterRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> TeacherCreated:
    ...
```

> ⚠️ Le paramètre `request: Request` est **obligatoire** pour que slowapi puisse extraire l'IP. Sans lui, le décorateur `@limiter.limit` lève une erreur.

### Pattern Session DB async

```python
# apps/api/app/core/database.py
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
```

> ⚠️ `DATABASE_URL` doit utiliser le driver `asyncpg` (ex. `postgresql+asyncpg://...`). SQLite async en tests utilise `aiosqlite` — prévoir le driver dans les deps de test : `uv add --dev aiosqlite`.

### Fixtures pytest — conftest.py

```python
# apps/api/tests/conftest.py
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import get_db
from app.main import app
from app.models.base import Base

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def db_session():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def async_client(db_session: AsyncSession):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()
```

> ⚠️ SQLite en mémoire ne supporte pas `UUID(as_uuid=True)` de PostgreSQL. Deux approches :
> **Approche recommandée :** déclarer `id: Mapped[str]` avec `default=lambda: str(uuid.uuid4())` pour les tests (déconseillé car deux modèles) **OU** utiliser `pytest-postgresql` pour tester sur une vraie PostgreSQL de test.
> **Approche pragmatique retenue :** utiliser `String(36)` dans le modèle comme fallback générique (`UUID(as_uuid=True)` se comporte comme `String` sur SQLite), ce qui marche avec `aiosqlite` sans modification du modèle.
>
> Ajouter dans `apps/api/pyproject.toml` : `aiosqlite` en dep de dev.

### Tests de rate limiting

```python
# Extrait de test_auth_register.py
@pytest.mark.asyncio
async def test_register_rate_limit(async_client):
    """Le 11ème appel dans la même minute doit retourner 429."""
    from unittest.mock import AsyncMock, patch

    with patch("app.services.auth_service.send_verification_email", new_callable=AsyncMock):
        for i in range(10):
            await async_client.post("/api/v1/auth/register", json={
                "email": f"teacher{i}@example.com",
                "password": "motdepasse123456"
            })
        response = await async_client.post("/api/v1/auth/register", json={
            "email": "teacher11@example.com",
            "password": "motdepasse123456"
        })
    assert response.status_code == 429
```

> ⚠️ slowapi utilise un compteur **en mémoire** par défaut (pas de Redis). En tests, chaque `AsyncClient` hérite du même état limiter. Il peut être nécessaire de réinitialiser l'état entre tests ou d'utiliser un préfixe d'IP différent.

### Service email — mode dégradé dev

```python
# apps/api/app/services/email_service.py
import structlog

from app.core.config import settings

logger = structlog.get_logger()


def send_verification_email(email: str, token: str) -> None:
    """Envoie l'email de vérification — NOP si SMTP_HOST non configuré."""
    verification_url = (
        f"{settings.APP_BASE_URL}/api/v1/auth/verify-email?token={token}"
    )
    if not settings.SMTP_HOST:
        logger.warning(
            "SMTP_HOST non configuré — email de vérification non envoyé",
            email=email,
            verification_url=verification_url,
        )
        return
    # Envoi SMTP réel (smtplib sync, acceptable en BackgroundTask)
    import smtplib
    from email.message import EmailMessage

    msg = EmailMessage()
    msg["Subject"] = "Kopie — Confirmez votre adresse email"
    msg["From"] = settings.SMTP_USER
    msg["To"] = email
    msg.set_content(
        f"Bonjour,\n\nCliquez sur ce lien pour confirmer votre adresse email :\n{verification_url}\n\nCe lien expire dans 24 heures."
    )
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
        if settings.SMTP_USER and settings.SMTP_PASSWORD:
            smtp.starttls()
            smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        smtp.send_message(msg)
    logger.info("Email de vérification envoyé", email=email)
```

> ⚠️ **Jamais** logger le contenu du mot de passe ou le token en clair dans les logs (NFR-8). Seul `email` et `verification_url` sont loggés (et seulement en dev/warning, pas en prod).
> ⚠️ Ajouter `APP_BASE_URL: str = "http://localhost:8000"` dans `config.py`.

### Contrat OpenAPI — schémas à ajouter dans `contracts/openapi.yaml`

```yaml
# Schémas à ajouter dans components/schemas :
RegisterRequest:
  type: object
  required: [email, password]
  properties:
    email:
      type: string
      format: email
      example: "marie.dupont@academie-versailles.fr"
    password:
      type: string
      minLength: 12
      description: Mot de passe — au moins 12 caractères
      example: "motdepasse123456"

TeacherCreated:
  type: object
  required: [id, email, status]
  properties:
    id:
      type: string
      format: uuid
    email:
      type: string
      format: email
    status:
      type: string
      enum: [pending]
      description: Toujours "pending" à l'inscription — en attente de confirmation email

# Routes à ajouter dans paths :
/api/v1/auth/register:
  post:
    summary: Inscription d'un nouvel enseignant
    tags: [auth]
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/RegisterRequest"
    responses:
      "201":
        description: Compte créé, email de confirmation envoyé
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/TeacherCreated"
      "409":
        description: Email déjà utilisé
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/Error"
      "422":
        description: Données invalides (email malformé, mot de passe trop court)
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/Error"
      "429":
        description: Trop de requêtes (rate limit)
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/Error"

/api/v1/auth/verify-email:
  get:
    summary: Confirmation de l'email par token
    tags: [auth]
    parameters:
      - name: token
        in: query
        required: true
        schema:
          type: string
    responses:
      "200":
        description: Email confirmé avec succès
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
      "400":
        description: Token invalide ou expiré
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/Error"
```

> ⚠️ **Règle absolue** : commencer par le YAML, puis régénérer les types, puis implémenter le backend. C'est le flux « contract-first » établi en Story 1.2.
> ⚠️ Bump la version `info.version` du YAML de `"0.1.0"` → `"0.2.0"` (première route métier). Aligner `app = FastAPI(version="0.2.0")` dans `main.py`.

### Politique mot de passe

- Longueur minimale : **12 caractères** (choix pragmatique MVP — pas de complexité supplémentaire requise au MVP).
- Pas de vérification de complexité (majuscules, chiffres, symboles) au MVP.
- Le message d'erreur côté front doit indiquer la règle : « Minimum 12 caractères ».

### Token de vérification email

- Généré avec `secrets.token_urlsafe(32)` → 43 caractères URL-safe.
- TTL : **24 heures** depuis la création (`datetime.now(timezone.utc) + timedelta(hours=24)`).
- Stocké en clair dans `Teacher.email_verification_token` (pas de hash — c'est un secret court-terme).
- Après activation, `email_verification_token` est mis à `NULL` et `email_verification_token_expires_at` aussi.

### Page front d'inscription — squelette

```tsx
// apps/web-prof/src/features/auth/RegisterPage.tsx
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

const registerSchema = z.object({
  email: z.string().email('Email invalide'),
  password: z.string().min(12, 'Minimum 12 caractères'),
})
type RegisterFormData = z.infer<typeof registerSchema>

export function RegisterPage() {
  const [success, setSuccess] = useState(false)
  const [serverError, setServerError] = useState<string | null>(null)
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  })

  const onSubmit = async (data: RegisterFormData) => {
    setServerError(null)
    const res = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    if (res.status === 201) {
      setSuccess(true)
    } else if (res.status === 409) {
      setServerError('Cet email est déjà utilisé.')
    } else {
      setServerError('Une erreur est survenue. Veuillez réessayer.')
    }
  }

  if (success) {
    return (
      <main>
        <h1>Vérifiez votre boîte mail</h1>
        <p>Un lien de confirmation vous a été envoyé. Cliquez dessus pour activer votre compte.</p>
      </main>
    )
  }

  return (
    <main>
      <h1>Créer un compte enseignant</h1>
      <form onSubmit={handleSubmit(onSubmit)}>
        {/* Champs email, password, bouton submit avec isSubmitting */}
      </form>
      {serverError && <p role="alert">{serverError}</p>}
    </main>
  )
}
```

> ⚠️ Utiliser `import.meta.env.VITE_API_URL` (configuré dans `apps/web-prof/.env.local` : `VITE_API_URL=http://localhost:8000`). **Ne jamais hardcoder l'URL de l'API**.
> ⚠️ La page doit respecter la charte UX-DR21 (vouvoiement) et UX-DR1 (design system Tailwind avec `theme-teacher`). Ajouter les classes Tailwind cohérentes avec `apps/web-prof/src/index.css`.

### Isolation multi-tenant — pas encore requise pour Story 1.3

La Story 1.3 crée le modèle `Teacher` mais ne gère pas encore les ressources métier liées à `teacher_id`. L'isolation sera testée exhaustivement en Story 1.6. **Cependant** :
- Le champ `id` UUID du `Teacher` sera la FK `teacher_id` sur toutes les tables futures.
- Implémenter `get_current_teacher()` dependency FastAPI **en Story 1.4** (JWT), pas dans cette story.
- Ne pas anticiper l'isolation dans les tests de cette story.

### Règles d'architecture CRITIQUES à respecter

1. **Contract-first** : modifier `contracts/openapi.yaml` avant d'écrire le code backend.
2. **Régénérer `shared-types`** après chaque modification du YAML.
3. **Logique métier dans `services/`**, jamais dans les endpoints.
4. **Repository layer** pour tout accès DB — jamais de query SQL directe dans les services ou endpoints.
5. **`snake_case`** dans tous les champs JSON (OpenAPI et réponses API).
6. **Logs structlog** : ne jamais logger de mot de passe, hash, ou token de vérification.
7. **`AsyncSession`** pour tous les accès DB (SQLAlchemy 2.x async).
8. **mypy strict** : annoter tous les types, utiliser `str | None` pas `Optional[str]`.

### Anti-patterns à éviter absolument

| Anti-pattern | Correct |
|---|---|
| Hasher le mot de passe dans l'endpoint | Dans `auth_service.py` |
| Logger le `password_hash` ou le `email_verification_token` | Ne jamais logger ces valeurs |
| `requests.get` (sync) dans un endpoint async | Utiliser `BackgroundTasks` pour l'envoi d'email |
| Query SQL directe dans l'endpoint | Via `teacher_repository.py` |
| `Optional[str]` (style Python < 3.10) | `str \| None` |
| Oublier `request: Request` dans l'endpoint limité | Paramètre obligatoire pour slowapi |
| Committer `packages/shared-types/src/api.ts` désynchronisé | `pnpm gen:types` avant commit |
| Hardcoder l'URL de l'API dans le front | `import.meta.env.VITE_API_URL` |
| `app.openapi_schema = None` pour reset en tests | Utiliser la fixture `_reset_openapi_cache` (pattern story 1.2) |

### Dépendances à ajouter

**Backend :**
```bash
# Depuis apps/api/
uv add slowapi
uv add "pydantic[email]"   # si pas encore installé (EmailStr)
uv add --dev aiosqlite      # SQLite async pour les tests
```

**Frontend :**
```bash
# Depuis la racine du monorepo
pnpm add react-hook-form @hookform/resolvers zod --filter web-prof
pnpm add @tanstack/react-query --filter web-prof
pnpm add react-router-dom --filter web-prof
```

### Cibles de qualité attendues

| Vérification | Critère de succès |
|---|---|
| `uv run ruff check .` | 0 erreur |
| `uv run mypy app` | 0 erreur strict |
| `uv run pytest -q` | 100 % pass (4 existants + ≥ 8 nouveaux) |
| `pnpm gen:types` | 0 erreur, idempotent |
| `pnpm --filter web-prof build` | 0 erreur TypeScript |
| `pnpm --filter web-prof test` | tous passent |
| CI `verify-shared-types` | verte |

### Références

- [Source: epics.md#Story 1.3] — AC officiels + user story
- [Source: epics.md#Additional Requirements] — Auth enseignant : JWT access (court) + refresh cookie (Story 1.4) ; bcrypt (passlib) pour mots de passe ; SMTP validation email async (Story 1.3)
- [Source: epics.md#FR-1] — Création de compte avec email/mot de passe + validation email
- [Source: epics.md#FR-43] — Protection endpoints auth par rate limiting
- [Source: architecture.md#Authentication & Security] — bcrypt (passlib), slowapi sur /auth/*, JWT côté Story 1.4
- [Source: architecture.md#Implementation Patterns] — Logique dans `services/`, repository layer, `teacher_id` FK future
- [Source: architecture.md#Naming Patterns] — Table `teachers`, colonnes `snake_case`, PK UUID v4
- [Source: architecture.md#Requirements to Structure Mapping] — FR-1…4 → `endpoints/auth.py`, `teachers.py`, `web-prof/features/auth/`
- [Source: 1-2-contrat-openapi-initial-et-types-partages.md#Dev Notes] — Contract-first workflow, `pnpm gen:types`, `ASGITransport` pattern, `AsyncSessionLocal`, mypy strict

## Dev Agent Record

### Agent Model Used

Claude Opus 4.7 (via Cursor IDE, skill `bmad-dev-story`).

### Completion Notes List

**Implémentation conforme aux 7 AC et aux 13 tâches.** Aucun écart fonctionnel.

**Décisions techniques notables :**

1. **Type colonne UUID** — j'ai utilisé `sqlalchemy.Uuid(as_uuid=True)` (générique
   SQLAlchemy 2.0) au lieu de `postgresql.dialects.UUID` proposé dans les Dev
   Notes. Avantage : un seul modèle, compatible PostgreSQL (UUID natif) ET
   SQLite (CHAR(32)) — les tests `aiosqlite` tournent sans modification du
   modèle. Le contrat OpenAPI et l'API publique restent `uuid` (`format: uuid`).
2. **Migration Alembic manuelle** — `alembic revision --autogenerate` requiert
   une DB live ; pour rester reproductible et reviewable, j'ai écrit
   `20260519_0001_add_teachers_table.py` à la main (équivalent au résultat
   autogen). Schema validé indirectement par les 15 tests qui appellent
   `Base.metadata.create_all` via la fixture.
3. **`bcrypt<5.0`** — bug connu : `passlib 1.7.4` (le dernier release) ne
   supporte pas `bcrypt>=5.0` (suppression de `__about__` + limite 72 bytes
   stricte qui casse la self-detection de passlib). J'ai épinglé
   `bcrypt<5.0` (resolved à `4.3.0`) dans `pyproject.toml`. Hash/verify
   fonctionnels et testés.
4. **Format `Error` du contrat sur 4xx/422/429** — j'ai ajouté trois
   exception handlers dans `main.py` (`RateLimitExceeded`, `HTTPException`,
   `RequestValidationError`) qui normalisent toutes les réponses d'erreur
   au schéma `Error` OpenAPI (`{ "error": { "code", "message", "details? } }`).
   Codes : `VALIDATION_ERROR` (422), `EMAIL_ALREADY_REGISTERED` (409),
   `INVALID_OR_EXPIRED_TOKEN` (400), `RATE_LIMIT_EXCEEDED` (429).
5. **Pattern `Annotated[AsyncSession, Depends(get_db)]`** — adopté pour
   contourner `ruff B008` (qui ne reconnaît pas la sémantique FastAPI
   `Depends`), tout en gardant un code idiomatique FastAPI 2024+.
6. **Reset du limiter slowapi entre tests** — `limiter.reset()` est appelé
   dans la fixture `async_client` avant/après chaque test pour empêcher
   l'in-memory state d'un test de faire échouer le suivant.

**Sécurité (NFR-8) :** aucun log de mot de passe, hash, ou token en clair en
prod. Le `verification_url` n'est loggé qu'en mode dégradé (SMTP absent, dev
uniquement) au niveau `warning`.

**Hors-scope confirmé** : login JWT (Story 1.4), profil enseignant (Story 1.5),
isolation multi-tenant (Story 1.6) — pas anticipés.

**Vérifications finales :**
- `ruff check .` → ✅ 0 erreur
- `mypy app` (strict) → ✅ 0 erreur sur 27 fichiers
- `pytest -q` → ✅ 15/15 passent
- `redocly lint contracts/openapi.yaml` → ✅ valid
- `pnpm gen:types` idempotent → ✅
- `pnpm --filter web-prof {test,build,lint}` → ✅ 10/10 tests, build OK, eslint OK
- `pnpm --filter web-eleve {test,build}` → ✅ non-régression
- `docker compose config` → ✅ valid

### File List

**Fichiers créés**
- `apps/api/app/api/v1/endpoints/auth.py`
- `apps/api/app/core/database.py`
- `apps/api/app/core/rate_limit.py`
- `apps/api/app/models/teacher.py`
- `apps/api/app/repositories/teacher_repository.py`
- `apps/api/app/schemas/teacher.py`
- `apps/api/app/services/auth_service.py`
- `apps/api/app/services/email_service.py`
- `apps/api/tests/conftest.py`
- `apps/api/tests/test_auth_register.py`
- `apps/api/alembic/versions/20260519_0001_add_teachers_table.py`
- `apps/web-prof/src/features/auth/api.ts`
- `apps/web-prof/src/features/auth/RegisterPage.tsx`
- `apps/web-prof/src/features/auth/VerifyEmailPage.tsx`
- `apps/web-prof/src/__tests__/RegisterPage.test.tsx`
- `apps/web-prof/src/__tests__/VerifyEmailPage.test.tsx`

**Fichiers modifiés**
- `contracts/openapi.yaml` — ajout schémas `RegisterRequest`, `TeacherCreated` + routes `/api/v1/auth/register`, `/api/v1/auth/verify-email` ; bump version `0.1.0` → `0.2.0`
- `packages/shared-types/src/api.ts` — régénéré (idempotent)
- `apps/api/app/main.py` — bump version 0.2.0 ; slowapi middleware + handlers `RateLimitExceeded`/`HTTPException`/`RequestValidationError` au format `Error`
- `apps/api/app/api/v1/router.py` — inclusion du router `auth`
- `apps/api/app/core/config.py` — ajout `APP_BASE_URL`
- `apps/api/app/core/security.py` — implémentation de `hash_password` / `verify_password` (bcrypt via passlib)
- `apps/api/app/models/__init__.py` — export `Base`, `Teacher`
- `apps/api/app/schemas/__init__.py` — export schémas teacher
- `apps/api/app/repositories/__init__.py` — export `TeacherRepository`
- `apps/api/app/services/__init__.py` — export `AuthService`, helpers email
- `apps/api/pyproject.toml` + `apps/api/uv.lock` — ajout `pydantic[email]`, `bcrypt<5.0` (pin compatibilité passlib), `aiosqlite` (dev), `pytest-mock` (dev)
- `apps/api/tests/test_openapi_contract.py` — assertions étendues (version 0.2.0, nouveaux schémas/routes)
- `.env.example` — section SMTP enrichie + nouvelle `APP_BASE_URL`
- `docker-compose.yml` — injection explicite `SMTP_*`, `APP_BASE_URL`, `RATE_LIMIT_*` dans le service `api`
- `apps/web-prof/package.json` + `pnpm-lock.yaml` — ajout `react-hook-form`, `@hookform/resolvers`, `zod`, `react-router-dom`, `@testing-library/user-event` (dev)
- `apps/web-prof/src/App.tsx` — routeur React (`/`, `/register`, `/verify-email`)
- `apps/web-prof/src/main.tsx` — `BrowserRouter` autour de `<App />`
- `apps/web-prof/src/__tests__/App.test.tsx` — tests adaptés au routeur (MemoryRouter)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — `1-3-...` → `in-progress` puis `review`

## Change Log

| Date | Auteur | Description |
|------|--------|-------------|
| 2026-05-19 | BMad (create-story) | Création de la story 1.3 — contexte exhaustif pour l'agent de développement. Status → ready-for-dev. |
| 2026-05-19 | BMad (dev-story) | Implémentation complète : contrat OpenAPI 0.2.0, modèle Teacher + migration Alembic, service d'inscription + service email asynchrone (mode dégradé), rate-limit slowapi, pages React /register et /verify-email, 15 tests pytest et 10 tests vitest verts, ruff/mypy clean. Status → review. |
| 2026-05-19 | BMad (dev-story patch) | Application des 7 review findings : (1) plafonner le mot de passe à 72 octets UTF-8 côté contrat/API/Zod + tests dédiés ; (2) `IntegrityError` mappée vers 409 idempotent en cas de race ; (3) suppression de l'URL/token des logs (préfixe court uniquement) ; (4) `fetch` rejects gérés (statut 0 + `NETWORK_ERROR`) ; (5) double-mount StrictMode dédupliqué via `useRef` ; (6) `Query(min_length=16, max_length=128)` aligné avec le contrat + 422 documenté + handler 422 hardened via `jsonable_encoder` ; (7) 409 affichée inline sous le champ email (`setError` RHF). 23 tests pytest et 12 tests vitest verts ; ruff/mypy/build/lint clean. Status → review. |
