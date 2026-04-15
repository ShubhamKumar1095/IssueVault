"""Application configuration management for ResolveHub."""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
import os

from dotenv import load_dotenv

load_dotenv()


def _csv_to_list(value: str, default: list[str]) -> list[str]:
    """Split a CSV env value into a cleaned list."""
    if not value:
        return default
    return [item.strip().lower() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    """Typed settings loaded from environment variables."""

    app_name: str = os.getenv("APP_NAME", "ResolveHub")
    app_env: str = os.getenv("APP_ENV", "local")
    app_secret_key: str = os.getenv("APP_SECRET_KEY", "change-this-secret")

    upload_dir: str = os.getenv("UPLOAD_DIR", "uploads")
    max_upload_mb: int = int(os.getenv("MAX_UPLOAD_MB", "10"))
    allowed_extensions: list[str] = field(
        default_factory=lambda: _csv_to_list(
            os.getenv("ALLOWED_EXTENSIONS", ""),
            default=["png", "jpg", "jpeg", "pdf", "txt", "log", "csv", "json", "zip"],
        )
    )

    sqlite_db_path: str = os.getenv("SQLITE_DB_PATH", "data/resolvehub.db")
    sqlite_busy_timeout_ms: int = int(os.getenv("SQLITE_BUSY_TIMEOUT_MS", "5000"))
    query_cache_ttl_sec: int = int(os.getenv("QUERY_CACHE_TTL_SEC", "45"))


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Cache and return application settings."""
    return Settings()
