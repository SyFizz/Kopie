# Story 1.4 : Connexion enseignant et gestion de session JWT

Status: review

<!-- Note: Validation optionnelle. Exécuter validate-create-story pour contrôle qualité avant dev-story. -->

## Story

As an **enseignant**,
I want **me connecter avec mon email et mot de passe et rester authentifié jusqu'à expiration ou déconnexion**,
So that **j'accède à mon espace sans me reconnecter à chaque action et mes données restent protégées**.

## Acceptance Criteria

1. **Given** un compte enseignant actif (`status: active`)
   **When** je soumets `POST /api/v1/auth/login` avec email et mot de passe corrects
   **Then** l'API retourne HTTP 200 avec `{ "access_token": "...", "token_type": "bearer" }`
   **And** un cookie `httpOnly` `Secure` `SameSite=Strict` nommé `refresh_token` est posé (TTL 7 jours)
   **And** l'access token est un JWT signé HS256 contenant `sub` (UUID enseignant) et `exp`

2. **Given** un compte enseignant avec `status: pending` (email non confirmé)
   **When** je tente de me connecter
   **Then** l'API retourne HTTP 403 avec `{ "error": { "code": "ACCOUNT_NOT_ACTIVE", "message": "..." } }`

3. **Given** des credentials incorrects (email inexistant ou mot de passe erroné)
   **When** je soumets `POST /api/v1/auth/login`
   **Then** l'API retourne HTTP 401 avec `{ "error": { "code": "INVALID_CREDENTIALS", "message": "..." } }`
   **And** le message est identique pour email inconnu et mot de passe erroné (pas d'énumération d'utilisateurs)

4. **Given** un enseignant connecté avec un access token expiré
   **When** il appelle `POST /api/v1/auth/refresh` avec le cookie `refresh_token` valide
   **Then** l'API retourne HTTP 200 avec un nouveau `access_token`
   **And** le cookie `refresh_token` est renouvelé (rotation — nouveau token, TTL réinitialisé)

5. **Given** un cookie `refresh_token` invalide ou expiré
   **When** j'appelle `POST /api/v1/auth/refresh`
   **Then** l'API retourne HTTP 401 avec `{ "error": { "code": "INVALID_REFRESH_TOKEN", "message": "..." } }`

6. **Given** un enseignant connecté
   **When** il appelle `POST /api/v1/auth/logout`
   **Then** l'API retourne HTTP 200
   **And** le cookie `refresh_token` est supprimé (Max-Age=0)
   **And** l'access token en mémoire côté client est effacé

7. **Given** une route protégée enseignant (ex. `GET /api/v1/teachers/me`)
   **When** un client appelle sans `Authorization: Bearer {token}` valide
   **Then** l'API retourne HTTP 401 avec `{ "error": { "code": "UNAUTHORIZED", "message": "..." } }`
   **And** la dépendance `get_current_teacher` est utilisée sur toutes les routes nécessitant auth

8. **Given** un enseignant authentifié
   **When** il appelle `GET /api/v1/teachers/me`
   **Then** l'API retourne HTTP 200 avec le schéma `Teacher` (id, email, display_name, status, created_at, updated_at)

9. **Given** le formulaire de connexion sur `apps/web-prof`
   **When** l'enseignant saisit email et mot de passe corrects et soumet
   **Then** le front stocke l'access token **en mémoire** (React Context — jamais localStorage ni sessionStorage)
   **And** le front est redirigé vers le tableau de bord (`/dashboard`)
   **And** le bouton « Se connecter » est désactivé pendant la soumission (loading state)

10. **Given** slowapi déjà configuré (Story 1.3)
    **When** des requêtes excessives ciblent `/api/v1/auth/login` ou `/api/v1/auth/refresh`
    **Then** slowapi applique le rate limit configuré par `RATE_LIMIT_AUTH` (défaut `10/minute`) et renvoie HTTP 429
    **And** le contrat OpenAPI est mis à jour avec les nouvelles routes avant l'implémentation backend

## Tasks / Subtasks

- [x] Tâche 1 — Enrichir `contracts/openapi.yaml` avec les nouvelles routes et schémas (AC: 10 → prérequis)
  - [x] Bump version `"0.2.0"` → `"0.3.0"` dans le YAML et dans `app = FastAPI(version="0.3.0")`
  - [x] Ajouter le schéma `LoginRequest` (`email: EmailStr`, `password: str`)
  - [x] Ajouter le schéma `LoginResponse` (`access_token: str`, `token_type: "bearer"`)
  - [x] Documenter `POST /api/v1/auth/login` (200 LoginResponse, 401 Error, 403 Error, 422 Error, 429 Error)
  - [x] Documenter `POST /api/v1/auth/refresh` (200 LoginResponse, 401 Error, 429 Error) — note : le refresh_token voyage via cookie httpOnly (non documenté dans le body)
  - [x] Documenter `POST /api/v1/auth/logout` (200 `{ "message": string }`)
  - [x] Documenter `GET /api/v1/teachers/me` (200 Teacher, 401 Error) — avec `securityScheme: BearerAuth`
  - [x] Ajouter la section `security` globale et le schéma `BearerAuth` dans `components/securitySchemes`
  - [x] Valider avec `pnpm --package=@redocly/cli dlx redocly lint contracts/openapi.yaml`
  - [x] Régénérer `pnpm gen:types` et committer `packages/shared-types/src/api.ts`

