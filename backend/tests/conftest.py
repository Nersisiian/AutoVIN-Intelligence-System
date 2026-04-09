from __future__ import annotations

import os

import pytest


@pytest.fixture(scope="session", autouse=True)
def _test_env() -> None:
    # Configure env BEFORE importing app modules.
    os.environ.setdefault("APP_ENV", "test")
    os.environ.setdefault("LOG_LEVEL", "INFO")
    os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
    os.environ.setdefault("REDIS_URL", "redis://localhost:6379/15")
    os.environ.setdefault("RATE_LIMIT", "1000/minute")
    os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")

