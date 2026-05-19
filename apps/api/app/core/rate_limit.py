"""Rate limiting via slowapi (FR-43).

Instance partagée par l'application : créée ici pour être importable
à la fois par ``main.py`` (middleware + handler) et par les endpoints
(``@limiter.limit(...)``).

Conformément à architecture.md, le rate limit s'applique aux routes
``/auth/*`` ainsi qu'aux routes sensibles côté élève (Story 4.x).
"""
from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