- [x] Tâche 2 — Fonctions JWT dans `apps/api/app/core/security.py` (AC: 1, 4, 7)
  - [x] Importer `from jose import JWTError, jwt` (python-jose déjà installé)
  - [x] Constante `ALGORITHM = "HS256"`
  - [x] Fonction `create_access_token(data: dict, expires_delta: timedelta | None = None) -> str`
  - [x] Fonction `create_refresh_token(data: dict) -> str` (TTL = `REFRESH_TOKEN_EXPIRE_DAYS` jours)
  - [x] Fonction `decode_token(token: str) -> dict | None` — retourne None si invalide/expiré, sans lever d'exception

- [x] Tâche 3 — Schémas Pydantic (AC: 1, 2, 3, 4)
  - [x] Ajouter dans `apps/api/app/schemas/teacher.py` : `LoginRequest` (`email: EmailStr`, `password: str`)
  - [x] Ajouter `LoginResponse` (`access_token: str`, `token_type: str = "bearer"`)

- [x] Tâche 4 — Méthode `login_teacher` dans `apps/api/app/services/auth_service.py` (AC: 1, 2, 3)
  - [x] `login_teacher(email: str, password: str) -> Teacher`
  - [x] Normalisation email en minuscules
  - [x] Lookup par email → None → HTTPException 401 `INVALID_CREDENTIALS`
  - [x] `verify_password(password, teacher.password_hash)` → False → HTTPException 401 `INVALID_CREDENTIALS`
  - [x] `teacher.status != "active"` → HTTPException 403 `ACCOUNT_NOT_ACTIVE`
  - [x] ⚠️ Vérifier le statut APRÈS vérification du mot de passe pour éviter l'énumération (même comportement)
  - [x] Retourner le `Teacher`

- [x] Tâche 5 — Dépendance `get_current_teacher` dans `apps/api/app/core/dependencies.py` (NEW) (AC: 7)
  - [x] Extraire le Bearer token de `Authorization` header
  - [x] `decode_token(token)` → payload
  - [x] Récupérer `teacher_id = payload.get("sub")` → lookup via `TeacherRepository`
  - [x] Si absent, invalide ou teacher non trouvé → HTTPException 401 `UNAUTHORIZED`
  - [x] Retourner le `Teacher` courant (utilisé par toutes les routes protégées)
  - [x] Type: `CurrentTeacher = Annotated[Teacher, Depends(get_current_teacher)]`

- [x] Tâche 6 — Nouveaux endpoints dans `apps/api/app/api/v1/endpoints/auth.py` (AC: 1–8, 10)
  - [x] `POST /auth/login` — rate-limité — appel `AuthService.login_teacher` → génère access + refresh token → pose cookie httpOnly
  - [x] `POST /auth/refresh` — rate-limité — lit cookie `refresh_token` → valide JWT → génère nouveaux tokens (rotation)
  - [x] `POST /auth/logout` — supprime cookie (Max-Age=0, même path/domain) → retourne 200 `{ "message": "Déconnecté." }`
  - [x] Paramètres cookie : `httponly=True`, `secure=True` (prod) / `False` (dev via settings), `samesite="strict"`, `max_age=REFRESH_TOKEN_EXPIRE_DAYS*86400`, `path="/api/v1/auth"`

- [x] Tâche 7 — Endpoint `GET /teachers/me` dans `apps/api/app/api/v1/endpoints/teachers.py` (NEW) (AC: 8)
  - [x] Créer `apps/api/app/api/v1/endpoints/teachers.py`
  - [x] `GET /teachers/me` protégé par `get_current_teacher` — retourne `TeacherPublic`
  - [x] Inclure le router dans `apps/api/app/api/v1/router.py`

- [x] Tâche 8 — AuthContext React dans `apps/web-prof/src/features/auth/AuthContext.tsx` (NEW) (AC: 9)
  - [x] `AuthProvider` avec état `accessToken: string | null` en mémoire
  - [x] `useAuth()` hook : `{ accessToken, setAccessToken, logout }`
  - [x] `logout()` appelle `POST /api/v1/auth/logout` + réinitialise l'état local
  - [x] Brancher dans `apps/web-prof/src/main.tsx` autour de `<App />`

- [x] Tâche 9 — Page de connexion dans `apps/web-prof/src/features/auth/LoginPage.tsx` (NEW) (AC: 9)
  - [x] Formulaire React Hook Form + résolveur Zod (email format, password non vide)
  - [x] Appel API via `loginTeacher()` dans `features/auth/api.ts`
  - [x] En cas de succès : stocker `access_token` dans `AuthContext` → redirection `useNavigate("/dashboard")`
  - [x] Erreurs 401 (credentials invalides) et 403 (compte non actif) mappées en messages français inline
  - [x] Loading state sur le bouton pendant `isSubmitting`
  - [x] Route `/login` ajoutée dans `apps/web-prof/src/App.tsx`
  - [x] Lien « S'inscrire » vers `/register` + lien « Mot de passe oublié ? » (placeholder MVP)

- [x] Tâche 10 — Page tableau de bord placeholder dans `apps/web-prof/src/features/dashboard/DashboardPage.tsx` (NEW)
  - [x] Route `/dashboard` protégée : redirige vers `/login` si pas d'`accessToken` dans `AuthContext`
  - [x] Affiche « Bonjour, {email} » + bouton « Se déconnecter » fonctionnel
  - [x] `PrivateRoute` wrapper réutilisable dans `App.tsx`

