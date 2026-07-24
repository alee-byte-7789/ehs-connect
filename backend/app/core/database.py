"""
Database engine, session factory, and declarative base.

Every model in app/models inherits from `Base` defined here. Alembic's
env.py imports this same `Base` so autogenerate can see all models.
"""
import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import get_settings

settings = get_settings()

# SQLite needs this connect_arg when used with multiple threads (FastAPI's
# default threadpool for sync endpoints). PostgreSQL ignores it if present,
# but we only pass it when actually on SQLite to keep the prod URL clean.
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

# On Vercel, each request may hit a fresh (or reused) short-lived function
# instance rather than one steady long-running process — maintaining our
# own local connection pool there fights with Supabase's own external
# pooler instead of cooperating with it. NullPool disables local pooling
# so every request opens/closes its own connection through Supabase's
# pooled connection string. Vercel sets the VERCEL env var automatically;
# this has no effect on Render or local dev, where a normal pool is fine.
engine_kwargs = {"poolclass": NullPool} if os.environ.get("VERCEL") else {}

engine = create_engine(settings.database_url, connect_args=connect_args, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Shared declarative base for every ORM model in the project."""
    pass


def get_db() -> Generator:
    """FastAPI dependency: yields a request-scoped DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
