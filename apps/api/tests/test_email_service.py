"""Tests du service email — NFR-8 (pas de fuite de token dans les logs)."""
from __future__ import annotations

import json

import pytest
from structlog.testing import capture_logs

from app.services import email_service


def test_send_verification_email_degraded_mode_does_not_log_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Mode dégradé : le token et l'URL ne doivent JAMAIS apparaître en clair.

    Le test capture spécifiquement les logs structlog (``capture_logs()``)
    plutôt que ``caplog`` (qui ne voit pas les enregistrements émis par
    ``structlog.PrintLoggerFactory``) — sinon il passerait trivialement
    sur une liste vide. On exige :

    1. **Au moins un log est émis** (le warning de mode dégradé) — sinon
       l'assertion d'absence est triviale et le test sans valeur.
    2. Ni le token complet ni l'URL de vérification ne figurent dans la
       sérialisation des logs.
    3. Un ``token_prefix`` court (≤ 9 caractères, terminé par ``…``) est
       présent — preuve que la log policy est bien appliquée.
    """
    monkeypatch.setattr(email_service.settings, "SMTP_HOST", "")

    token = "very-secret-token-1234567890abcdef-do-not-log"
    email = "victime@example.fr"

    with capture_logs() as cap_logs:
        email_service.send_verification_email(email, token)

    assert cap_logs, (
        "Au moins un log doit être émis en mode dégradé — sinon les "
        "assertions d'absence ci-dessous seraient triviales."
    )

    serialized = json.dumps(cap_logs, ensure_ascii=False, default=str)

    assert token not in serialized, (
        "Le token complet ne doit jamais apparaître dans les logs."
    )
    assert "/api/v1/auth/verify-email?token=" not in serialized, (
        "L'URL de vérification (qui embarque le token) ne doit pas être loggée."
    )

    prefixes = [
        record.get("token_prefix")
        for record in cap_logs
        if isinstance(record.get("token_prefix"), str)
    ]
    assert prefixes, "Le préfixe court du token doit être journalisé."
    for prefix in prefixes:
        assert prefix.endswith("…"), prefix
        assert len(prefix) <= 9, prefix
        assert token.startswith(prefix.rstrip("…"))


def test_build_verification_url_uses_app_base_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        email_service.settings, "APP_BASE_URL", "https://api.kopie.cc/"
    )
    url = email_service.build_verification_url("abc123")
    assert url == "https://api.kopie.cc/api/v1/auth/verify-email?token=abc123"