- [x] Tâche 11 — Mise à jour `apps/web-prof/src/features/auth/api.ts` (AC: 9)
  - [x] Ajouter `loginTeacher(data: { email, password }) → Promise<{ access_token: string }>`
  - [x] Gestion des erreurs 401/403/429/network identique au pattern de `registerTeacher`

- [x] Tâche 12 — Tests pytest (AC: 1–8, 10)
  - [x] Créer `apps/api/tests/test_auth_login.py` — ≥ 12 tests :
    - [x] `test_login_success` : 200 + access_token JWT valide + cookie refresh_token posé
    - [x] `test_login_inactive_account_returns_403` : compte pending → 403 `ACCOUNT_NOT_ACTIVE`
    - [x] `test_login_wrong_password_returns_401` : bon email, mauvais mdp → 401 `INVALID_CREDENTIALS`
    - [x] `test_login_unknown_email_returns_401` : email inexistant → 401 `INVALID_CREDENTIALS`
    - [x] `test_login_rate_limit` : 11ème appel → 429 `RATE_LIMIT_EXCEEDED`
    - [x] `test_refresh_success` : cookie refresh valide → 200 + nouveau access_token + cookie renouvelé
    - [x] `test_refresh_invalid_cookie_returns_401` : cookie absent ou corrompu → 401 `INVALID_REFRESH_TOKEN`
    - [x] `test_refresh_expired_cookie_returns_401` : exp forcée dans le passé → 401 `INVALID_REFRESH_TOKEN`
    - [x] `test_logout_clears_cookie` : 200 + cookie Max-Age=0
    - [x] `test_get_me_success` : Bearer valide → 200 + schéma Teacher complet
    - [x] `test_get_me_no_token_returns_401` : sans header → 401 `UNAUTHORIZED`
    - [x] `test_get_me_invalid_token_returns_401` : token malformé → 401 `UNAUTHORIZED`

- [x] Tâche 13 — Vérifications finales (AC: 1–10)
  - [x] `uv run ruff check .` (apps/api) → 0 erreur
  - [x] `uv run mypy app` (apps/api) → 0 erreur strict
  - [x] `uv run pytest -q` → 100 % pass (existants + nouveaux)
  - [x] `pnpm gen:types` → 0 erreur, idempotent
  - [x] `pnpm --filter web-prof build` → 0 erreur TypeScript
  - [x] `pnpm --filter web-prof test` → tous passent
  - [x] `pnpm --filter web-prof lint` → 0 erreur ESLint
  - [x] `pnpm --filter web-eleve test` + `build` → toujours verts (non-régression)
  - [x] `redocly lint contracts/openapi.yaml` → valid
  - [x] `docker compose config` → valid

## Dev Notes

### État du dépôt après Story 1.3

**Ce qui existe et sera modifié :**

| Fichier | État actuel | Ce que Story 1.4 fait |
|---------|------------|----------------------|
| `apps/api/app/core/security.py` | `hash_password` + `verify_password` (bcrypt) | **Étendre** avec fonctions JWT (`create_access_token`, `create_refresh_token`, `decode_token`) |
| `apps/api/app/core/config.py` | `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES=15`, `REFRESH_TOKEN_EXPIRE_DAYS=7` déjà présents | Ajouter `COOKIE_SECURE: bool = True` (False en dev) |
| `apps/api/app/services/auth_service.py` | `register_teacher` + `verify_email` | **Ajouter** `login_teacher` |
| `apps/api/app/api/v1/endpoints/auth.py` | `/register` + `/verify-email` | **Étendre** : `login`, `refresh`, `logout` |
| `apps/api/app/api/v1/router.py` | inclut `auth` + `health` | **Ajouter** le router `teachers` |
| `apps/api/app/schemas/teacher.py` | `RegisterRequest`, `TeacherCreated`, `TeacherPublic`, `VerifyEmailResponse` | **Ajouter** `LoginRequest`, `LoginResponse` |
| `apps/api/app/main.py` | version `0.2.0`, middlewares + handlers | Bump version → `0.3.0` |
| `contracts/openapi.yaml` | version `0.2.0`, routes register + verify-email | **Étendre** : login, refresh, logout, teachers/me |
| `apps/web-prof/src/App.tsx` | routes `/`, `/register`, `/verify-email` | **Étendre** : `/login`, `/dashboard`, `PrivateRoute` |
| `apps/web-prof/src/features/auth/api.ts` | `registerTeacher` | **Ajouter** `loginTeacher`, `logoutTeacher` |
| `apps/web-prof/src/main.tsx` | `BrowserRouter` + `<App />` | **Étendre** : wrapper `<AuthProvider>` |

**Ce qui n'existe PAS encore (à créer) :**

- `apps/api/app/core/dependencies.py` — `get_current_teacher` dependency
- `apps/api/app/api/v1/endpoints/teachers.py` — `GET /teachers/me`
- `apps/web-prof/src/features/auth/AuthContext.tsx` — access token en mémoire
- `apps/web-prof/src/features/auth/LoginPage.tsx` — formulaire connexion
- `apps/web-prof/src/features/dashboard/DashboardPage.tsx` — placeholder post-login

### Stack et librairies EXACTES

