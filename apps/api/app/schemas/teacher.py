"""Schémas Pydantic pour les comptes enseignant.

Story 1.3 — Inscription enseignant avec validation email.

Ces schémas reflètent EXACTEMENT le contrat ``contracts/openapi.yaml``
(source de vérité unique). En cas de divergence, le YAML l'emporte ;
ces classes ne sont utilisées que pour valider les entrées/sorties Python.
"""
from __future__ import annotations

import uuid

from pydantic import BaseModel, EmailStr, Field, field_validator

PASSWORD_MIN_LENGTH = 12
# bcrypt tronque silencieusement les mots de passe au-delà de 72 octets UTF-8 :
# nous rejetons explicitement les entrées plus longues afin d'éviter toute
# divergence ultérieure entre la chaîne enregistrée et celle utilisée pour
# vérifier le mot de passe (cf. ``passlib.handlers.bcrypt``).
PASSWORD_MAX_BYTES = 72


class RegisterRequest(BaseModel):
    """Charge utile de ``POST /api/v1/auth/register``."""

    email: EmailStr = Field(..., description="Adresse email de l'enseignant.")
    password: str = Field(
        ...,
        min_length=PASSWORD_MIN_LENGTH,
        description=(
            "Mot de passe en clair (12 caractères minimum, 72 octets UTF-8 maximum)."
        ),
    )

    @field_validator("password")
    @classmethod
    def password_within_bounds(cls, v: str) -> str:
        if len(v) < PASSWORD_MIN_LENGTH:
            raise ValueError(
                "Le mot de passe doit comporter au moins 12 caractères."
            )
        if len(v.encode("utf-8")) > PASSWORD_MAX_BYTES:
            raise ValueError(
                "Le mot de passe ne doit pas dépasser 72 octets UTF-8."
            )
        return v


class TeacherCreated(BaseModel):
    """Réponse de ``POST /api/v1/auth/register`` (statut HTTP 201)."""

    id: uuid.UUID
    email: EmailStr
    status: str = Field(
        default="pending",
        description="Toujours `pending` à l'inscription.",
    )


class TeacherPublic(BaseModel):
    """Représentation publique complète d'un enseignant.

    Réutilisable par les stories ultérieures (1.4 login, 1.5 profil).
    """

    id: uuid.UUID
    email: EmailStr
    display_name: str
    status: str
    created_at: str
    updated_at: str


class VerifyEmailResponse(BaseModel):
    """Réponse de ``GET /api/v1/auth/verify-email`` (HTTP 200)."""

    message: str


class LoginRequest(BaseModel):
    """Charge utile de ``POST /api/v1/auth/login`` — Story 1.4.

    Aucune contrainte de longueur côté login (la politique 12 octets+ ne
    s'applique qu'à l'inscription) : on accepte n'importe quel mot de passe
    fourni et on le compare au hash en base. La sortie est donc symétrique
    pour ``email`` invalide et mot de passe vide → 422 ``VALIDATION_ERROR``.
    """

    email: EmailStr = Field(..., description="Adresse email de l'enseignant.")
    password: str = Field(
        ...,
        min_length=1,
        description="Mot de passe en clair (HTTPS obligatoire en production).",
    )


class LoginResponse(BaseModel):
    """Réponse de ``POST /api/v1/auth/login`` et ``POST /api/v1/auth/refresh``.

    Le ``refresh_token`` est servi via cookie httpOnly Secure SameSite=Strict
    et n'apparaît jamais dans ce schéma JSON (cf. ``contracts/openapi.yaml``).
    """

    access_token: str
    token_type: str = Field(
        default="bearer",
        description="Toujours `bearer` (RFC 6750).",
    )
