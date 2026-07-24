"""
Remote migration trigger.

This exists because Vercel's serverless functions and a developer's local
machine are two different network environments — a local machine can
sometimes fail to resolve Supabase's hostname (broken local/ISP DNS) even
though the deployed backend itself reaches Supabase fine for every other
request. Rather than debugging a developer's local network configuration,
this endpoint runs the exact same `alembic upgrade head` from inside the
already-working Vercel environment instead.

Protected by a shared secret (`MIGRATION_SECRET` env var) that has NO
default — if it's unset, this endpoint always refuses, so there's no
accidental unprotected door into running migrations against production.
This is intentionally a blunt, temporary tool, not a permanent CI/CD
migration pipeline — remove or rotate the secret once no longer needed.
"""
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi import APIRouter, Header, HTTPException, status

from app.core.config import get_settings

router = APIRouter(prefix="/ops", tags=["ops"])

_BACKEND_DIR = Path(__file__).resolve().parents[3]  # .../backend


@router.post("/migrate")
def run_migrations(x_migration_secret: str | None = Header(default=None)) -> dict[str, str]:
    settings = get_settings()

    if not settings.migration_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MIGRATION_SECRET is not configured; this endpoint is disabled.",
        )

    if x_migration_secret != settings.migration_secret:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid or missing secret.")

    alembic_ini_path = _BACKEND_DIR / "alembic.ini"
    cfg = Config(str(alembic_ini_path))
    cfg.set_main_option("script_location", str(_BACKEND_DIR / "alembic"))

    command.upgrade(cfg, "head")

    return {"message": "Migrations applied successfully."}
