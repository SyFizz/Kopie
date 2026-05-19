---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
workflowType: architecture
lastStep: 8
status: complete
completedAt: 2026-05-19
inputDocuments:
  - _bmad-output/planning-artifacts/prds/prd-Kopie-2026-05-19/prd.md
  - _bmad-output/planning-artifacts/prds/prd-Kopie-2026-05-19/addendum.md
  - _bmad-output/planning-artifacts/prds/prd-Kopie-2026-05-19/.decision-log.md
  - _bmad-output/planning-artifacts/briefs/brief-Kopie-2026-05-19/brief.md
  - _bmad-output/planning-artifacts/briefs/brief-Kopie-2026-05-19/addendum.md
  - _bmad-output/planning-artifacts/briefs/brief-Kopie-2026-05-19/.decision-log.md
project_name: Kopie
user_name: Gregory
date: 2026-05-19
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements:**

Kopie est une plateforme **full-stack web asynchrone** à deux personas distincts :

1. **Espace enseignant (authentifié)** — CRUD évaluations, banque de questions, import CSV, variantes (standard/PAP), génération d’accès individuels (lien signé, fenêtre, aménagements), consultation résultats/journal, exports, historique des envois. L’isolation stricte des données par enseignant (FR-4) impose un modèle **multi-tenant logique** dès le MVP.

2. **Interface élève (non authentifiée, token d’accès)** — Identification légère (nom/prénom), session unique via lien, plein écran, timer avec aménagements, navigation conditionnelle, journalisation d’événements d’intégrité (fullscreen, visibility, copier-coller, DevTools), soumission avec confirmation. Posture **« tracer, pas sanctionner »** : événements suspects journalisés, avertissements non bloquants.

3. **Couche déploiement / ops** — Configuration par `.env`, Docker Compose (app + PostgreSQL + reverse proxy HTTPS), migrations versionnées, documentation self-host, instance cloud officielle fonctionnellement équivalente (FR-39).

Points structurants pour l’architecture :

- **Modèle de données polymorphe** pour les types de questions (FR-5, extensibilité future) avec `schemaVersion` dès le jour 1.
- **Machine à états** pour accès individuels : en attente → en cours → terminée / expirée / invalidée — distinction claire **accès (token)** vs **session (passage)**.
- **Journal append-only** horodaté serveur (référence authoritative) + client ; idempotence sur ingestion ; politique effacement vs immuabilité RGPD à trancher (pseudonymisation, tombstones).
- **Tokens d’accès** HMAC ou JWT à usage contrôlé, invalidation serveur, rate limiting.
- **Pas de WebSocket** au MVP ; **polling léger ou ETag/`updatedAt`** côté enseignant pour suivi des soumissions.

**Non-Functional Requirements:**

| Domaine | Exigence | Impact architecture |
|---------|----------|---------------------|
| Performance | FCP élève < 3 s, interactions < 100 ms ressenti, matériel modeste/ADSL | SPA élève optimisée, bundle léger |
| Sécurité | OWASP Top 10, rate limiting, secrets hors repo, audits CI | Middleware sécurité, OpenAPI, tests isolation tenant |
| Accessibilité | RGAA AA côté élève, OpenDyslexic via aménagements | Design system élève dédié ; structure sémantique, clavier, `aria-live` |
| Compatibilité | Chrome/Firefox complets ; Safari/iOS best-effort | Mode examen **dégradé** documenté (bannière, reprise guidée) |
| i18n | Chaînes externalisées, français au MVP | Couche i18n dès le départ |
| Observabilité | Logs structurés, pas de données élève en clair | Corrélation `request_id` / `session_id` |
| RGPD / légal | Hébergement UE, conservation paramétrable (défaut 12 mois) | Jobs purge, export avant suppression |
| Licence | AGPL-3.0 | Compatibilité dépendances, distribution cloud + self-host |

**Scale & Complexity:**

