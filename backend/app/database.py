import logging
from datetime import datetime, timezone
from typing import Any

from pymongo import MongoClient
from pymongo.database import Database

from app.config import get_settings

logger = logging.getLogger(__name__)

_client: MongoClient | None = None
_db: Database | None = None
_last_successful_query: datetime | None = None
_last_query_latency_ms: float = 0.0


def get_client() -> MongoClient:
    global _client
    if _client is None:
        settings = get_settings()
        _client = MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=5000)
    return _client


def get_db() -> Database:
    global _db
    if _db is None:
        settings = get_settings()
        _db = get_client()[settings.mongodb_db]
    return _db


def ping_db() -> dict[str, Any]:
    global _last_successful_query, _last_query_latency_ms
    import time

    start = time.perf_counter()
    client = get_client()
    client.admin.command("ping")
    latency = (time.perf_counter() - start) * 1000
    _last_successful_query = datetime.now(timezone.utc)
    _last_query_latency_ms = latency
    settings = get_settings()
    return {
        "connected": True,
        "database": settings.mongodb_db,
        "latency_ms": round(latency, 2),
        "last_successful_query": _last_successful_query.isoformat(),
    }


def get_db_health() -> dict[str, Any]:
    settings = get_settings()
    try:
        ping = ping_db()
        db = get_db()
        collections = db.list_collection_names()
        counts = {}
        total = 0
        for name in [
            "debates", "claims", "evidence", "counterarguments",
            "contradictions", "sources", "debate_history", "embeddings", "audit_logs",
        ]:
            if name in collections:
                c = db[name].count_documents({})
                counts[name] = c
                total += c
        index_count = sum(len(list(db[c].list_indexes())) for c in collections)
        return {
            **ping,
            "collections": len(collections),
            "collection_counts": counts,
            "total_records": total,
            "index_count": index_count,
        }
    except Exception as e:
        logger.error("MongoDB health check failed: %s", e)
        return {
            "connected": False,
            "database": settings.mongodb_db,
            "error": str(e),
            "last_successful_query": _last_successful_query.isoformat() if _last_successful_query else None,
            "latency_ms": _last_query_latency_ms,
        }


def close_db() -> None:
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None
