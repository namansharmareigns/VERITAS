# VERITAS API

Base URL: `http://localhost:8000`

Swagger: `/docs`

## Core Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/health | Health check |
| POST/GET/PUT/DELETE | /api/debates | Debate CRUD |
| POST/GET/PUT/DELETE | /api/claims | Claim CRUD |
| POST/GET/PUT/DELETE | /api/evidence | Evidence CRUD |
| GET | /api/history/{debate_id} | Temporal history |
| POST | /api/ai/analyze | Run debate analysis |
| GET | /api/search | Keyword search |
| GET | /api/semantic-search | Semantic search |
| GET | /api/analytics/overview | Dashboard stats |
| GET | /api/analytics/queries/{name} | Run named query |
| GET | /api/analysis/debate/{id}/graph | Debate graph data |

See Swagger for full request/response schemas.
