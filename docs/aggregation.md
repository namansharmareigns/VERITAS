# Aggregation Pipelines

Implemented in `backend/app/analytics/service.py`

| ID | Pipeline | Endpoint |
|----|----------|----------|
| A1 | PRO vs CON avg confidence | /api/analytics/aggregations/pro-con-confidence |
| A2 | Evidence quality by source type | /api/analytics/aggregations/evidence-quality |
| A3 | Evidence count per claim | /api/analytics/aggregations/evidence-per-claim |
| A4 | Highest-scoring claims | /api/analytics/aggregations/top-claims |
| A5 | Contradiction distribution | /api/analytics/aggregations/contradiction-distribution |
