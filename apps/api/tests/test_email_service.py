"""Tests du service email — NFR-8 (pas de fuite de token dans les logs)."""
from __future__ import annotations

import logging

import pytest

from app.services import email_service


def test_send_verification_email_degraded_mode_does_not_log_token(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Mode dégradé : le token et l'URL ne doivent JAMAIS apparaître en clair.

    Couvre la review finding #3 : on ne logge qu'un préfixe court (non
    réversible) et l'email destinataire.
    """
    monkeypatch.setattr(email_service.settings, "SMTP_HOST", "")

    token = "very-secret-token-1234567890abcdef-do-not-log"
    email = "victime@example.fr"

    with caplog.at_level(logging.WARNING):
        email_service.send_verification_email(email, token)

    full_logs = "\n".join(record.getMessage() for record in caplog.records)
    full_logs += "\n".join(
        str(getattr(record, attr, ""))
        for record in caplog.records
        for attr in ("verification_url", "token", "args")
    )

    assert token not in full_logs, (
        "Le token complet ne doit jamais apparaître dans les logs."
    )
    assert "/api/v1/auth/verify-email?token=" not in full_logs, (
        "L'URL de vérification (qui embarque le token) ne doit pas être loggée."
    )


def test_build_verification_url_uses_app_base_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        email_service.settings, "APP_BASE_URL", "https://api.kopie.cc/"
    )
    url = email_service.build_verification_url("abc123")
    assert url == "https://api.kopie.cc/api/v1/auth/verify-email?token=abc123"
