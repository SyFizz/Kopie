"""Schémas Pydantic pour les comptes enseignant.

Story 1.3 — Inscription enseignant avec validation email.

Ces schémas reflètent EXACTEMENT le contrat ``contracts/openapi.yaml``
(source de vérité unique). En cas de divergence, le YAML l'emporte ;
ces classes ne sont utilisées que pour valider les entrées/sorties Python.
"""
from __future__ import annotations

import uuid

from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    """Charge utile de ``POST /api/v1/auth/register``."""

    email: EmailStr = Field(..., description="Adresse email de l'enseignant.")
    password: str = Field(
        ...,
        min_length=12,
        max_length=200,
        description="Mot de passe en clair (12 caractères minimum).",
    )

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 12:
            raise ValueError(
                "Le mot de passe doit comporter au moins 12 caractères."
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