- **Domaine principal :** full-stack web (React/Vite frontend + API REST + PostgreSQL)
- **Niveau de complexité :** **moyen-élevé** — faible en infra distribuée, élevé en conformité, intégrité session et dual-surface UX
- **Runtime MVP (5 composants)** : API (+ modules export/journal), worker léger optionnel, PostgreSQL, stockage fichiers, reverse proxy
- **Capacités logiques (~8)** : auth, évaluations, accès, sessions, journal, exports, purge, notifications email async

### Bounded Contexts

| Contexte | Responsabilité |
|----------|----------------|
| Identity | JWT enseignant, refresh, révocation |
| Evaluation lifecycle | CRUD, variantes, banque, import |
| Student access | Tokens signés, fenêtres, aménagements figés |
| Submission & grading | Session, réponses, correction auto/manuelle |
| Audit journal | Événements append-only, exports |
| Notifications | Email async (validation compte, etc.) |

### Technical Constraints & Dependencies

**Contraintes explicites (PRD + addendum) :**

- Stack indicative : React + Vite + TailwindCSS ; backend **Node/Fastify OU Python/FastAPI** (à trancher étape 3–4)
- PostgreSQL obligatoire ; auth JWT local (OAuth/SAML → v1)
- Zéro WebSocket au MVP
- Docker Compose + images GHCR ; HTTPS Let’s Encrypt
- APIs navigateur standard uniquement côté élève
- Instance cloud officielle = **même codebase** que self-host

**Dual-surface UX (contrainte architecture) :**

- UI enseignant et UI élève : bundles ou apps distincts, tokens/composants séparés
- PAP et timer : **état de session serveur** ; accommodations revalidées à chaque requête
- Sauvegarde incrémentale, reprise après fermeture d’onglet, vue « sessions incomplètes » enseignant

**Rails implémentation (Party Mode / revue technique) :**

- `contracts/openapi.yaml` versionné dès story 1
- `docs/adr/` pour décisions stack, auth, exports
- Migrations outillées ; service `migrate` dans Compose
- Tests isolation tenant automatisés ; fixtures CSV réalistes
- Idempotency keys sur ingestion journal ; stratégie exports (libs, streaming)

**Questions ouvertes reportées :**

1. Choix Node vs Python
2. Schéma polymorphe des types de questions
3. Chiffrement applicatif vs disque managé cloud EU
4. CI/CD et scans de vulnérabilités
5. Modèle multi-tenant cloud (schéma partagé vs instance établissement)
6. Comportement session abandonnée (reprise vs nouvel accès)
7. Format import Markdown

### Cross-Cutting Concerns Identified

| Préoccupation | Périmètre |
|---------------|-----------|
| Isolation enseignant (`teacher_id` au query layer) | API, SQL, exports, tests |
| Auth dual (JWT / token élève) | Surfaces, rate limiting, messages d’erreur asymétriques |
| Horodatage et intégrité journal | Client batch + serveur authoritative |
| Gestion du temps | Fenêtres, timer, aménagements |
| Exports PDF/CSV | Templates, streaming, i18n polices |
| Configuration déploiement | `.env`, rétention, secrets, TLS |
| Conformité RGPD | Minimisation, purge, documentation légale |
| Accessibilité | RGAA AA surface élève |
| Extensibilité types de questions | Schéma versionné + rendu UI |
| Observabilité & erreurs API | Format stable, healthchecks |

## Starter Template Evaluation

### Primary Technology Domain

Application web full-stack asynchrone : 2 SPA React (enseignant / élève) + API REST Python + PostgreSQL + Docker Compose. Pas de temps réel MVP.

### Décisions utilisateur (2026-05-19)

| Sujet | Choix |
|-------|-------|
| Backend | **Python FastAPI** |
| Monorepo | **pnpm workspaces** (gestionnaire unique front + orchestration) |
| Frontends | **Deux apps Vite** distinctes |
| Hébergement front (cible) | `prof.kopie.cc` (enseignant), `eleve.kopie.cc` (élève) |

### Starter Options Considered

