import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import close_db, ping_db
from app.routes import (
    ai,
    analysis,
    analytics,
    claims,
    contradictions,
    counterarguments,
    debates,
    evidence,
    health,
    history,
    import_data,
    search,
    sources,
)
from app.services.change_streams import get_change_stream_status, start_change_streams
from app.utils.mongo_errors import is_mongo_error
from pymongo.errors import PyMongoError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("veritas")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.info("Starting VERITAS backend (demo_mode=%s)", settings.demo_mode)
    try:
        ping_db()
        logger.info("MongoDB connected")
        cs_status = start_change_streams()
        logger.info("Change streams: %s", cs_status.get("mode"))
    except Exception as e:
        logger.warning("MongoDB not available at startup: %s", e)
    yield
    close_db()


app = FastAPI(
    title="VERITAS API",
    description="Evidence-Aware, Temporal and Explainable Database for Evolving AI Debates",
    version="1.0.0",
    lifespan=lifespan,
)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = (time.perf_counter() - start) * 1000
    logger.info("%s %s %.1fms", request.method, request.url.path, duration)
    return response


@app.exception_handler(PyMongoError)
async def mongo_exception_handler(request: Request, exc: PyMongoError):
    logger.warning("MongoDB error on %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=503,
        content={
            "detail": "MongoDB unavailable. Start MongoDB with: docker compose up -d",
            "code": "MONGODB_UNAVAILABLE",
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if is_mongo_error(exc):
        return await mongo_exception_handler(request, exc)  # type: ignore[arg-type]
    logger.error("Unhandled error on %s: %s", request.url.path, exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error", "code": "INTERNAL_ERROR"})


for module in [health, debates, claims, evidence, counterarguments, contradictions, sources, search, analytics, history, ai, analysis, import_data]:
    app.include_router(module.router)


@app.get("/api/change-streams/status")
def change_stream_status():
    return get_change_stream_status()
