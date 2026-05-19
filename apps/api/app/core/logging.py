"""Configuration des logs structurés (structlog, JSON).

⚠️ JAMAIS logger de PII élève (student_first_name, student_last_name, etc.)
   conformément à NFR-8 et à l'architecture §Logs.
"""
import structlog


def configure_logging() -> None:
    """Configure structlog en mode JSON (production-ready)."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(20),
        logger_factory=structlog.PrintLoggerFactory(),
    )


logger = structlog.get_logger()