| Composant | Version / Statut | Note |
|-----------|-----------------|------|
| `python-jose[cryptography]` | déjà installé (Story 1.1) | `from jose import JWTError, jwt` |
| `passlib[bcrypt]` | déjà installé (Story 1.3) | `verify_password` déjà dans `security.py` |
| `fastapi` | 0.136.1 (figée) | Cookie via `response.set_cookie(...)` |
| `slowapi` | déjà installé (Story 1.3) | `@limiter.limit(settings.RATE_LIMIT_AUTH)` |
| React Hook Form | déjà installé (Story 1.3) | `useForm` + `zodResolver` |
| `react-router-dom` | déjà installé (Story 1.3) | `useNavigate`, `Navigate` |
| Zod | déjà installé (Story 1.3) | Validation formulaire |

> ⚠️ `python-jose` est importé comme `from jose import JWTError, jwt` — ne pas confondre avec `python_jose` ou `jwt` direct.

### Implémentation JWT dans `security.py`

```python
# apps/api/app/core/security.py — ajouts à faire APRÈS les fonctions bcrypt existantes
from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt

ALGORITHM = "HS256"


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    from app.core.config import settings

    to_encode = data.copy()
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire
    encoded: str = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded


def create_refresh_token(data: dict) -> str:
    from app.core.config import settings

    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode["exp"] = expire
    encoded: str = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded


def decode_token(token: str) -> dict | None:
    from app.core.config import settings

    try:
        payload: dict = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
```

> ⚠️ Import circulaire à éviter : importer `settings` à l'intérieur de la fonction, pas au niveau module, si `config.py` importe `security.py`. Alternativement, passer `secret_key` en paramètre.
> ⚠️ Le `sub` dans le payload doit être `str(teacher.id)` (UUID → string) ; lors du décodage, le re-convertir en `uuid.UUID(payload["sub"])`.

### Pattern dépendance `get_current_teacher`

```python
# apps/api/app/core/dependencies.py (NOUVEAU)
from __future__ import annotations

import uuid
from typing import Annotated

import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.models.teacher import Teacher
from app.repositories.teacher_repository import TeacherRepository

logger = structlog.get_logger(__name__)

_bearer_scheme = HTTPBearer(auto_error=False)

_UNAUTHORIZED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail={"error": {"code": "UNAUTHORIZED", "message": "Authentification requise."}},
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_teacher(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)
    ],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Teacher:
    if credentials is None:
        raise _UNAUTHORIZED

    payload = decode_token(credentials.credentials)
    if payload is None:
        raise _UNAUTHORIZED

    sub = payload.get("sub")
    if sub is None:
        raise _UNAUTHORIZED

    try:
        teacher_id = uuid.UUID(sub)
    except ValueError:
        raise _UNAUTHORIZED

    repo = TeacherRepository(db)
    teacher = await repo.get_by_id(teacher_id)
    if teacher is None:
        raise _UNAUTHORIZED

    return teacher


CurrentTeacher = Annotated[Teacher, Depends(get_current_teacher)]
```

### Pattern endpoints login / refresh / logout

```python
# apps/api/app/api/v1/endpoints/auth.py — ajouts aux routes existantes

from fastapi import Cookie, Response

REFRESH_COOKIE_NAME = "refresh_token"
REFRESH_COOKIE_PATH = "/api/v1/auth"


@router.post("/login", response_model=LoginResponse, status_code=200)
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def login(
    request: Request,
    body: LoginRequest,
    response: Response,
    db: DbSession,
) -> LoginResponse:
    service = AuthService(db)
    teacher = await service.login_teacher(email=body.email, password=body.password)

    access_token = create_access_token({"sub": str(teacher.id)})
    refresh_token = create_refresh_token({"sub": str(teacher.id)})

    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="strict",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        path=REFRESH_COOKIE_PATH,
    )
    return LoginResponse(access_token=access_token, token_type="bearer")


@router.post("/refresh", response_model=LoginResponse, status_code=200)
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def refresh(
    request: Request,
    response: Response,
    db: DbSession,
    refresh_token_cookie: str | None = Cookie(default=None, alias=REFRESH_COOKIE_NAME),
) -> LoginResponse:
    _INVALID = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"error": {"code": "INVALID_REFRESH_TOKEN", "message": "Token de rafraîchissement invalide ou expiré."}},
    )
    if refresh_token_cookie is None:
        raise _INVALID

    payload = decode_token(refresh_token_cookie)
    if payload is None or "sub" not in payload:
        raise _INVALID

    # Rotation : vérifie que le teacher existe encore
    try:
        teacher_id = uuid.UUID(payload["sub"])
    except ValueError:
        raise _INVALID

    repo = TeacherRepository(db)
    teacher = await repo.get_by_id(teacher_id)
    if teacher is None or teacher.status != "active":
        raise _INVALID

    new_access = create_access_token({"sub": str(teacher.id)})
    new_refresh = create_refresh_token({"sub": str(teacher.id)})

    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=new_refresh,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="strict",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        path=REFRESH_COOKIE_PATH,
    )
    return LoginResponse(access_token=new_access, token_type="bearer")


@router.post("/logout", status_code=200)
async def logout(response: Response) -> dict[str, str]:
    response.delete_cookie(
        key=REFRESH_COOKIE_NAME,
        path=REFRESH_COOKIE_PATH,
        httponly=True,
        samesite="strict",
    )
    return {"message": "Déconnecté."}
```

