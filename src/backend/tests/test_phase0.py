"""Tests for Phase 0 — Project scaffolding & infrastructure."""

import os
import pytest
from httpx import Client

# Disable proxy for httpx so requests go directly to localhost
os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)
os.environ.pop("http_proxy", None)
os.environ.pop("https_proxy", None)

BACKEND_URL = "http://127.0.0.1:8002"
FRONTEND_URL = "http://localhost:5173"

# ── Step 0.1 + 0.2: Backend + DB connection ──────────────────


def test_health_endpoint():
    """GET /api/v1/health returns 200 with {"status": "ok"}."""
    with Client(base_url=BACKEND_URL, trust_env=False) as client:
        resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_swagger_docs_reachable():
    """OpenAPI schema is served, proving Swagger docs are available."""
    import subprocess, time
    # Retry up to 3 times — uvicorn reload mode may briefly restart during test
    for attempt in range(3):
        result = subprocess.run(
            ["curl.exe", "-s", "--retry", "2", "--retry-delay", "1",
             "-o", "NUL", "-w", "%{http_code}", f"{BACKEND_URL}/openapi.json"],
            capture_output=True, text=True, timeout=15,
        )
        code = result.stdout.strip()
        if code == "200":
            break
        time.sleep(2)
    assert code == "200", f"Expected 200, got {code}"


# ── Step 0.2: Database connection ─────────────────────────────


def test_database_connection():
    """SQLAlchemy engine can connect and execute a simple query."""
    from sqlalchemy import text
    from app.database import engine

    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1 AS test"))
        row = result.fetchone()
    assert row is not None
    assert row[0] == 1


def test_get_db_dependency():
    """get_db yields a session and closes it properly."""
    from app.dependencies import get_db

    gen = get_db()
    session = next(gen)
    assert session is not None

    # Ensure the session is usable
    from sqlalchemy import text
    result = session.execute(text("SELECT 1"))
    assert result.fetchone()[0] == 1

    # Cleanup
    try:
        next(gen)
    except StopIteration:
        pass  # Expected — generator exhausted after close


# ── Step 0.3: Alembic ────────────────────────────────────────


def test_alembic_current_version():
    """Alembic has a current head revision applied."""
    import subprocess
    result = subprocess.run(
        ["alembic", "current"],
        capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(__file__))
    )
    combined = result.stdout + result.stderr
    assert "head" in combined, f"Expected 'head' in alembic output: {combined}"


# ── Step 0.4: Frontend proxy ─────────────────────────────────


def test_vite_proxy_to_backend():
    """Vite dev server proxies /api requests to the backend."""
    with Client(base_url=FRONTEND_URL, trust_env=False) as client:
        resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
