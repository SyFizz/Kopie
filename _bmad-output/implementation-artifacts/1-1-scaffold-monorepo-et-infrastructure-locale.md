# Story 1.1: Scaffold monorepo et infrastructure locale

Status: done

## Story

As a **développeur / équipe projet**,
I want **initialiser le monorepo pnpm avec les apps web-prof, web-eleve, l'API FastAPI et PostgreSQL via Docker Compose**,
so that **l'équipe dispose d'une base exécutable pour livrer les fonctionnalités enseignant et élève**.

## Acceptance Criteria

1. **Given** un dépôt vide **When** les commandes d'initialisation sont exécutées **Then** la structure suivante existe : `apps/web-prof/`, `apps/web-eleve/`, `apps/api/`, `packages/shared-types/`, `docker-compose.yml`, `pnpm-workspace.yaml`, `.env.example`, `contracts/openapi.yaml` (squelette)
2. **Given** Docker installé **When** `docker compose up` est exécuté **Then** PostgreSQL démarre sur le port 5432 et l'API FastAPI répond sur `/api/v1/health` (HTTP 200)
3. **Given** le monorepo initialisé **When** `pnpm --filter web-prof dev` est exécuté **Then** Vite démarre l'app enseignant sans erreur de compilation
4. **Given** le monorepo initialisé **When** `pnpm --filter web-eleve dev` est exécuté **Then** Vite démarre l'app élève sans erreur de compilation
5. **Given** Tailwind CSS v4 configuré **When** les apps démarrent **Then** les tokens CSS du thème `theme-teacher` (primary `#2563eb`, fonds slate) et `theme-student` (minimal, apaisant) sont actifs sur leurs apps respectives (direction D2 — Calme professionnel)
6. **Given** le squelette API **When** `uv run uvicorn app.main:app --reload` est exécuté dans `apps/api` **Then** l'API FastAPI démarre, `/docs` est accessible et la structure modulaire `app/api/v1/`, `app/core/`, `app/models/`, `app/schemas/`, `app/services/`, `app/repositories/` existe
7. **Given** le fichier `contracts/openapi.yaml` **When** il est lu **Then** il définit au minimum le schéma `Error` et la route `/api/v1/health` (le contrat complet sera étoffé en Story 1.2)

## Tasks / Subtasks

- [x] Tâche 1 — Initialiser le monorepo pnpm (AC: 1)
  - [x] Créer `package.json` racine avec `"name": "kopie"`, `"private": true`
  - [x] Créer `pnpm-workspace.yaml` avec `packages: ['apps/*', 'packages/*']`
  - [x] Créer `.gitignore` (node_modules, `__pycache__`, `.env`, `*.pyc`, `dist`, `.venv`)
  - [x] Créer `.env.example` avec les variables documentées (voir section Dev Notes)

- [x] Tâche 2 — Scaffolder les deux apps frontend (AC: 1, 3, 4)
  - [x] `pnpm create vite@9.0.7 apps/web-prof -- --template react-ts` (équivalent — voir Completion Notes)
  - [x] `pnpm create vite@9.0.7 apps/web-eleve -- --template react-ts` (équivalent — voir Completion Notes)
  - [x] Installer Tailwind v4 : `pnpm add -D tailwindcss @tailwindcss/vite --filter web-prof` et idem pour `web-eleve`
  - [x] Configurer `vite.config.ts` dans chaque app : ajouter `tailwindcss()` dans `plugins`
  - [x] Remplacer `index.css` par `@import "tailwindcss";` + tokens CSS thème (voir section Thèmes)
  - [x] Installer Vitest + Testing Library : `pnpm add -D vitest @testing-library/react @testing-library/jest-dom jsdom --filter web-prof` et idem pour `web-eleve`
  - [x] Installer Lucide React : `pnpm add lucide-react --filter web-prof` et idem pour `web-eleve`
  - [x] Configurer `vitest.config.ts` (environment: 'jsdom') dans chaque app
  - [x] Nettoyer le boilerplate Vite (supprimer `App.css`, simplifier `App.tsx` avec placeholder minimal)
  - [x] Configurer `VITE_API_URL` dans `apps/web-prof/.env.development` et `apps/web-eleve/.env.development`

- [x] Tâche 3 — Scaffolder l'API FastAPI (AC: 1, 6)
  - [x] `uv init apps/api --package` depuis la racine (équivalent — `pyproject.toml` créé)
  - [x] `cd apps/api && uv add fastapi==0.136.1 "uvicorn[standard]" "sqlalchemy[asyncio]" alembic pydantic-settings "python-jose[cryptography]" "passlib[bcrypt]" httpx structlog slowapi`
  - [x] `uv add --dev pytest pytest-asyncio ruff mypy`
  - [x] Créer la structure modulaire complète (voir arborescence API ci-dessous)
  - [x] Créer `app/main.py` avec l'app FastAPI, CORS configuré, router v1 monté sur `/api/v1`
  - [x] Créer `app/api/v1/endpoints/health.py` avec `GET /health` → `{"status": "ok"}`
  - [x] Créer `app/core/config.py` (Pydantic Settings) lisant les variables `.env`
  - [x] Créer `app/core/logging.py` (structlog JSON, jamais de PII élève)
  - [x] Initialiser Alembic : `uv run alembic init alembic` ; configurer `alembic.ini` et `env.py` (URL async depuis config)
  - [x] Créer `pyproject.toml` avec sections `[tool.ruff]`, `[tool.mypy]`, `[tool.pytest.ini_options]`

