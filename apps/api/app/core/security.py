"""Sécurité — hachage de mots de passe (bcrypt via passlib).

Story 1.3 : helpers ``hash_password`` / ``verify_password``.
Story 1.4 (à venir) : ajoutera ici la génération / vérification des JWT.

Conformité :
- Algorithme : ``bcrypt`` (architecture.md#Authentication & Security).
- NFR-8 : ne JAMAIS logger les mots de passe ni les hashes.
"""
from __future__ import annotations

from passlib.context import CryptContext

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Retourne le hash bcrypt du mot de passe en clair.

    Le sel est généré automatiquement par passlib.
    """
    hashed: str = _pwd_context.hash(password)
    return hashed


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie qu'un mot de passe en clair correspond au hash bcrypt."""
    ok: bool = _pwd_context.verify(plain_password, hashed_password)
    return ok
