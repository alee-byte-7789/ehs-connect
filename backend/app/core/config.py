"""
Central application settings.

All configuration is environment-driven so the same codebase runs against
SQLite in local development and PostgreSQL (Supabase) in production without
any code changes — only environment variables differ.
"""
from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- App ---
    app_name: str = "EHS Connect API"
    api_v1_prefix: str = "/api/v1"
    environment: str = "development"  # "development" | "production"

    # --- Database ---
    # Dev default: local SQLite file. Prod: set DATABASE_URL to the Supabase
    # PostgreSQL connection string via environment variables (never committed).
    # Supabase (and most providers) hand out "postgres://" or "postgresql://"
    # URLs, which default to the psycopg2 driver. This project uses psycopg3
    # instead, so the scheme is normalized automatically below — paste the
    # connection string exactly as Supabase gives it, no manual editing needed.
    database_url: str = "sqlite:///./ehs_connect.db"

    @field_validator("database_url")
    @classmethod
    def normalize_postgres_scheme(cls, v: str) -> str:
        if v.startswith("postgres://"):
            return "postgresql+psycopg://" + v[len("postgres://") :]
        if v.startswith("postgresql://"):
            return "postgresql+psycopg://" + v[len("postgresql://") :]
        return v

    # --- Auth / JWT ---
    jwt_secret_key: str = "CHANGE_ME_IN_ENV__NEVER_COMMIT_REAL_SECRET"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # --- CORS ---
    # A comma-separated string, not a list — pydantic-settings tries to JSON-parse
    # list-typed env vars before any validator runs, which breaks a plain
    # comma-separated value pasted into Railway's env var UI. Use
    # `cors_allow_origins_list` below to get the parsed list.
    cors_allow_origins: str = "http://localhost:5173,http://localhost:19006"

    @property
    def cors_allow_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allow_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Settings are cached so the .env file is parsed only once per process."""
    return Settings()