| Option | Rôle | Statut |
|--------|------|--------|
| create-vite@**9.0.7** (`react-ts`) | Frontend ×2 | Retenu |
| @tailwindcss/vite (Tailwind v4) | Styles | Retenu (post-install par app) |
| **uv** + structure FastAPI manuelle | API Python | Retenu |
| fastify-cli@8.0.0 | API Node | Écarté (préférence Python) |
| cookiecutter-fastapi | Scaffold API | Référence — structure trop opinionée (auth/users) pour MVP ; structure `app/` custom retenue |
| Turborepo starters communautaires | Monorepo | Écarté (maintenance / décalage) |

### Selected Starter: pnpm monorepo + create-vite ×2 + uv + FastAPI

**Rationale for Selection:**

- Aligné PRD (React/Vite/Tailwind) et choix **FastAPI** pour l’API
- **pnpm** : un seul `node_modules` à la racine, commandes `pnpm --filter <app> dev`, adapté au monorepo sans courbe d’apprentissage lourde (équivalent npm/yarn, plus rapide et strict sur les dépendances)
- **Deux apps** = bundles optimisés (élève minimal), déploiement et cookies isolés par sous-domaine
- **uv** : gestion moderne des dépendances Python (`pyproject.toml`, `uv.lock`), rapide, standard 2026
- API : structure **production-ready** modulaire (`app/api`, `services`, `repositories`) plutôt qu’un cookiecutter surchargé

**Initialization Commands:**

```bash
# Prérequis : Node.js 22.12+ (ou 20.19+), pnpm, uv, Python 3.12+
mkdir kopie && cd kopie
pnpm init

# Workspace pnpm (pnpm-workspace.yaml)
# packages:
#   - 'apps/*'
#   - 'packages/*'

# Frontends
pnpm create vite@latest apps/web-prof -- --template react-ts
pnpm create vite@latest apps/web-eleve -- --template react-ts

# Tailwind v4 (par app)
pnpm add -D tailwindcss @tailwindcss/vite --filter web-prof
pnpm add -D tailwindcss @tailwindcss/vite --filter web-eleve
# vite.config.ts : plugins [react(), tailwindcss()]
# index.css : @import "tailwindcss";

# Tests front
pnpm add -D vitest @testing-library/react --filter web-prof
pnpm add -D vitest @testing-library/react --filter web-eleve

# API Python
uv init apps/api --package
cd apps/api
uv add fastapi uvicorn[standard] sqlalchemy alembic pydantic-settings python-jose[cryptography] passlib[bcrypt] httpx
uv add --dev pytest pytest-asyncio ruff mypy
# Structure app/ à créer (main.py, api/v1/, core/, models/, schemas/, services/, repositories/)
```

**Déploiement sous-domaines (cible) :**

| App | Package | URL cible | Rôle |
|-----|---------|-----------|------|
| Enseignant | `apps/web-prof` | `https://prof.kopie.cc` | Composition, accès, résultats |
| Élève | `apps/web-eleve` | `https://eleve.kopie.cc` | Session examen |
| API | `apps/api` | `https://api.kopie.cc` (ou path unique derrière proxy) | REST + OpenAPI |

CORS : origines explicites `prof.kopie.cc` et `eleve.kopie.cc` uniquement.

### Architectural Decisions Provided by Starter

**Language & Runtime:** TypeScript (front) ; Python 3.12+ (API) ; Node 20.19+ / 22.12+ pour toolchain front

**Styling Solution:** Tailwind CSS v4 via `@tailwindcss/vite`

**Build Tooling:** Vite (create-vite 9) ; uvicorn pour FastAPI

**Testing Framework:** Vitest + Testing Library (front) ; pytest + pytest-asyncio (API)

**Code Organization:**

```
kopie/
├── apps/
│   ├── web-prof/      # prof.kopie.cc
│   ├── web-eleve/     # eleve.kopie.cc
│   └── api/           # FastAPI (uv)
├── packages/
│   └── shared-types/  # types TS générés depuis OpenAPI (openapi-typescript)
├── pnpm-workspace.yaml
└── docker-compose.yml
```

**Development Experience:** `pnpm --filter web-prof dev` ; `pnpm --filter web-eleve dev` ; `uv run uvicorn app.main:app --reload` dans `apps/api`

