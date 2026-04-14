"""Application configuration management for IssueVault."""

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

    app_name: str = os.getenv("APP_NAME", "IssueVault")
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

    oracle_host: str = os.getenv("ORACLE_HOST", "localhost")
    oracle_port: int = int(os.getenv("ORACLE_PORT", "1521"))
    oracle_service_name: str = os.getenv("ORACLE_SERVICE_NAME", "XEPDB1")
    oracle_dsn: str = os.getenv("ORACLE_DSN", "")
    oracle_user: str = os.getenv("ORACLE_USER", "")
    oracle_password: str = os.getenv("ORACLE_PASSWORD", "")
    oracle_pool_min: int = int(os.getenv("ORACLE_POOL_MIN", "1"))
    oracle_pool_max: int = int(os.getenv("ORACLE_POOL_MAX", "8"))
    oracle_pool_increment: int = int(os.getenv("ORACLE_POOL_INCREMENT", "1"))

    @property
    def dsn(self) -> str:
        """Build DSN from host/port/service when ORACLE_DSN is not provided."""
        if self.oracle_dsn:
            return self.oracle_dsn
        return f"{self.oracle_host}:{self.oracle_port}/{self.oracle_service_name}"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Cache and return application settings."""
    return Settings()