> ⚠️ `Cookie(alias=REFRESH_COOKIE_NAME)` — FastAPI lit automatiquement les cookies HTTP via ce mécanisme. En tests, passer le cookie via `async_client.cookies[REFRESH_COOKIE_NAME] = "..."`.
> ⚠️ Le cookie `path="/api/v1/auth"` restreint son envoi automatique aux seules routes `/api/v1/auth/*` — c'est intentionnel pour limiter la surface d'exposition. Le front n'a pas à gérer ce cookie manuellement (httpOnly).
> ⚠️ `COOKIE_SECURE` doit être `False` en développement local (HTTP) et `True` en production (HTTPS). Ajouter dans `config.py` : `COOKIE_SECURE: bool = True` et le setter dans `.env` dev à `COOKIE_SECURE=false`.

### Pattern `AuthService.login_teacher`

```python
# apps/api/app/services/auth_service.py — méthode à ajouter

async def login_teacher(self, *, email: str, password: str) -> Teacher:
    """Authentifie un enseignant.

    Retourne le Teacher si credentials valides et compte actif.
    Lève HTTPException(401) pour credentials incorrects (message identique
    quel que soit le motif réel — pas d'énumération d'utilisateurs).
    Lève HTTPException(403) si le compte existe mais n'est pas actif.
    """
    _INVALID_CREDENTIALS = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "error": {
                "code": "INVALID_CREDENTIALS",
                "message": "Email ou mot de passe incorrect.",
            }
        },
    )

    normalized_email = email.lower().strip()
    teacher = await self._repo.get_by_email(normalized_email)

    if teacher is None:
        # Timing constant : éviter l'énumération via différence de temps
        # En vérifiant un hash fictif (même opération que verify_password)
        verify_password("placeholder", "$2b$12$invalidhashforthisdummy00000000000000")
        raise _INVALID_CREDENTIALS

    if not verify_password(password, teacher.password_hash):
        raise _INVALID_CREDENTIALS

    if teacher.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": {
                    "code": "ACCOUNT_NOT_ACTIVE",
                    "message": "Votre compte n'est pas encore activé. Vérifiez votre boîte mail.",
                }
            },
        )

    logger.info("auth.teacher_logged_in", teacher_id=str(teacher.id))
    return teacher
```

> ⚠️ **Timing attack** : appeler `verify_password` même quand le teacher est `None` (avec un hash bidon) pour que le temps de réponse soit constant. Sinon, un attaquant peut distinguer « email inconnu » (réponse rapide) de « mauvais mot de passe » (réponse bcrypt lente).
> ⚠️ **Ordre de vérification** : vérifier le mot de passe AVANT le statut, pour éviter l'énumération via le code d'erreur (401 vs 403). Un attaquant ne doit pas pouvoir déduire l'existence d'un compte non confirmé.

### AuthContext React (access token en mémoire)

```tsx
// apps/web-prof/src/features/auth/AuthContext.tsx
import { createContext, useCallback, useContext, useState } from 'react'

interface AuthContextValue {
  accessToken: string | null
  setAccessToken: (token: string | null) => void
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [accessToken, setAccessToken] = useState<string | null>(null)

  const logout = useCallback(async () => {
    try {
      await fetch(`${import.meta.env.VITE_API_URL}/api/v1/auth/logout`, {
        method: 'POST',
        credentials: 'include', // envoie le cookie httpOnly
      })
    } finally {
      setAccessToken(null)
    }
  }, [])

  return (
    <AuthContext.Provider value={{ accessToken, setAccessToken, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (ctx === null) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
```

> ⚠️ **Jamais** stocker l'access token dans `localStorage` ou `sessionStorage` — vulnérabilité XSS. Le token en mémoire (`useState`) est perdu à chaque refresh de page ; c'est intentionnel au MVP. La récupération silencieuse via `POST /api/v1/auth/refresh` (qui envoie automatiquement le cookie httpOnly) sera gérée ultérieurement en Story 1.5 ou via un `useEffect` à l'initialisation de l'`AuthProvider`.
> ⚠️ Le cookie `refresh_token` est `httpOnly` — il n'est PAS accessible depuis JavaScript. Il est envoyé automatiquement par le navigateur sur les requêtes `fetch` avec `credentials: 'include'`.

### Pattern PrivateRoute

```tsx
// apps/web-prof/src/App.tsx — ajouter
import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from './features/auth/AuthContext'

function PrivateRoute() {
  const { accessToken } = useAuth()
  return accessToken ? <Outlet /> : <Navigate to="/login" replace />
}

// Dans <Routes> :
// <Route element={<PrivateRoute />}>
//   <Route path="/dashboard" element={<DashboardPage />} />
// </Route>
```

### Pattern fixtures tests login

```python
# apps/api/tests/test_auth_login.py — helpers

import pytest_asyncio

@pytest_asyncio.fixture
async def active_teacher(db_session):
    """Crée un Teacher avec statut 'active' directement en DB (sans passer par l'inscription)."""
    from app.core.security import hash_password
    from app.repositories.teacher_repository import TeacherRepository

    repo = TeacherRepository(db_session)
    teacher = await repo.create(
        email="marie@example.com",
        password_hash=hash_password("motdepasse123456"),
        verification_token="unused",
        verification_token_expires_at=datetime.now(UTC) + timedelta(days=1),
    )
    teacher.status = "active"
    teacher.email_verification_token = None
    teacher.email_verification_token_expires_at = None
    await db_session.flush()
    await db_session.refresh(teacher)
    await db_session.commit()
    return teacher


async def test_login_success(async_client, active_teacher):
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "marie@example.com", "password": "motdepasse123456"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    # Vérifier que le cookie refresh est posé
    assert "refresh_token" in response.cookies


async def test_get_me_success(async_client, active_teacher):
    login_resp = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "marie@example.com", "password": "motdepasse123456"},
    )
    token = login_resp.json()["access_token"]
    me_resp = await async_client.get(
        "/api/v1/teachers/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "marie@example.com"
```