**Note:** Le scaffold monorepo + deux Vite + squelette FastAPI + Docker Compose minimal constitue la **première story d’implémentation**.

## Core Architectural Decisions

### Decision Priority Analysis

**Critical Decisions (Block Implementation):**

- Backend **FastAPI 0.136.1** + Python **≥3.12** + **uv**
- **PostgreSQL** + SQLAlchemy 2.x async + Alembic
- Monorepo **pnpm** : `web-prof`, `web-eleve`, `api`
- Sous-domaines : `prof.kopie.cc`, `eleve.kopie.cc`, `api.kopie.cc`
- Auth enseignant JWT (access + refresh cookie httpOnly)
- Accès élève par **JWT signé** à usage contrôlé
- Isolation **`teacher_id`** au niveau repository/query
- Questions : **JSONB** + `type` + `schemaVersion`
- REST `/api/v1` + OpenAPI → `shared-types`

**Important Decisions (Shape Architecture):**

- TanStack Query + React Router (front)
- react-i18next (français MVP)
- Journal : POST batch + idempotency-key
- Polling enseignant sur statuts accès (`updatedAt`)
- Caddy + Docker Compose + GHCR + GitHub Actions
- slowapi rate limiting
- structlog JSON sans PII élève

**Deferred Decisions (Post-MVP):**

- SSO ENT / OAuth2 / SAML2
- Redis / cache applicatif
- Chiffrement applicatif par champ
- Format import Markdown (story dédiée)
- Choix hébergeur UE précis (OVH / Scaleway / Hetzner)

**Décision MVP tranchée (session abandonnée) :** sauvegarde incrémentale des réponses + reprise tant que la session n’est pas soumée ; pas de nouveau lien requis.

### Data Architecture

| Décision | Choix | Version / détail |
|----------|-------|------------------|
| SGBD | PostgreSQL | PRD |
| ORM | SQLAlchemy 2.x mode async | Compatible FastAPI |
| Migrations | Alembic | Versionnées, exécutées au déploiement |
| Validation | Pydantic v2 (schemas) séparés des models ORM | |
| Questions | JSONB `content` + colonnes `type`, `schema_version` | Extensibilité FR-5 |
| Multi-tenant | `teacher_id` UUID FK sur toutes tables métier | Tests d’isolation obligatoires |
| Cache | Aucun au MVP | |
| Rétention | Job planifié ; défaut **12 mois** (config `.env`) | FR-41 |

### Authentication & Security

| Décision | Choix | Rationale |
|----------|-------|-----------|
| Enseignant | JWT access (court) + refresh (rotation) | FR-2 |
| Stockage client prof | Access en mémoire ; refresh **httpOnly** `Secure` `SameSite=Strict` sur `prof.kopie.cc` | Limite XSS |
| Élève | JWT signé embarqué dans le lien d’accès ; validation à chaque requête | FR-11, FR-40 |
| Mots de passe | bcrypt (passlib) | FR-1 |
| Rate limiting | slowapi sur `/auth/*` et routes accès public | FR-43 |
| CSRF | Protection sur mutations prof (cookie refresh) ; surface élève stateless | Dual-surface |
| Chiffrement repos | Disque managé hébergeur UE au MVP | Pragmatique |

### API & Communication Patterns

