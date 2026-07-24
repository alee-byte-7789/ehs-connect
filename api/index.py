"""
Vercel Python serverless entrypoint.

Vercel's Python runtime looks for an ASGI-compatible `app` object exported
from this file and wraps it as a serverless function per request. This is
NOT a rewrite of the backend — it's a thin adapter that imports the exact
same FastAPI app used for local/Render deployment, so there is only ever
one copy of the actual application code.
"""
import sys
from pathlib import Path

# Makes `backend/app/...` importable from this file's location.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.main import app  # noqa: E402  (import after sys.path setup, by necessity)

__all__ = ["app"]
