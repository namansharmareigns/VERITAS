from fastapi import APIRouter

from app.config import get_settings
from app.database import get_db_health
from app.services.change_streams import get_change_stream_status

router = APIRouter(tags=["health"])


@router.get("/api/health")
def health():
    settings = get_settings()
    db_health = get_db_health()
    return {
        "status": "ok" if db_health.get("connected") else "degraded",
        "demo_mode": settings.demo_mode,
        "database": db_health,
        "change_streams": get_change_stream_status(),
    }
