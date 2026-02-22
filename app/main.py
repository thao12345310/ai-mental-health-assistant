"""
FastAPI application factory and startup/shutdown lifecycle.
"""
import logging

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import create_tables

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=settings.APP_DESCRIPTION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # ── CORS ──────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Global exception handlers ─────────────────────────────────────────────
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception on %s %s", request.method, request.url)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An internal server error occurred. Please try again."},
        )

    # ── Startup ───────────────────────────────────────────────────────────────
    @app.on_event("startup")
    async def on_startup() -> None:
        logger.info("Starting %s v%s", settings.APP_NAME, settings.APP_VERSION)
        await create_tables()
        logger.info("Database tables verified/created.")

    # ── Routes ────────────────────────────────────────────────────────────────
    app.include_router(api_router)

    @app.get("/health", tags=["Health"], summary="Health check")
    async def health_check() -> dict:
        return {"status": "healthy", "version": settings.APP_VERSION}

    return app


app = create_app()
