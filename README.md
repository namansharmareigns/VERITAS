# VERITAS

**VERITAS — An Evidence-Aware, Temporal and Explainable Database for Evolving AI Debates**

> From answering questions to understanding how positions evolve.

Turn a debate into a living knowledge object.

GitHub Repository: [ADD REPOSITORY URL]

## Overview

VERITAS is a proposed framework that represents debates as persistent, evidence-aware knowledge structures instead of temporary AI conversations. The system manages questions, PRO/CON claims, evidence, counterarguments, sources, contradictions, confidence scores, and temporal history in MongoDB.

**Important:** VERITAS does not determine objective truth. Synthesis outputs represent evidence-weighted estimates with explicit uncertainty.

## Architecture

```
React Frontend (Vite + TypeScript + Tailwind)
        ↓ REST/JSON
FastAPI Backend (Python)
        ↓
Debate Engine | Retrieval | Analytics | AI Agents
        ↓
MongoDB (veritas_db)
```

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React, Vite, TypeScript, Tailwind CSS, TanStack Query, Recharts, React Flow |
| Backend | Python, FastAPI, Pydantic, PyMongo, Uvicorn |
| Database | MongoDB (Atlas or local) |
| AI | Provider abstraction (OpenAI-compatible) with local fallback |

## MongoDB Design

**Database:** `veritas_db`

**Collections:** debates, claims, evidence, counterarguments, contradictions, sources, debate_history, embeddings, audit_logs

**Embed vs Reference:**
- **Embed:** current_synthesis, compact metadata within debates
- **Reference:** sources, evidence, claims, contradictions (independent lifecycle)

See [docs/data-model.md](docs/data-model.md) for full schema.

## Setup

### Prerequisites

- Node.js 18+
- Python 3.12+ (installed via winget: `Python.Python.3.12`)
- MongoDB 6+ running locally **or** MongoDB Atlas URI in `backend/.env`

> Without MongoDB, the frontend builds and runs but API calls will show degraded/disconnected status. Start MongoDB before seeding and integration testing.

### Environment

```bash
cp backend/.env.example backend/.env
# Edit MONGODB_URI, optional LLM_API_KEY
```

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python scripts/indexes.py
python scripts/seed.py
python scripts/embed_seed.py
python scripts/counts.py
uvicorn app.main:app --reload --port 8000
```

Swagger docs: http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:5173

## Environment Variables

| Variable | Description |
|----------|-------------|
| `MONGODB_URI` | MongoDB connection string |
| `MONGODB_DB` | Database name (default: veritas_db) |
| `LLM_PROVIDER` | openai or local |
| `LLM_API_KEY` | API key for LLM provider |
| `LLM_MODEL` | Model name |
| `EMBEDDING_MODEL` | Embedding model |
| `CORS_ORIGINS` | Allowed frontend origins |
| `DEMO_MODE` | Show demo mode banner |

## Seeding

```bash
python scripts/seed.py          # Seed development fixtures
python scripts/seed.py --clear  # Clear fixtures first
python scripts/indexes.py       # Create indexes
```

Development records are marked `development_fixture: true`.

## Queries & Aggregations

- 12 queries: `backend/app/analytics/queries.py`
- MongoDB shell examples: `backend/scripts/query_examples.js`
- 5 aggregations: `backend/app/analytics/service.py`
- Query Explorer UI: `/query-explorer`

## AI Configuration

Without `LLM_API_KEY`, the system uses deterministic fallback logic (clearly labeled). With a key, structured JSON generation is used for synthesis.

## Project Structure

```
VERITAS/
├── backend/          # FastAPI application
├── frontend/         # React application
├── docs/             # Documentation & academic evidence
├── data/             # Data exports
├── screenshots/      # Screenshot placeholders
└── README.md
```

## Screenshots

Capture using the application UI and MongoDB Compass. See [docs/SCREENSHOT_CHECKLIST.md](docs/SCREENSHOT_CHECKLIST.md).

## Current Status

See [docs/status.md](docs/status.md).

**Assignment (DA2 / Review 2):** [docs/DA2_SUBMISSION_RUNDOWN.md](docs/DA2_SUBMISSION_RUNDOWN.md) — rubric mapping, demo script, screenshot order.

## Future Work

- Advanced autonomous evidence ingestion
- Atlas Vector Search integration
- Multi-agent orchestration at scale
- Production deployment

## License

Academic project — see CONTRIBUTING.md
