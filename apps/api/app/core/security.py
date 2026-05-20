"""Sécurité — hachage bcrypt + jetons JWT.

Story 1.3 : helpers ``hash_password`` / ``verify_password`` (bcrypt via passlib).
Story 1.4 : génération et décodage des JWT (HS256) pour l'authentification
enseignant (access token court + refresh token cookie httpOnly).

Conformité :
- Algorithme bcrypt — architecture.md#Authentication & Security.
- Algorithme JWT HS256 — architecture.md#Authentication & Security ; durée
  d'expiration côté ``settings`` (``ACCESS_TOKEN_EXPIRE_MINUTES`` /
  ``REFRESH_TOKEN_EXPIRE_DAYS``).
- NFR-8 : ne JAMAIS logger les mots de passe, hashes ou tokens.

Notes d'implémentation :
- ``settings`` est importé localement dans chaque fonction JWT afin d'éviter
  toute dépendance circulaire (``app.core.config`` reste libre de ré-importer
  ``security``). Le coût additionnel d'import est négligeable (module Python
  mis en cache après le premier accès).
- ``decode_token`` retourne ``None`` quand le token est invalide ou expiré
  (jamais d'exception levée) : c'est la dépendance ``get_current_teacher``
  qui décide du code HTTP — cf. architecture du module ``core/dependencies``.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

ALGORITHM = "HS256"

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Retourne le hash bcrypt du mot de passe en clair.

    Le sel est généré automatiquement par passlib.
    """
    hashed: str = _pwd_context.hash(password)
    return hashed


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie qu'un mot de passe en clair correspond au hash bcrypt.

    Retourne ``False`` silencieusement si le hash stocké est mal formé
    (utile pour le pattern timing-constant de ``AuthService.login_teacher``
    qui appelle ``verify_password`` même quand le compte n'existe pas).
    """
    try:
        ok: bool = _pwd_context.verify(plain_password, hashed_password)
    except (ValueError, TypeError):
        return False
    return ok


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    """Crée un JWT access token signé HS256.

    Le payload reçu (``data``) est copié puis enrichi du champ ``exp``
    (timestamp UNIX d'expiration). La durée par défaut vient des settings
    (``ACCESS_TOKEN_EXPIRE_MINUTES``).
    """
    from app.core.config import settings

    to_encode = data.copy()
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire
    encoded: str = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded


def create_refresh_token(data: dict[str, Any]) -> str:
    """Crée un JWT refresh token signé HS256 (TTL ``REFRESH_TOKEN_EXPIRE_DAYS``)."""
    from app.core.config import settings

    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode["exp"] = expire
    encoded: str = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded


def decode_token(token: str) -> dict[str, Any] | None:
    """Décode et valide un JWT (signature + ``exp``).

    Retourne le payload ``dict`` si valide, ``None`` sinon (token invalide,
    signature incorrecte, expiré, malformé…). Aucune exception n'est propagée :
    c'est l'appelant (dépendance d'authentification) qui décide du code HTTP.
    """
    from app.core.config import settings

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
    if not isinstance(payload, dict):
        return None
    return payload
