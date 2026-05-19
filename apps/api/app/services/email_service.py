"""Service d'envoi d'email — Story 1.3 (vérification d'adresse).

Conformité :
- NFR-8 : ne JAMAIS logger le mot de passe ni le token en clair. Seuls
  l'email et l'URL de vérification (qui contient le token, certes — d'où
  un log uniquement en mode dégradé/dev) sont émis.
- Mode dégradé : si ``SMTP_HOST`` est vide → on logge un ``warning``
  et on retourne sans erreur. Pratique en dev local et en CI sans SMTP.
- ``smtplib`` synchrone est acceptable : la fonction est appelée via
  ``BackgroundTasks`` FastAPI, donc hors du chemin de réponse HTTP.
"""
from __future__ import annotations

import smtplib
from email.message import EmailMessage

import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


def build_verification_url(token: str) -> str:
    """Construit l'URL de vérification à partir de ``APP_BASE_URL``."""
    base = settings.APP_BASE_URL.rstrip("/")
    return f"{base}/api/v1/auth/verify-email?token={token}"


def send_verification_email(email: str, token: str) -> None:
    """Envoie l'email de vérification — NOP si SMTP_HOST non configuré.

    Cette fonction est destinée à être enregistrée via
    ``BackgroundTasks.add_task(send_verification_email, email, token)``.
    Elle ne doit JAMAIS lever d'exception sortant du contexte de la
    background-task : on logge et on échoue silencieusement (UX : la
    réponse HTTP 201 doit rester correcte même si SMTP est down).
    """
    verification_url = build_verification_url(token)

    if not settings.SMTP_HOST:
        logger.warning(
            "smtp.host_not_configured_email_skipped",
            email=email,
            verification_url=verification_url,
        )
        return

    msg = EmailMessage()
    msg["Subject"] = "Kopie — Confirmez votre adresse email"
    msg["From"] = settings.SMTP_USER or "no-reply@kopie.local"
    msg["To"] = email
    msg.set_content(
        "Bonjour,\n\n"
        "Cliquez sur ce lien pour confirmer votre adresse email :\n"
        f"{verification_url}\n\n"
        "Ce lien expire dans 24 heures.\n\n"
        "— L'équipe Kopie"
    )

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                smtp.starttls()
                smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            smtp.send_message(msg)
    except Exception as exc:
        logger.error(
            "smtp.send_failed",
            email=email,
            error=str(exc),
        )
        return

    logger.info("smtp.verification_email_sent", email=email)