| Décision | Choix | Rationale |
|----------|-------|-----------|
| Style | REST `/api/v1/...` | Simplicité, PRD |
| Documentation | OpenAPI natif FastAPI | Contrat unique |
| Types front | `openapi-typescript` → `packages/shared-types` | Cohérence agents |
| Erreurs | `{ "error": { "code", "message", "details" } }` | Stable |
| Journal événements | `POST /api/v1/sessions/{id}/events` batch + header `Idempotency-Key` | Intégrité append-only |
| **Drafts réponses élève** | `POST /api/v1/sessions/{id}/answers` (idempotent par `question_id` + `X-Idempotency-Key`) + `GET /api/v1/sessions/{id}/answers` (reprise) | Sauvegarde incrémentale Story 4.6 ; distinct du journal (mutable jusqu'à soumission, gelé après) |
| Temps réel | Polling `GET /api/v1/accesses/{id}` | Pas de WebSocket |
| CORS | Origines `https://prof.kopie.cc`, `https://eleve.kopie.cc` uniquement | |

### Frontend Architecture

| Décision | Choix | Rationale |
|----------|-------|-----------|
| Data serveur | TanStack Query | Cache, polling |
| Routing | React Router v7 | Par app |
| i18n | react-i18next | NFR |
| State local | useState / useReducer ; pas de Redux | MVP léger |
| Bundle élève | Code-splitting, deps minimales | FCP < 3 s |
| Config | `VITE_API_URL=https://api.kopie.cc` | Les deux apps |
| a11y | eslint-plugin-jsx-a11y + revue RGAA | FR élève |
| Déploiement | Builds statiques servis derrière Caddy | Sous-domaines |

### Infrastructure & Deployment

| Décision | Choix | Rationale |
|----------|-------|-----------|
| Reverse proxy | Caddy (TLS Let’s Encrypt) | FR-36 |
| Compose | postgres, api, web-prof, web-eleve | FR-35 |
| Registry | GHCR | Addendum |
| CI | GitHub Actions : ruff, mypy, pytest, vitest, build, scan deps | NFR |
| Région | Union européenne uniquement | RGPD |
| Logs API | structlog JSON ; jamais nom/prénom élève en clair | NFR |

### Decision Impact Analysis

**Implementation Sequence:**

1. Scaffold monorepo (pnpm + uv + 2 Vite + squelette FastAPI)
2. Docker Compose + Caddy + PostgreSQL + migrations Alembic
3. Auth enseignant + isolation `teacher_id`
4. Modèle évaluation / questions JSONB
5. Accès individuel + tokens élève
6. Session élève + journal batch
7. Résultats + exports
8. Front prof puis front élève
9. CI + documentation self-host

**Cross-Component Dependencies:**

- OpenAPI doit précéder les stories front consommant l’API
- `shared-types` régénéré à chaque changement de contrat
- Aménagements PAP figés sur l’accès → lus par API session et rendus par `web-eleve` uniquement
- CORS et cookies liés aux sous-domaines figés avant tests e2e

## Implementation Patterns & Consistency Rules

### Pattern Categories Defined

**Points de conflit identifiés :** 12 zones (nommage DB/API/code, structure monorepo, formats JSON, événements journal, auth, erreurs, dates, tests).

### Naming Patterns

**Database (PostgreSQL) :**

- Tables : `snake_case` pluriel — `teachers`, `evaluations`, `individual_accesses`, `sessions`, `session_events`
- Colonnes : `snake_case` — `teacher_id`, `created_at`, `schema_version`
- PK : `id` (UUID v4)
- FK : `{entity}_id`
- Index : `ix_{table}_{columns}`
- Contraintes : `uq_{table}_{columns}`, `fk_{table}_{ref}`

**API REST :**

- Ressources plurielles : `/api/v1/evaluations`, `/api/v1/individual-accesses`
- IDs UUID dans le path
- Query : `snake_case`
- Headers : `X-Idempotency-Key`, `X-Request-Id`
- Codes erreur : `SCREAMING_SNAKE` — `ACCESS_EXPIRED`, `SESSION_ALREADY_SUBMITTED`

**Code :**

- Python : PEP 8 — `snake_case`, `PascalCase` classes, fichiers `snake_case.py`
- TypeScript : `PascalCase` composants, `camelCase` variables, `PascalCase.tsx` pour composants
- Routes React : kebab dans l’URL — `/evaluations/:evaluationId/accesses`

### Structure Patterns

**Monorepo :** features par domaine dans chaque app ; `services/` + `repositories/` côté API ; `packages/shared-types/` généré (ne pas éditer à la main).

**Tests :** API `apps/api/tests/` ; front `*.test.tsx` co-localisés ; e2e futur `tests/e2e/`.

### Format Patterns

**API JSON :** `snake_case` ; dates ISO 8601 UTC `Z` ; succès = corps direct ou `{ "items": [], "total": n }` pour listes ; erreurs `{ "error": { "code", "message", "details" } }` ; HTTP 410 pour accès invalidé.

**Journal batch :** `events[].type` en `snake_case` ; catalogue dans `app/core/event_types.py` ; header `X-Idempotency-Key` obligatoire.

### Communication Patterns

**TanStack Query :** clés `['evaluations', id]` ; polling accès `refetchInterval: 5000` si `pending` ou `in_progress`.

### Process Patterns

**Auth prof :** login → access + cookie refresh ; 401 → refresh → retry une fois.

**Auth élève :** token dans le path `eleve.kopie.cc/s/{token}` ; pas de header Authorization.

**Isolation :** dependency `get_current_teacher` + filtre `teacher_id` dans chaque repository ; test automatisé cross-teacher interdit.

### Enforcement Guidelines

**All AI Agents MUST :**

- Régénérer `shared-types` après changement OpenAPI
- Filtrer `teacher_id` dans chaque requête repository prof
- Utiliser `X-Idempotency-Key` pour le journal
- Placer la logique métier dans `services/`, pas dans les endpoints
- Ne jamais logger nom/prénom élève

**Vérification :** ruff, mypy, pytest, eslint, vitest ; checklist PR alignée sur cette section.

### Pattern Examples

**Bon :** repository avec `.where(IndividualAccess.teacher_id == teacher_id)`.

**Anti-pattern :** `db.get(Session, id)` sans filtre enseignant dans une route prof.

## Project Structure & Boundaries

### Complete Project Directory Structure

```
kopie/
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
├── pnpm-workspace.yaml
├── package.json
├── docker-compose.yml
├── docker-compose.prod.yml
├── Caddyfile
├── .github/workflows/ci.yml
├── docs/self-hosting.md
├── docs/architecture-patterns.md
├── contracts/openapi.yaml
├── scripts/gen-types.sh
├── scripts/migrate.sh
├── packages/shared-types/          # généré (openapi-typescript)
├── apps/api/                       # FastAPI + uv + Alembic
│   ├── app/api/v1/endpoints/     # auth, evaluations, accesses, sessions, events, results, exports
│   ├── app/core/                 # security, event_types, exceptions, logging
│   ├── app/models/ | schemas/ | services/ | repositories/ | jobs/
│   └── tests/
├── apps/web-prof/                  # prof.kopie.cc
│   └── src/features/             # auth, evaluations, accesses, results, journal
├── apps/web-eleve/                 # eleve.kopie.cc
│   └── src/features/session/     # /s/:token, timer, integrity monitor
└── tests/e2e/                    # post-MVP
```

### Architectural Boundaries

| Surface | Hôte | Auth |
|---------|------|------|
| Enseignant | `prof.kopie.cc` | JWT + cookie refresh |
| Élève | `eleve.kopie.cc/s/{token}` | Token path |
| API | `api.kopie.cc` | Par route |

**Flux :** prof → API → DB ; élève → API (token) → journal batch ; pas de communication directe entre fronts.

### Requirements to Structure Mapping

| FR | Emplacement principal |
|----|------------------------|
| FR-1…4 | `endpoints/auth.py`, `teachers.py`, `web-prof/features/auth/` |
| FR-5…10 | `evaluations.py`, `questions.py`, `imports.py`, `web-prof/features/evaluations/` |
| FR-11…14 | `individual_accesses.py`, `web-prof/features/accesses/` |
| FR-15…24 | `sessions.py`, `web-eleve/features/session/` |
| FR-25…28 | `session_events.py`, journal prof + `useSessionEvents.ts` |
| FR-29…33 | `results.py`, `exports.py`, `web-prof/features/results/` |
| FR-34…39 | Docker, Caddy, `docs/self-hosting.md` |
| FR-40…43 | `core/security.py`, rate limiting, config rétention |

### Integration Points

- **Interne :** HTTPS vers `api.kopie.cc` ; CORS deux origines front
- **Externe :** SMTP validation email (MVP) ; pas d’ENT
- **Données :** PostgreSQL unique ; isolation `teacher_id`

## Architecture Validation Results

### Coherence Validation ✅

**Decision Compatibility :** Stack cohérente — TypeScript (2× Vite) + Python FastAPI + PostgreSQL + pnpm monorepo + Docker/Caddy. Pas de conflit Node/Python (rôles séparés). Versions documentées (create-vite 9.0.7, FastAPI 0.136.1).

**Pattern Consistency :** `snake_case` API/DB aligné avec Python ; isolation `teacher_id` propagée structure → repositories → tests ; dual-auth (JWT prof / token élève) reflétée dans les boundaries.

**Structure Alignment :** Arborescence `apps/api`, `web-prof`, `web-eleve`, `shared-types` supporte les sous-domaines et le mapping FR.

### Requirements Coverage Validation ✅

**Functional Requirements Coverage :** FR-1 à FR-43 mappés vers endpoints et features (voir tableau structure). Questions ouvertes PRD §10 traitées ou reportées explicitement.

**Non-Functional Requirements Coverage :** Perf (bundle élève), sécurité (OWASP, rate limit), RGAA (web-eleve), i18n, observabilité (structlog), RGPD (UE, rétention, purge job) — couverts architecturalement.

### Implementation Readiness Validation ✅

**Decision Completeness :** Décisions critiques documentées avec versions et commandes d’init.

**Structure Completeness :** Arbre projet et mapping FR fournis.

**Pattern Completeness :** Conventions nommage, formats API, auth, isolation — avec exemples bon/anti-pattern.

### Gap Analysis Results

| Priorité | Écart | Action |
|----------|-------|--------|
| Important | Documentation juridique RGPD (`docs/legal/`) | Story 6.8 avant bêta publique |
| Important | Spécification import Markdown | **Story 2.7 dédiée** (spécification + implémentation) |
| Important | Choix hébergeur UE précis | Décision déploiement |
| Mineur | E2E tests | Post-MVP |
| Mineur | Catalogue complet `event_types.py` | À compléter en implémentation session |

Aucun écart **bloquant** pour démarrer le scaffold.

### Validation Issues Addressed

- Node vs Python : **tranché** (FastAPI)
- Session abandonnée : **sauvegarde incrémentale + reprise** avant soumission
- Multi-tenant cloud : schéma partagé + `teacher_id` au MVP

### Architecture Completeness Checklist

**Requirements Analysis**

- [x] Project context thoroughly analyzed
- [x] Scale and complexity assessed
- [x] Technical constraints identified
- [x] Cross-cutting concerns mapped

**Architectural Decisions**

- [x] Critical decisions documented with versions
- [x] Technology stack fully specified
- [x] Integration patterns defined
- [x] Performance considerations addressed

**Implementation Patterns**

- [x] Naming conventions established
- [x] Structure patterns defined
- [x] Communication patterns specified
- [x] Process patterns documented

**Project Structure**

- [x] Complete directory structure defined
- [x] Component boundaries established
- [x] Integration points mapped
- [x] Requirements to structure mapping complete

### Architecture Readiness Assessment

**Overall Status :** **READY WITH MINOR GAPS** (documentation légale et import Markdown à préciser en stories ; aucun blocant scaffold)

**Confidence Level :** **Élevé**

**Key Strengths :**

- Dual-surface claire (prof / élève / api)
- Posture « tracer pas sanctionner » portée par journal + patterns
- Conventions anti-conflit pour agents IA
- Alignement fort PRD ↔ structure

**Areas for Future Enhancement :**

- SSO ENT, Redis, e2e, chiffrement applicatif champs

### Implementation Handoff

**AI Agent Guidelines :**

- Suivre ce document comme source de vérité
- Régénérer `shared-types` après chaque changement API
- Respecter isolation `teacher_id` et patterns § Implementation Patterns

**First Implementation Priority :**

```bash
# Story 0 — scaffold monorepo (voir § Starter Template Evaluation)
pnpm create vite@latest apps/web-prof -- --template react-ts
pnpm create vite@latest apps/web-eleve -- --template react-ts
uv init apps/api --package && uv add fastapi uvicorn[standard] sqlalchemy alembic pydantic-settings
docker compose up -d postgres
```
