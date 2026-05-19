"""Configuration applicative — Pydantic Settings (lecture .env)."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Variables d'environnement de l'API Kopie."""

    DATABASE_URL: str = "postgresql+asyncpg://kopie:kopie@localhost:5432/kopie"
    SECRET_KEY: str = "changeme-generate-with-openssl-rand-hex-32"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
    ]
    DATA_RETENTION_MONTHS: int = 12

    OPENAPI_CONTRACT_PATH: str = "../../contracts/openapi.yaml"

    # SMTP (Story 1.3)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    # URL de base de l'API (Story 1.3 — construction des liens email de vérification)
    APP_BASE_URL: str = "http://localhost:8000"

    # Rate limiting (FR-43)
    RATE_LIMIT_AUTH: str = "10/minute"
    RATE_LIMIT_STUDENT_ANSWERS: str = "60/minute"
    RATE_LIMIT_STUDENT_EVENTS: str = "30/minute"
    RATE_LIMIT_STUDENT_SUBMIT: str = "5/minute"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
