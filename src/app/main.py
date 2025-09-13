from config import SENTRY_DSN
from src.app.database import engine, Base
from src.app.api import balancer
from src.app.srv import config

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sentry_sdk.integrations.httpx import HttpxIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
import sentry_sdk

import logging.config
from contextlib import asynccontextmanager
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from logger_config import CONFIG


logging.config.dictConfig(CONFIG)
logger = logging.getLogger(__name__)

uvicorn_logger = logging.getLogger("uvicorn")
uvicorn_access_logger = logging.getLogger("uvicorn.access")
uvicorn_error_logger = logging.getLogger("uvicorn.error")
fastapi_logger = logging.getLogger("fastapi")

sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=[
        LoggingIntegration(),
        HttpxIntegration(),
    ],
    traces_sample_rate=0.1,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database tables initialized successfully")
    except Exception as e:
        logger.warning(f"⚠️  Warning: Could not initialize database tables: {e}")
        logger.warning(
            "   The application will continue but database features may not work"
        )

    yield

    await engine.dispose()
    logger.info("✅ Database connections closed")


app = FastAPI(
    title="Video Balancer",
    description="A simple video request balancer that routes requests to CDN or origin servers",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(balancer.router)
app.include_router(config.router)


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    logger.error(f"Invalid input: {exc}")
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception):
    logger.exception("Unhandled server error")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Video Balancer API",
        "version": "1.0.0",
        "endpoints": {
            "balancer": "/?video=<video_url>",
            "config_api": "/api/config/",
            "docs": "/docs",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "video-balancer"}