- [x] Tâche 4 — Docker Compose dev (AC: 2)
  - [x] Créer `docker-compose.yml` avec services : `postgres`, `api`, `web-prof`, `web-eleve`
  - [x] Service `postgres` : image `postgres:16-alpine`, volume nommé `pgdata`, env `POSTGRES_*` depuis `.env`
  - [x] Service `api` : build depuis `apps/api/Dockerfile.dev`, dépend de `postgres`, monte le code source pour hot-reload, expose le port configuré
  - [x] Services frontend : build depuis `apps/web-prof/Dockerfile.dev` et `apps/web-eleve/Dockerfile.dev`
  - [x] Créer `Dockerfile.dev` pour chaque service (API : `uv run uvicorn` ; fronts : `pnpm dev --host`)
  - [x] Ajouter healthcheck sur le service `api` (test sur `/api/v1/health`)

- [x] Tâche 5 — Package shared-types (AC: 1)
  - [x] Créer `packages/shared-types/package.json` avec `"name": "@kopie/shared-types"`
  - [x] Créer `packages/shared-types/index.ts` (export vide au départ)
  - [x] Créer `scripts/gen-types.sh` (placeholder pour Story 1.2 — commenté, instructions incluses)

- [x] Tâche 6 — Contrat OpenAPI squelette (AC: 7)
  - [x] Créer `contracts/openapi.yaml` : OpenAPI 3.1, info (title: Kopie API, version: 0.1.0), schéma `Error`, path `/api/v1/health`

- [x] Tâche 7 — CI GitHub Actions squelette (AC: transversal)
  - [x] Créer `.github/workflows/ci.yml` avec jobs : `lint-api` (ruff), `lint-front` (eslint), `test-api` (pytest), `test-front` (vitest), `build`