> ⚠️ Dans les tests pytest, `async_client` (via `ASGITransport` + `httpx.AsyncClient`) supporte les cookies — utiliser `async_client.cookies` ou vérifier `response.cookies` directement.
> ⚠️ Le cookie `secure=True` en tests doit être `False` (HTTP localhost) — vérifier que `COOKIE_SECURE` est `False` dans l'env de test. Utiliser `monkeypatch.setattr(settings, "COOKIE_SECURE", False)` ou passer `COOKIE_SECURE=false` dans l'env.

### Schémas Pydantic à ajouter

```python
# apps/api/app/schemas/teacher.py — ajouts

class LoginRequest(BaseModel):
    """Charge utile de ``POST /api/v1/auth/login``."""
    email: EmailStr = Field(..., description="Adresse email de l'enseignant.")
    password: str = Field(..., description="Mot de passe en clair.")


class LoginResponse(BaseModel):
    """Réponse de ``POST /api/v1/auth/login`` et ``POST /api/v1/auth/refresh``."""
    access_token: str
    token_type: str = "bearer"
```

### Contrat OpenAPI — schémas et routes à ajouter

```yaml
# À ajouter dans components/schemas :
LoginRequest:
  type: object
  required: [email, password]
  properties:
    email:
      type: string
      format: email
      example: "marie.dupont@academie-versailles.fr"
    password:
      type: string
      description: Mot de passe en clair (HTTPS obligatoire en prod)
      example: "motdepasse123456"

LoginResponse:
  type: object
  required: [access_token, token_type]
  properties:
    access_token:
      type: string
      description: JWT access token (court — défaut 15 min)
    token_type:
      type: string
      enum: [bearer]

# À ajouter dans components/securitySchemes :
BearerAuth:
  type: http
  scheme: bearer
  bearerFormat: JWT

# Routes à ajouter dans paths :
/api/v1/auth/login:
  post:
    operationId: loginTeacher
    summary: Connexion enseignant
    tags: [auth]
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/LoginRequest"
    responses:
      "200":
        description: Connexion réussie — access token retourné + cookie refresh posé
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/LoginResponse"
      "401":
        description: Credentials incorrects
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/Error"
      "403":
        description: Compte non actif (email non confirmé)
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/Error"
      "422":
        description: Données invalides
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

/api/v1/auth/refresh:
  post:
    operationId: refreshToken
    summary: Rafraîchissement du token d'accès
    description: |
      Le refresh_token voyage via cookie httpOnly (non visible dans le body).
      Le navigateur l'envoie automatiquement si credentials:include.
    tags: [auth]
    responses:
      "200":
        description: Nouveau access token + cookie refresh renouvelé (rotation)
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/LoginResponse"
      "401":
        description: Cookie refresh absent, invalide ou expiré
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

/api/v1/auth/logout:
  post:
    operationId: logoutTeacher
    summary: Déconnexion enseignant
    tags: [auth]
    responses:
      "200":
        description: Cookie refresh supprimé
        content:
          application/json:
            schema:
              type: object
              required: [message]
              properties:
                message:
                  type: string
                  example: "Déconnecté."

/api/v1/teachers/me:
  get:
    operationId: getCurrentTeacher
    summary: Profil de l'enseignant connecté
    tags: [teachers]
    security:
      - BearerAuth: []
    responses:
      "200":
        description: Profil enseignant complet
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/Teacher"
      "401":
        description: Token absent ou invalide
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/Error"
```

### Configuration `config.py` — ajout requis

```python
# Dans la classe Settings, ajouter :
COOKIE_SECURE: bool = True  # False en développement (HTTP), True en prod (HTTPS)
```

Et dans `.env` (dev local) :
```
COOKIE_SECURE=false
```

Et dans `.env.example` :
```
# Cookie sécurité (mettre à true en production avec HTTPS)
COOKIE_SECURE=false
```

### Règles d'architecture CRITIQUES à respecter (rappel + spécifique 1.4)

