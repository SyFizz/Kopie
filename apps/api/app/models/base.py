"""Base déclarative SQLAlchemy commune à tous les modèles."""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base commune pour tous les modèles ORM Kopie."""