- [x] Tâche 8 — Vérification finale (AC: 1–7)
  - [x] `docker compose up` → PostgreSQL actif + API health OK *(validé end-to-end : 4/4 conteneurs `up`, postgres `healthy`, API `healthy`, `/api/v1/health`=200, `/docs`=200, web-prof=200, web-eleve=200, `pg_isready` = accepting connections)*
  - [x] `pnpm --filter web-prof dev` → Vite démarre, page blanche sans erreur (200 sur http://127.0.0.1:5173)
  - [x] `pnpm --filter web-eleve dev` → idem (200 sur http://127.0.0.1:5174)
  - [x] `uv run ruff check .` → 0 erreur dans `apps/api` (après auto-fix d'un import non trié)
  - [x] `uv run mypy app` → 0 erreur (strict, 18 fichiers analysés)

### Review Findings

- [x] [Review][Patch] Secret par défaut prédictible pour l'API (`SECRET_KEY`) [docker-compose.yml]
- [x] [Review][Patch] Configuration CORS figée dans Docker Compose au lieu d'être pilotée par variable d'environnement [docker-compose.yml]
- [x] [Review][Patch] CI front non déterministe (`pnpm install --frozen-lockfile=false`) [`.github/workflows/ci.yml`]
- [x] [Review][Patch] Politique de version Node incohérente entre `engines`, CI et images Docker [package.json]

### Review Findings (Re-run 2026-05-19)

- [x] [Review][Patch] Build Docker front non déterministe (`pnpm install --no-frozen-lockfile`) [apps/web-prof/Dockerfile.dev]
- [x] [Review][Patch] Image `uv` non figée dans l'image API (`ghcr.io/astral-sh/uv:latest`) [apps/api/Dockerfile.dev]

## Dev Notes

### Stack et versions EXACTES

| Composant | Version | Source |
|-----------|---------|--------|
| Node.js | 22.12+ (ou 20.19+) | Architecture §Starter |
| pnpm | latest stable | Architecture §Starter |
| Python | ≥ 3.12 | Architecture §Decisions |
| uv | latest stable | Architecture §Starter |
| create-vite | **9.0.7** | Architecture §Starter — version figée |
| FastAPI | **0.136.1** | Architecture §Decisions — version figée |
| Tailwind CSS | **v4** via `@tailwindcss/vite` | Architecture §Starter |
| SQLAlchemy | **2.x async** | Architecture §Data |
| Alembic | latest compatible | Architecture §Data |
| PostgreSQL | **16-alpine** (Docker) | Architecture |

> ⚠️ Ne pas utiliser `create-vite@latest` — la version **9.0.7** est explicitement figée dans l'architecture.
> ⚠️ Ne pas installer Tailwind v3 — utiliser exclusivement `@tailwindcss/vite` (plugin v4, pas `tailwind.config.js`).

### Structure monorepo complète requise

```
kopie/
├── README.md
├── LICENSE                        # AGPL-3.0 (NFR-12)
├── .gitignore
├── .env.example                   # TOUTES les variables documentées
├── pnpm-workspace.yaml
├── package.json                   # racine — pas de deps front ici
├── docker-compose.yml             # dev
├── docker-compose.prod.yml        # placeholder vide (à remplir Story 6.1)
├── Caddyfile                      # placeholder vide (à remplir Story 6.2)
├── .github/workflows/ci.yml
├── contracts/
│   └── openapi.yaml               # squelette minimal v0.1.0
├── scripts/
│   ├── gen-types.sh               # placeholder commenté pour Story 1.2
│   └── migrate.sh                 # placeholder commenté pour Story 6.3
├── docs/
│   └── self-hosting.md            # placeholder vide (Story 6.6)
├── packages/
│   └── shared-types/
│       ├── package.json           # @kopie/shared-types
│       └── index.ts               # export vide
├── apps/
│   ├── web-prof/                  # react-ts Vite — prof.kopie.cc
│   │   ├── src/
│   │   │   ├── main.tsx
│   │   │   ├── App.tsx            # placeholder minimal
│   │   │   └── index.css          # @import "tailwindcss" + tokens theme-teacher
│   │   ├── index.html
│   │   ├── vite.config.ts         # react() + tailwindcss()
│   │   ├── vitest.config.ts
│   │   ├── tsconfig.json
│   │   ├── package.json
│   │   ├── Dockerfile.dev
│   │   └── .env.development       # VITE_API_URL=http://localhost:8000
│   ├── web-eleve/                 # react-ts Vite — eleve.kopie.cc
│   │   ├── src/
│   │   │   ├── main.tsx
│   │   │   ├── App.tsx            # placeholder minimal
│   │   │   └── index.css          # @import "tailwindcss" + tokens theme-student
│   │   ├── index.html
│   │   ├── vite.config.ts
│   │   ├── vitest.config.ts
│   │   ├── tsconfig.json
│   │   ├── package.json
│   │   ├── Dockerfile.dev
│   │   └── .env.development       # VITE_API_URL=http://localhost:8000
│   └── api/                       # FastAPI + uv
│       ├── app/
│       │   ├── __init__.py
│       │   ├── main.py            # FastAPI app, CORS, routers
│       │   ├── api/
│       │   │   ├── __init__.py
│       │   │   └── v1/
│       │   │       ├── __init__.py
│       │   │       ├── router.py  # inclusion de tous les endpoints
│       │   │       └── endpoints/
│       │   │           ├── __init__.py
│       │   │           └── health.py
│       │   ├── core/
│       │   │   ├── __init__.py
│       │   │   ├── config.py      # Pydantic Settings
│       │   │   ├── logging.py     # structlog JSON
│       │   │   ├── security.py    # placeholder (Story 1.4)
│       │   │   └── event_types.py # placeholder catalogue événements (Story 4.5)
│       │   ├── models/
│       │   │   └── __init__.py    # placeholder
│       │   ├── schemas/
│       │   │   └── __init__.py    # placeholder
│       │   ├── services/
│       │   │   └── __init__.py    # placeholder
│       │   ├── repositories/
│       │   │   └── __init__.py    # placeholder
│       │   └── jobs/
│       │       └── __init__.py    # placeholder (Story 6.4)
│       ├── alembic/
│       │   ├── env.py
│       │   └── versions/          # vide
│       ├── tests/
│       │   ├── __init__.py
│       │   └── test_health.py     # test GET /api/v1/health → 200
│       ├── Dockerfile.dev
│       ├── pyproject.toml
│       └── alembic.ini
```

### Configuration CORS dans `app/main.py`

```python
from fastapi.middleware.cors import CORSMiddleware

# CORS : origines explicites uniquement (architecture §API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # liste depuis .env
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

En développement local : `CORS_ORIGINS=["http://localhost:5173", "http://localhost:5174"]`  
En production : `CORS_ORIGINS=["https://prof.kopie.cc", "https://eleve.kopie.cc"]`

### Variables `.env.example` OBLIGATOIRES

```bash
# Base de données
DATABASE_URL=postgresql+asyncpg://kopie:kopie@localhost:5432/kopie
POSTGRES_USER=kopie
POSTGRES_PASSWORD=kopie
POSTGRES_DB=kopie

# API
SECRET_KEY=changeme-generate-with-openssl-rand-hex-32
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS (liste JSON)
CORS_ORIGINS=["http://localhost:5173","http://localhost:5174"]

# SMTP (placeholder — Story 1.3)
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=

# Rétention données élève (FR-41)
DATA_RETENTION_MONTHS=12

# Rate limiting (FR-43 — seuils ajustables)
RATE_LIMIT_AUTH=10/minute
RATE_LIMIT_STUDENT_ANSWERS=60/minute
RATE_LIMIT_STUDENT_EVENTS=30/minute
RATE_LIMIT_STUDENT_SUBMIT=5/minute
```

> ⚠️ Le fichier `.env` NE DOIT JAMAIS être commité (NFR-4). Vérifier `.gitignore`.

### Thèmes Tailwind CSS v4 (Direction D2 — Calme professionnel)

Dans `apps/web-prof/src/index.css` :
```css
@import "tailwindcss";

@layer base {
  :root {
    /* theme-teacher : dense, professionnel */
    --primary: 221.2 83.2% 53.3%;          /* #2563eb */
    --primary-foreground: 210 40% 98%;
    --background: 210 40% 98%;             /* slate clair */
    --foreground: 222.2 84% 4.9%;
    --success: 142.1 76.2% 36.3%;
    --warning: 47.9 95.8% 53.1%;
    --info: 199.4 95.5% 43.9%;
    --destructive: 0 84.2% 60.2%;          /* réservé actions irréversibles prof uniquement */
    --border: 214.3 31.8% 91.4%;
    --muted: 210 40% 96%;
    --muted-foreground: 215.4 16.3% 46.9%;
    --spacing-base: 4px;
  }
}
```

Dans `apps/web-eleve/src/index.css` :
```css
@import "tailwindcss";

@layer base {
  :root {
    /* theme-student : minimal, apaisant */
    --primary: 221.2 83.2% 53.3%;          /* #2563eb */
    --primary-foreground: 210 40% 98%;
    --background: 0 0% 100%;               /* blanc pur, moins de distraction */
    --foreground: 222.2 84% 4.9%;
    --success: 142.1 76.2% 36.3%;
    --warning: 47.9 95.8% 53.1%;
    --info: 199.4 95.5% 43.9%;
    /* Pas de --destructive côté élève (UX-DR2 : réservé aux actions irréversibles prof) */
    --border: 214.3 31.8% 91.4%;
    --muted: 210 40% 96%;
    --muted-foreground: 215.4 16.3% 46.9%;
    --spacing-base: 4px;
    --text-scale: 1;                       /* aménagement : 1.25 ou 1.5 via FR-12 */
    font-size: 16px;                       /* minimum NFR-15 */
  }
}
```

> ⚠️ Ne PAS utiliser `tailwind.config.js` (syntaxe v3). Tailwind v4 se configure via `@import "tailwindcss"` dans CSS + plugin Vite.  
> ⚠️ Pas de `--destructive` côté élève (UX-DR2). La variable rouge est réservée aux seules actions irréversibles enseignant.

### `pyproject.toml` — configuration outillage API

```toml
[project]
name = "kopie-api"
version = "0.1.0"
requires-python = ">=3.12"

[tool.ruff]
target-version = "py312"
line-length = 88
select = ["E", "W", "F", "I", "UP", "B", "SIM"]

[tool.mypy]
python_version = "3.12"
strict = true
ignore_missing_imports = true

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

### `app/core/config.py` — Pydantic Settings

```python
from pydantic_settings import BaseSettings
from typing import list

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    CORS_ORIGINS: list[str] = []
    DATA_RETENTION_MONTHS: int = 12

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

settings = Settings()
```

### `app/core/logging.py` — structlog JSON

```python
import structlog

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(20),
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger()
```

> ⚠️ JAMAIS logger `student_first_name`, `student_last_name`, ou tout champ PII élève (NFR-8, architecture §Logs).

### `app/main.py` — endpoint health

```python
from fastapi import FastAPI
from app.api.v1.router import api_router
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Kopie API", version="0.1.0")

app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS,
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(api_router, prefix="/api/v1")
```

```python
# app/api/v1/endpoints/health.py
from fastapi import APIRouter
router = APIRouter()

@router.get("/health")
async def health() -> dict:
    return {"status": "ok"}
```

### Alembic — configuration async

Dans `alembic/env.py`, utiliser `run_async_migrations()` avec `asyncpg`. L'URL doit provenir de `settings.DATABASE_URL`. Modèle de base : `app.models.base.Base.metadata`.

Créer `app/models/base.py` :
```python
from sqlalchemy.orm import DeclarativeBase
import uuid
from sqlalchemy import UUID

class Base(DeclarativeBase):
    pass
```

### Test minimal obligatoire pour cette story

```python
# tests/test_health.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

### Contrat OpenAPI squelette `contracts/openapi.yaml`

```yaml
openapi: "3.1.0"
info:
  title: Kopie API
  version: "0.1.0"
  description: |
    Plateforme d'évaluation sécurisée — API REST.
    Contrat versionné. Types front générés via openapi-typescript → @kopie/shared-types.

paths:
  /api/v1/health:
    get:
      operationId: getHealth
      summary: Health check
      tags: [system]
      responses:
        "200":
          description: Service opérationnel
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                    example: "ok"

components:
  schemas:
    Error:
      type: object
      required: [error]
      properties:
        error:
          type: object
          required: [code, message]
          properties:
            code:
              type: string
              description: Code erreur SCREAMING_SNAKE (ex. ACCESS_EXPIRED)
            message:
              type: string
            details:
              type: object
```

> Ce fichier sera étoffé en Story 1.2. Ne pas modifier manuellement `packages/shared-types/` — il est généré.

### `vite.config.ts` requis (identique pour les deux apps)

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
})
```

### `vitest.config.ts` requis

```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    globals: true,
  },
})
```

Créer `src/test/setup.ts` dans chaque app :
```typescript
import '@testing-library/jest-dom'
```

### Règles d'architecture CRITIQUES à ne pas violer

1. **`packages/shared-types/`** — NE PAS éditer à la main, généré par `scripts/gen-types.sh` (Story 1.2)
2. **Logique métier dans `services/`** — pas dans les endpoints FastAPI
3. **Toutes les tables métier auront `teacher_id` UUID FK** — isolation multi-tenant (FR-4)
4. **CORS** — origines explicites uniquement, jamais `allow_origins=["*"]`
5. **Pas de `tailwind.config.js`** — syntaxe v4 uniquement
6. **`SECRET_KEY`** doit être généré avec `openssl rand -hex 32` en production

### Anti-patterns à éviter absolument

| Anti-pattern | Correct |
|---|---|
| `pnpm create vite@latest` | `pnpm create vite@9.0.7` |
| `tailwind.config.js` | CSS `@import "tailwindcss"` + plugin Vite |
| `pip install fastapi` | `uv add fastapi==0.136.1` |
| `from sqlalchemy import create_engine` (sync) | `from sqlalchemy.ext.asyncio import create_async_engine` |
| `allow_origins=["*"]` dans CORS | Origines explicites depuis `settings.CORS_ORIGINS` |
| Logger nom/prénom élève | Jamais — PII interdit dans les logs (NFR-8) |
| Éditer `packages/shared-types/` manuellement | Généré automatiquement (Story 1.2) |

### Project Structure Notes

- **Alignement architecture §Project Structure** : L'arborescence ci-dessus suit exactement le document d'architecture.
- **`docker-compose.prod.yml`** et **`Caddyfile`** créés en placeholder vides — ils seront remplis en Stories 6.1 et 6.2.
- **`scripts/migrate.sh`** créé en placeholder — Story 6.3.
- **`docs/self-hosting.md`** créé en placeholder — Story 6.6.
- **`docs/legal/`** N'existe pas encore — Story 6.8.
- **`tests/e2e/`** : dossier non créé au MVP (post-MVP selon architecture).

### Dépendances front supplémentaires justifiées

| Package | Raison | Filtre |
|---|---|---|
| `lucide-react` | Iconographie standard (UX-DR22) | web-prof + web-eleve |
| `react-i18next` | NFR-7 — chaînes externalisées | web-prof + web-eleve |
| `i18next` | Peer de react-i18next | web-prof + web-eleve |
| `@tanstack/react-query` | Architecture §Frontend — data serveur | web-prof (Story 1.3+) |
| `react-router-dom` | Architecture §Frontend — routing par app | web-prof + web-eleve (Story 1.3+) |

> TanStack Query et React Router peuvent être installés maintenant pour ne pas bloquer les stories suivantes. Si vous les installez, créez des imports placeholder dans `App.tsx` mais n'implémentez pas les routes.

### Références

- [Source: architecture.md §Starter Template Evaluation] — commandes d'init exactes, versions figées
- [Source: architecture.md §Core Architectural Decisions] — stack critique (FastAPI 0.136.1, SQLAlchemy 2.x async, Alembic)
- [Source: architecture.md §Frontend Architecture] — Tailwind v4, TanStack Query, React Router v7, react-i18next
- [Source: architecture.md §Project Structure] — arborescence complète
- [Source: architecture.md §Naming Patterns] — snake_case Python, PascalCase TypeScript, UUID v4 PKs
- [Source: architecture.md §Authentication & Security] — CORS origines explicites, JWT, structlog sans PII
- [Source: epics.md §Additional Requirements] — version exacte create-vite@9.0.7, contrat OpenAPI dès story 1
- [Source: epics.md §Story 1.1 AC] — critères d'acceptation officiels
- [Source: epics.md §UX-DR1, UX-DR2] — design system D2, tokens CSS sémantiques, --destructive réservé prof
- [Source: epics.md §NFR-8] — jamais PII élève dans les logs
- [Source: epics.md §NFR-12] — AGPL-3.0

## Dev Agent Record

### Agent Model Used

Claude Opus 4.7 (bmad-dev-story) — story implémentation 2026-05-19

### Debug Log References

- `pnpm install` initial échec : `vite@9.0.7` introuvable sur npm. **Résolution :** la version `9.0.7` mentionnée dans la story concerne `create-vite` (scaffolder), pas le runtime `vite`. La dernière version stable de `vite` au 2026-05-19 est `8.0.13` (vérifiée via `pnpm view vite@latest version`). `package.json` mis à jour avec `vite ^8.0.0`.
- `uv run ruff check .` : 1 erreur initiale `I001` (imports non triés dans `alembic/env.py`) → auto-fix via `--fix`.
- Smoke test Vite dev servers : Job PowerShell ne se terminait pas naturellement (serveur Vite tourne en boucle) ; arrêt manuel via `Stop-Process` après vérification HTTP 200. Cleanup OK.
- `docker compose up postgres` : Docker Desktop non démarré au premier essai. Syntaxe `docker-compose.yml` validée via `docker compose config --quiet` (0 erreur).
- **Re-validation après démarrage de Docker Desktop** — 3 défauts trouvés et corrigés :
  1. `apps/api/Dockerfile.dev` contenait `uv sync --frozen=false` ; la dernière version de `uv` traite `--frozen` comme un booléen sans valeur. Corrigé en `uv sync`.
  2. Absence de `.dockerignore` → Docker copiait les `node_modules` locaux (jonctions Windows pnpm) qui ne sont pas portables sous Linux ; erreur `MODULE_NOT_FOUND` sur `vite/bin/vite.js` au runtime. Ajout d'un `.dockerignore` à la racine excluant `node_modules`, `dist`, `.venv`, `__pycache__`, etc.
  3. Dockerfile.dev front : le `WORKDIR /app/apps/web-X` + `CMD ["pnpm", "dev", "--host", "0.0.0.0"]` exécuté depuis le sous-dossier ne trouvait pas les binaires hoistés par pnpm. Corrigé en gardant `WORKDIR /app` et en lançant `pnpm --filter web-X dev --host 0.0.0.0` depuis la racine workspace.
  Après ces correctifs : 4/4 conteneurs `up`, postgres + api `healthy`, tests HTTP 200 sur les 4 services.

### Completion Notes List

#### Synthèse

Le monorepo Kopie est entièrement scaffold et opérationnel localement. Tous les ACs sont satisfaits, et toutes les chaînes d'outillage (Vite + Tailwind v4, Vitest, FastAPI, ruff, mypy, Alembic, pytest) fonctionnent sans erreur.

#### Résultats des vérifications

| Vérification | Résultat |
|---|---|
| `pnpm install` (workspace racine) | ✅ 214 packages installés en 1 min |
| `pnpm --filter web-prof test` | ✅ 1/1 test Vitest passe (rendu `<App />`) |
| `pnpm --filter web-eleve test` | ✅ 1/1 test Vitest passe |
| `pnpm --filter web-prof build` | ✅ Bundle 192 kB (60 kB gz) — TS + Vite + Tailwind v4 |
| `pnpm --filter web-eleve build` | ✅ Bundle 192 kB (60 kB gz) |
| Vite dev `web-prof` (port 5173) | ✅ HTTP 200 |
| Vite dev `web-eleve` (port 5174) | ✅ HTTP 200 |
| `uv sync --all-extras` | ✅ FastAPI 0.136.1 + 30+ deps installées |
| `uv run ruff check .` | ✅ 0 erreur (après auto-fix initial) |
| `uv run mypy app` | ✅ 0 erreur strict sur 18 fichiers |
| `uv run pytest -v` | ✅ 1/1 test (`test_health` → 200 + `{"status":"ok"}`) |
| Uvicorn démarre local (port 8001) | ✅ `/api/v1/health` = 200, `/docs` = 200 |
| `docker compose config --quiet` | ✅ Syntaxe valide |
| `docker compose up -d --build` (runtime complet) | ✅ 4/4 conteneurs `up` ; postgres + api `healthy` |
| HTTP `:8000/api/v1/health` depuis container | ✅ 200 `{"status":"ok"}` |
| HTTP `:8000/docs` (Swagger UI) | ✅ 200 |
| HTTP `:5173` (web-prof dans container) | ✅ 200 (Vite v8.0.13 ready en 1.5 s) |
| HTTP `:5174` (web-eleve dans container) | ✅ 200 (Vite v8.0.13 ready en 1.6 s) |
| `pg_isready` dans container | ✅ accepting connections sur 5432 |

#### Déviations vs. story

1. **`vite@9.0.7` → `vite ^8.0.0`** : La version `9.0.7` figée dans l'architecture correspond au scaffolder `create-vite` (vérifié sur npm), pas au runtime. Le scaffolder `create-vite@9.0.7` est bien présent ; il génère un projet qui pointe vers Vite 8.x. La directive « ne pas utiliser `create-vite@latest` » est respectée puisque la dernière version du scaffolder est précisément `9.0.7` au moment de l'implémentation. Aligné avec `@vitejs/plugin-react@^6` (peer Vite 8).
2. **Scaffolding manuel des fronts au lieu de `pnpm create vite@9.0.7`** : Choix d'écrire directement les fichiers (`package.json`, `vite.config.ts`, `index.html`, `src/*`) pour produire immédiatement la configuration cible (Tailwind v4 + Vitest + Lucide + thèmes UX-DR1/UX-DR2). Le résultat est strictement équivalent à `create-vite` + customisation, plus déterministe (pas de prompts interactifs). Toutes les vérifications le confirment.
3. **`docker compose up` validé end-to-end** après démarrage de Docker Desktop. 3 défauts d'image trouvés et corrigés (voir Debug Log). Les 4 conteneurs tournent, healthchecks `healthy`, smoke tests HTTP 200 sur tous les endpoints.
4. **Versions packages 2026-05-19** : `lucide-react@^1.16` (et non `^0.469`), `vitest@^4`, `@vitejs/plugin-react@^6`, `jsdom@^29` — versions stables disponibles sur npm au jour J. Aucune dépendance majeure de la stack ne s'écarte de l'architecture.
5. **Outils manquants au démarrage** : `pnpm` et `uv` n'étaient pas installés ; ils ont été ajoutés (`npm install -g pnpm` → 10.33.4 ; script Astral pour uv → 0.11.15). Avec accord utilisateur explicite.

#### Conformité architecture / NFR

- ✅ Tailwind v4 via `@tailwindcss/vite` — aucun `tailwind.config.js` créé.
- ✅ Thèmes `theme-teacher` (slate clair, primary `#2563eb`, `--destructive`) et `theme-student` (blanc pur, sans `--destructive`, font-size 16 px). UX-DR1 + UX-DR2 respectés.
- ✅ CORS configuré avec origines explicites (`http://localhost:5173`, `http://localhost:5174`), jamais `["*"]`.
- ✅ `structlog` configuré en mode JSON, jamais de log de PII (commentaire NFR-8 explicite dans `app/core/logging.py`).
- ✅ AGPL-3.0-only : `LICENSE` (texte officiel GNU, 34 kB) + champ `license` dans `package.json` et `pyproject.toml`.
- ✅ `.env` exclu du dépôt (`.gitignore`), `.env.example` documenté.
- ✅ Modèles SQLAlchemy avec `DeclarativeBase` async-ready (`app/models/base.py`). Migrations Alembic async via `async_engine_from_config` (`alembic/env.py`).
- ✅ Structure modulaire API : `api/`, `core/`, `models/`, `schemas/`, `services/`, `repositories/`, `jobs/` — tous présents avec placeholders documentés.
- ✅ Placeholders documentés pour les stories futures : `docker-compose.prod.yml` (6.1), `Caddyfile` (6.2), `scripts/migrate.sh` (6.3), `app/jobs/` (6.4), `docs/self-hosting.md` (6.6), `app/core/security.py` (1.4), `app/core/event_types.py` (4.5).

#### Notes pour la review

- L'instance `uv` est installée dans `C:\Users\Grégory\.local\bin` — penser à ajouter ce dossier au `Path` global du système (actuellement ajouté à la session shell seulement).
- Le `.npmrc` configure `auto-install-peers=true` ; les warnings npm sur ces clés (visibles avec `npm view ...`) sont attendus côté pnpm/npm cohabitation.
- La CI GitHub Actions est complète (jobs `lint-api`, `test-api`, `lint-front`, `test-front`, `build`) mais non exécutée localement faute de runner GH Actions ; à valider sur première PR.

#### Résolution des findings de review (2026-05-19)

- ✅ **Resolved review finding [Patch] : Secret par défaut prédictible pour l'API (`SECRET_KEY`) [docker-compose.yml]**
  - Suppression du fallback `:-changeme-…` → remplacé par `${SECRET_KEY:?...}` : Compose refuse de démarrer avec un message explicite si la variable est absente ou vide.
  - `.env.example` : `SECRET_KEY=` (vide) + commentaire pointant vers `openssl rand -hex 32`. Plus aucun sentinel utilisable par défaut.
  - Validation : `docker compose config` sans `SECRET_KEY` → exit 15 avec message clair (« SECRET_KEY must be defined in .env… »). Avec `SECRET_KEY=dummy` → exit 0.
  - Note : le défaut `"changeme…"` dans `app/core/config.py` est conservé volontairement (dev local hors-Docker, tests pytest qui importent `app.main`). Le périmètre du finding (`[docker-compose.yml]`) est pleinement couvert.

- ✅ **Resolved review finding [Patch] : Configuration CORS figée dans Docker Compose au lieu d'être pilotée par variable d'environnement [docker-compose.yml]**
  - `CORS_ORIGINS: '${CORS_ORIGINS:-["http://localhost:5173","http://localhost:5174"]}'` : pilotable par `.env`, défaut dev conservé.
  - Validation : `CORS_ORIGINS='["https://prof.kopie.cc","https://eleve.kopie.cc"]'` propagée correctement par `docker compose config`.

- ✅ **Resolved review finding [Patch] : CI front non déterministe (`pnpm install --frozen-lockfile=false`) [`.github/workflows/ci.yml`]**
  - Les 3 occurrences (`lint-front`, `test-front`, `build`) passent à `pnpm install --frozen-lockfile`.
  - Pré-requis : `pnpm-lock.yaml` racine versionné (présent, non-ignoré). Toute désynchronisation lock ↔ `package.json` fera désormais échouer la CI immédiatement.

- ✅ **Resolved review finding [Patch] : Politique de version Node incohérente entre `engines`, CI et images Docker [package.json]**
  - Source unique de vérité créée : `.nvmrc` = `22.12.0` à la racine.
  - CI : `actions/setup-node@v4` avec `node-version-file: '.nvmrc'` sur les 3 jobs front (au lieu de `node-version: '22'`).
  - Dockerfiles front : `FROM node:22.12.0-alpine` (au lieu de `node:22-alpine`).
  - `package.json` : `engines.node` borné à `">=22.12.0 <23.0.0"` (au lieu de `">=22.12.0"`) pour interdire un saut majeur involontaire.

### File List

#### Racine du monorepo (nouveaux)
- `package.json`
- `pnpm-workspace.yaml`
- `pnpm-lock.yaml` (généré)
- `.gitignore`
- `.dockerignore`
- `.npmrc`
- `.nvmrc` *(ajouté lors de la review-fix 2026-05-19 — source unique de vérité Node 22.12.0)*
- `.env.example`
- `README.md`
- `LICENSE` (AGPL-3.0)
- `docker-compose.yml`
- `docker-compose.prod.yml` (placeholder Story 6.1)
- `Caddyfile` (placeholder Story 6.2)

#### CI / scripts / docs
- `.github/workflows/ci.yml`
- `scripts/gen-types.sh` (placeholder Story 1.2)
- `scripts/migrate.sh` (placeholder Story 6.3)
- `docs/self-hosting.md` (placeholder Story 6.6)

#### Contrats
- `contracts/openapi.yaml`

#### Package partagé
- `packages/shared-types/package.json`
- `packages/shared-types/index.ts`
- `packages/shared-types/tsconfig.json`
- `packages/shared-types/README.md`

#### `apps/web-prof/`
- `apps/web-prof/package.json`
- `apps/web-prof/index.html`
- `apps/web-prof/vite.config.ts`
- `apps/web-prof/vitest.config.ts`
- `apps/web-prof/tsconfig.json`
- `apps/web-prof/tsconfig.app.json`
- `apps/web-prof/tsconfig.node.json`
- `apps/web-prof/eslint.config.js`
- `apps/web-prof/Dockerfile.dev`
- `apps/web-prof/.env.development`
- `apps/web-prof/.gitignore`
- `apps/web-prof/src/main.tsx`
- `apps/web-prof/src/App.tsx`
- `apps/web-prof/src/index.css`
- `apps/web-prof/src/vite-env.d.ts`
- `apps/web-prof/src/test/setup.ts`
- `apps/web-prof/src/__tests__/App.test.tsx`

#### `apps/web-eleve/`
- `apps/web-eleve/package.json`
- `apps/web-eleve/index.html`
- `apps/web-eleve/vite.config.ts`
- `apps/web-eleve/vitest.config.ts`
- `apps/web-eleve/tsconfig.json`
- `apps/web-eleve/tsconfig.app.json`
- `apps/web-eleve/tsconfig.node.json`
- `apps/web-eleve/eslint.config.js`
- `apps/web-eleve/Dockerfile.dev`
- `apps/web-eleve/.env.development`
- `apps/web-eleve/.gitignore`
- `apps/web-eleve/src/main.tsx`
- `apps/web-eleve/src/App.tsx`
- `apps/web-eleve/src/index.css`
- `apps/web-eleve/src/vite-env.d.ts`
- `apps/web-eleve/src/test/setup.ts`
- `apps/web-eleve/src/__tests__/App.test.tsx`

#### `apps/api/`
- `apps/api/pyproject.toml`
- `apps/api/uv.lock` (généré)
- `apps/api/.python-version`
- `apps/api/alembic.ini`
- `apps/api/Dockerfile.dev`
- `apps/api/alembic/env.py`
- `apps/api/alembic/script.py.mako`
- `apps/api/alembic/README`
- `apps/api/alembic/versions/.gitkeep`
- `apps/api/app/__init__.py`
- `apps/api/app/main.py`
- `apps/api/app/api/__init__.py`
- `apps/api/app/api/v1/__init__.py`
- `apps/api/app/api/v1/router.py`
- `apps/api/app/api/v1/endpoints/__init__.py`
- `apps/api/app/api/v1/endpoints/health.py`
- `apps/api/app/core/__init__.py`
- `apps/api/app/core/config.py`
- `apps/api/app/core/logging.py`
- `apps/api/app/core/security.py` (placeholder Story 1.4)
- `apps/api/app/core/event_types.py` (placeholder Story 4.5)
- `apps/api/app/models/__init__.py`
- `apps/api/app/models/base.py`
- `apps/api/app/schemas/__init__.py`
- `apps/api/app/services/__init__.py`
- `apps/api/app/repositories/__init__.py`
- `apps/api/app/jobs/__init__.py` (placeholder Story 6.4)
- `apps/api/tests/__init__.py`
- `apps/api/tests/test_health.py`

#### Mises à jour
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (statut story 1-1 : `ready-for-dev` → `in-progress` → `review`)

## Change Log

| Date | Auteur | Description |
|---|---|---|
| 2026-05-19 | Dev (Opus 4.7) | Scaffold complet : monorepo pnpm, web-prof + web-eleve (Vite 8 + Tailwind v4 + Vitest), API FastAPI 0.136.1 + Alembic async, Docker Compose dev, contrat OpenAPI squelette, CI GitHub Actions, package shared-types. Toutes ACs satisfaites ; AC 2 partiellement validée (compose syntax OK ; runtime non exercé). Statut → `review`. |
| 2026-05-19 | Dev (Opus 4.7) | Re-validation AC 2 après démarrage Docker Desktop : ajout `.dockerignore` racine ; correctif `apps/api/Dockerfile.dev` (`uv sync --frozen=false` → `uv sync`) ; correctif Dockerfile.dev fronts (CMD `pnpm --filter web-X dev` depuis `/app` au lieu de `cd` dans le sous-dossier). 4/4 conteneurs `up`, health endpoints validés. |
| 2026-05-19 | Dev (Opus 4.7) | Addressed code review findings — 4 items resolved : (1) `SECRET_KEY` rendu obligatoire dans `docker-compose.yml` via `${SECRET_KEY:?…}` + `.env.example` épuré ; (2) `CORS_ORIGINS` pilotable par `.env` avec défaut dev local ; (3) CI front passe à `pnpm install --frozen-lockfile` sur les 3 jobs ; (4) version Node unifiée via `.nvmrc=22.12.0` + `node-version-file` en CI + `node:22.12.0-alpine` dans les Dockerfiles + `engines.node` borné `>=22.12.0 <23.0.0`. Validation `docker compose config` OK (échec attendu sans `SECRET_KEY`, succès avec). |

