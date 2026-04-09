from __future__ import annotations

from contextlib import asynccontextmanager

from app.api.routes import router as api_router
from app.core.config import settings
from app.core.db import engine
from app.core.logging import configure_logging, get_logger
from app.models.base import Base
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from sqlalchemy import text

configure_logging(settings.log_level)
log = get_logger(component="main")

limiter = Limiter(key_func=get_remote_address, default_limits=[settings.rate_limit])


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create DB tables (keeps "one command" run simple). For serious migrations use Alembic.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text("SELECT 1"))
    log.info("startup_complete")
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.middleware("http")
async def request_logging(request: Request, call_next):
    logger = get_logger(component="http", method=request.method, path=request.url.path)
    try:
        resp = await call_next(request)
        logger.info("request_complete", status_code=resp.status_code)
        return resp
    except Exception as e:  # noqa: BLE001
        logger.exception("request_failed", err=str(e))
        raise