1. **Contract-first** : modifier `contracts/openapi.yaml` AVANT d'écrire le code backend.
2. **Régénérer `shared-types`** après chaque modification du YAML (`pnpm gen:types`).
3. **Logique métier dans `services/`**, jamais dans les endpoints.
4. **Repository layer** pour tout accès DB — `TeacherRepository` existant à réutiliser.
5. **Access token en mémoire uniquement** côté front — jamais `localStorage`/`sessionStorage`.
6. **httpOnly + Secure + SameSite=Strict** pour le cookie refresh.
7. **Timing constant** sur `login_teacher` pour éviter l'énumération d'emails.
8. **`decode_token` retourne `None`** (ne lève pas d'exception) — la dépendance `get_current_teacher` gère la 401.
9. **Logs structlog** : ne jamais logger de mot de passe, hash, ou token.
10. **`mypy strict`** : annoter tous les types, `str | None` pas `Optional[str]`.

### Anti-patterns à éviter absolument

| Anti-pattern | Correct |
|---|---|
| Stocker l'access token dans `localStorage` | `useState` dans `AuthContext` (mémoire) |
| Logger `password` ou `password_hash` | Ne jamais logger ces valeurs |
| Réponse différente pour email inexistant vs mauvais mdp | Même 401 `INVALID_CREDENTIALS` dans les deux cas |
| Oublier `verify_password` avec hash bidon quand teacher=None | Toujours payer le coût bcrypt pour timing constant |
| Cookie refresh sans `httpOnly`, `SameSite=Strict` | Attributs obligatoires (architecture § Auth) |
| Cookie refresh sans rotation | Renouveler à chaque `POST /auth/refresh` |
| `import jwt` direct (PyJWT) | `from jose import jwt` (python-jose) |
| `get_current_teacher` lève un `ValueError` au lieu de 401 | `try/except ValueError` autour de `uuid.UUID(sub)` |
| Route `/teachers/me` sans `CurrentTeacher` | Toutes routes protégées passent par la dépendance |
| `app.openapi_schema = None` pour reset en tests | Utiliser `app.openapi_schema = None` dans fixture post-test si besoin |

### Page de connexion — squelette

```tsx
// apps/web-prof/src/features/auth/LoginPage.tsx
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useAuth } from './AuthContext'
import { loginTeacher } from './api'

const loginSchema = z.object({
  email: z.string().email('Email invalide.'),
  password: z.string().min(1, 'Le mot de passe est requis.'),
})
type LoginFormData = z.infer<typeof loginSchema>

export function LoginPage() {
  const { setAccessToken } = useAuth()
  const navigate = useNavigate()
  const [serverError, setServerError] = useState<string | null>(null)
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  })

  const onSubmit = async (data: LoginFormData) => {
    setServerError(null)
    const result = await loginTeacher(data)
    if (result.ok) {
      setAccessToken(result.data.access_token)
      navigate('/dashboard', { replace: true })
      return
    }
    if (result.status === 401) {
      setServerError('Email ou mot de passe incorrect.')
    } else if (result.status === 403) {
      setServerError('Votre compte n\'est pas encore activé. Vérifiez votre boîte mail.')
    } else {
      setServerError('Une erreur est survenue. Veuillez réessayer.')
    }
  }

  return (
    <main>
      <h1>Connexion à votre espace enseignant</h1>
      <form onSubmit={handleSubmit(onSubmit)}>
        {/* Champs email, password, bouton submit avec isSubmitting */}
        {/* Lien « S'inscrire » vers /register */}
      </form>
      {serverError && <p role="alert">{serverError}</p>}
    </main>
  )
}
```

> ⚠️ `credentials: 'include'` sur tous les `fetch` vers l'API — obligatoire pour que le navigateur envoie le cookie `refresh_token` httpOnly.
> ⚠️ Respecter la charte UX-DR21 (vouvoiement) et UX-DR1 (design system Tailwind `theme-teacher`, primary `#2563eb`).

### Cibles de qualité attendues

| Vérification | Critère de succès |
|---|---|
| `uv run ruff check .` | 0 erreur |
| `uv run mypy app` | 0 erreur strict |
| `uv run pytest -q` | 100 % pass (existants + ≥ 12 nouveaux) |
| `pnpm gen:types` | 0 erreur, idempotent |
| `pnpm --filter web-prof build` | 0 erreur TypeScript |
| `pnpm --filter web-prof test` | tous passent |
| CI `verify-shared-types` | verte |

### Références

- [Source: epics.md#Story 1.4] — AC officiels + user story
- [Source: epics.md#Additional Requirements] — Auth enseignant : JWT access (court) + refresh cookie httpOnly Secure SameSite=Strict
- [Source: epics.md#FR-2] — Connexion + session JWT ; 401 si non authentifié ; déconnexion invalide le jeton côté client
- [Source: epics.md#FR-43] — Rate limiting sur `/auth/*`
- [Source: architecture.md#Authentication & Security] — Stockage client : access en mémoire, refresh httpOnly cookie `prof.kopie.cc`
- [Source: architecture.md#Process Patterns] — Auth prof : login → access + cookie refresh ; 401 → refresh → retry une fois
- [Source: architecture.md#Enforcement Guidelines] — isolation teacher_id, logique dans services/, shared-types régénéré
- [Source: 1-3-inscription-enseignant-avec-validation-email.md#Dev Notes] — Stack exacte, python-jose installé, conftest pattern, slowapi reset, contract-first workflow
- [Source: 1-3-inscription-enseignant-avec-validation-email.md#Dev Agent Record] — `Uuid(as_uuid=True)` dialect-agnostic, bcrypt<5.0 pin, format Error handlers, pattern Annotated[AsyncSession, Depends(get_db)]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.7 (via Cursor — workflow `bmad-dev-story`).

### Completion Notes List

- **Contrat OpenAPI 0.3.0** — Quatre routes ajoutées (`POST /auth/login`, `POST /auth/refresh`, `POST /auth/logout`, `GET /teachers/me`), schémas `LoginRequest` / `LoginResponse` et `securityScheme: BearerAuth`. `redocly lint` passe et `pnpm gen:types` est idempotent.
- **JWT HS256** — `create_access_token`, `create_refresh_token` (TTL `REFRESH_TOKEN_EXPIRE_DAYS`), `decode_token` (retourne `None` plutôt que de lever). `settings` est importé localement dans chaque fonction JWT pour éviter tout import circulaire avec `config.py`.
- **`verify_password` durci** — Le hash bidon utilisé pour le timing-constant peut être malformé sur certaines plateformes ; `verify_password` retourne désormais `False` proprement (sans propager `ValueError`/`TypeError`) si le hash stocké n'est pas un bcrypt valide.
- **AuthService.login_teacher** — Pattern timing-constant via un hash bcrypt « bidon » (`$2b$12$…`) quand l'email est inconnu, vérification du mot de passe AVANT le statut pour ne pas distinguer 401/403 selon l'existence d'un compte `pending`. Logs structlog (jamais de mot de passe ni de hash).
- **`get_current_teacher`** — Dépendance unique pour toutes les routes protégées. `HTTPBearer(auto_error=False)` → 401 standardisée même quand l'en-tête est absent (sinon FastAPI émettait un 403 hors format `Error`). UUID invalide → 401 (try/except sur `uuid.UUID(sub)`).
- **Endpoints `auth.py`** — Cookie `refresh_token` posé/renouvelé par un helper interne (`_set_refresh_cookie`) pour garantir des attributs identiques côté login/refresh (`httponly`, `samesite=strict`, `secure=COOKIE_SECURE`, `path=/api/v1/auth`, `max_age`). Rotation systématique au refresh. `logout` est idempotent.
- **`GET /teachers/me`** — Sérialise `created_at` / `updated_at` au format ISO 8601 (string) pour respecter le contrat OpenAPI (`format: date-time`).
- **`COOKIE_SECURE`** — Setting ajouté (`True` par défaut, surchargeable via `.env`). `.env.example` documenté + `.env` local à `false`. La fixture pytest `conftest.py` force `COOKIE_SECURE=False` pendant les tests (autoresent : sinon `httpx` n'envoie pas le cookie sur `http://test`).
- **Tests pytest** — 19 nouveaux tests (`test_auth_login.py`) couvrent AC1–8 et AC10 incluant : rotation cookie, expiration `exp` forcée, schéma JWT cassé, sub non-UUID, schéma `Basic` au lieu de `Bearer`, rate-limit (11ᵉ appel → 429), idempotence du logout, identité du code d'erreur 401 entre email inconnu et mot de passe erroné. Suite complète : 40 passed, 0 failed, `ruff check` + `mypy --strict` verts.
- **Front web-prof** — `AuthContext` co-localise `AuthProvider` et `useAuth()` (un seul point d'entrée) et accepte un `initialAccessToken` pour les tests + future rehydratation silencieuse (story 1.5). `LoginPage` mappe explicitement 401/403/422/429/réseau en messages français. `DashboardPage` placeholder avec bouton de déconnexion. `PrivateRoute` exposé par `App.tsx` pour réutilisation.
- **Tests Vitest** — `LoginPage.test.tsx` (8 tests : validation locale, succès, 401, 403, 429, erreur réseau, credentials:include) + `AuthContext.test.tsx` (8 tests : hook hors provider, logout résilient au réseau, PrivateRoute redirige / passe). `App.test.tsx` mis à jour avec `AuthProvider` autour de chaque rendu. Total : **30 tests passed** (web-prof), web-eleve non régressé (3/3).
- **Build / lint** — `pnpm --filter web-prof build` OK (TS strict, vite). `pnpm --filter web-prof lint` OK (un seul `eslint-disable-next-line` ciblé sur le hook `useAuth` pour conserver le pattern Context React standard). `docker compose config` valide.

### File List

**Fichiers à créer**
- `apps/api/app/core/dependencies.py`
- `apps/api/app/api/v1/endpoints/teachers.py`
- `apps/api/tests/test_auth_login.py`
- `apps/web-prof/src/features/auth/AuthContext.tsx`
- `apps/web-prof/src/features/auth/LoginPage.tsx`
- `apps/web-prof/src/features/dashboard/DashboardPage.tsx`

**Fichiers à modifier**
- `contracts/openapi.yaml` — bump 0.2.0 → 0.3.0 ; nouvelles routes (login, refresh, logout, teachers/me) + schémas (LoginRequest, LoginResponse) + securitySchemes (BearerAuth)
- `packages/shared-types/src/api.ts` — régénéré
- `apps/api/app/core/security.py` — ajout fonctions JWT (`create_access_token`, `create_refresh_token`, `decode_token`)
- `apps/api/app/core/config.py` — ajout `COOKIE_SECURE: bool = True`
- `apps/api/app/schemas/teacher.py` — ajout `LoginRequest`, `LoginResponse`
- `apps/api/app/services/auth_service.py` — ajout `login_teacher`
- `apps/api/app/api/v1/endpoints/auth.py` — ajout routes login, refresh, logout
- `apps/api/app/api/v1/router.py` — inclure router `teachers`
- `apps/api/app/main.py` — bump version → `0.3.0`
- `.env.example` — ajout `COOKIE_SECURE=false`
- `apps/web-prof/src/App.tsx` — route `/login`, `PrivateRoute`, route `/dashboard`
- `apps/web-prof/src/main.tsx` — wrapper `<AuthProvider>`
- `apps/web-prof/src/features/auth/api.ts` — ajout `loginTeacher`, `logoutTeacher`

## Change Log

| Date | Auteur | Description |
|------|--------|-------------|
| 2026-05-20 | BMad (create-story) | Création de la story 1.4 — contexte exhaustif pour l'agent de développement. Status → ready-for-dev. |
| 2026-05-20 | BMad (dev-story) | Implémentation complète : contrat OpenAPI 0.3.0, JWT HS256, login/refresh/logout/me, AuthContext + LoginPage + DashboardPage + PrivateRoute. 40 tests pytest (ruff/mypy strict OK) + 30 tests Vitest + non-régression web-eleve. Status → review. |
