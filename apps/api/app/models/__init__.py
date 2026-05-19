"""Modèles SQLAlchemy.

Tous les modèles concrets sont importés ici pour qu'Alembic
``--autogenerate`` les détecte via ``Base.metadata``.
"""
from app.models.base import Base
from app.models.teacher import Teacher

__all__ = ["Base", "Teacher"]
