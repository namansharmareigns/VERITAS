from fastapi import APIRouter, Query

from app.search.service import SearchService

router = APIRouter(prefix="/api", tags=["search"])


@router.get("/search")
def keyword_search(
    q: str = Query(..., min_length=1),
    domain: str | None = None,
    limit: int = Query(20, ge=1, le=50),
):
    return SearchService().keyword_search(q, domain=domain, limit=limit)


@router.get("/semantic-search")
async def semantic_search(
    q: str = Query(..., min_length=1),
    min_reliability: float = Query(0.0, ge=0.0, le=1.0),
    source_type: str | None = None,
    supports: bool | None = None,
    limit: int = Query(10, ge=1, le=30),
):
    return await SearchService().semantic_search(q, min_reliability, source_type, supports, limit)
