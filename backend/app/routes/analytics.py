from fastapi import APIRouter, HTTPException

from app.analytics.queries import QueryService
from app.analytics.service import AnalyticsService
from app.database import get_db_health
from app.utils.serialization import serialize_docs

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/overview")
def analytics_overview():
    return AnalyticsService().overview()


@router.get("/database-summary")
def database_summary():
    return AnalyticsService().database_summary()


@router.get("/database-health")
def database_health():
    return get_db_health()


@router.get("/indexes")
def list_indexes():
    return AnalyticsService().list_indexes()


@router.get("/debate/{debate_id}")
def debate_analytics(debate_id: str):
    result = AnalyticsService().debate_analytics(debate_id)
    if not result:
        raise HTTPException(status_code=404, detail="Debate not found")
    return result


@router.get("/aggregations/pro-con-confidence")
def agg_pro_con(debate_id: str | None = None):
    return AnalyticsService().pro_con_avg_confidence(debate_id)


@router.get("/aggregations/evidence-quality")
def agg_evidence_quality():
    return AnalyticsService().evidence_quality_by_source_type()


@router.get("/aggregations/evidence-per-claim")
def agg_evidence_per_claim(debate_id: str | None = None):
    return AnalyticsService().evidence_count_per_claim(debate_id)


@router.get("/aggregations/top-claims")
def agg_top_claims(limit: int = 10):
    return serialize_docs(AnalyticsService().highest_scoring_claims(limit))


@router.get("/aggregations/contradiction-distribution")
def agg_contradictions():
    return AnalyticsService().contradiction_distribution()


@router.get("/aggregations/domain-stats")
def agg_domain_stats():
    return AnalyticsService().domain_statistics()


@router.get("/queries/{query_name}")
def run_query(query_name: str, debate_id: str | None = None, claim_id: str | None = None):
    svc = QueryService()
    kwargs = {}
    if debate_id:
        kwargs["debate_id"] = debate_id
    if claim_id:
        kwargs["claim_id"] = claim_id
    try:
        result = svc.run_named_query(query_name, **kwargs)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    result["results"] = serialize_docs(result["results"])
    return result
