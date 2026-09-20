# DA2 / Review-2 Submission Rundown

**Project:** VERITAS — An Evidence-Aware, Temporal and Explainable Database for Evolving AI Debates  
**Database:** MongoDB `veritas_db` (Docker: `veritas-mongo` on port 27017)  
**Application:** React (Vite) + FastAPI + MongoDB  

This rundown maps the implemented system to the Review-2 / DA2 academic items. Seed records are marked `development_fixture: true` and are **not** experimental evidence.

---

## How to run (for demo / screenshots)

MongoDB (already started once Docker is running):

```powershell
cd c:\Users\NAMAN\Projects\VERITAS
docker compose up -d mongodb
```

Backend:

```powershell
cd c:\Users\NAMAN\Projects\VERITAS\backend
.\venv\Scripts\activate
python scripts\indexes.py
python scripts\seed.py
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Frontend:

```powershell
cd c:\Users\NAMAN\Projects\VERITAS\frontend
npm run dev
```

| Surface | URL |
|---------|-----|
| Website | http://127.0.0.1:5173 |
| API / Swagger | http://127.0.0.1:8000/docs |
| Health | http://127.0.0.1:8000/api/health |
| Database health UI | http://127.0.0.1:5173/database-health |
| Query explorer | http://127.0.0.1:5173/query-explorer |
| Project evidence UI | http://127.0.0.1:5173/projects/evidence |
| Analytics / indexes | http://127.0.0.1:5173/admin |

Verified live counts after seed (queried from MongoDB, not hard-coded):

| Collection | Count |
|------------|------:|
| debates | 5 |
| claims | 24 |
| evidence | 48 |
| counterarguments | 24 |
| contradictions | 13 |
| sources | 22 |
| debate_history | 30 |
| embeddings | 72 |

---

## Rubric mapping (DA2 / Review 2)

### 1. Finalized problem statement

**Submit:** `docs/problem-statement.md`

Traditional debate chatbots discard argument structure when a session ends. VERITAS is a **proposed framework** that stores debates as persistent, evidence-aware MongoDB documents (claims, evidence, contradictions, temporal history) with **explicit uncertainty** in synthesis. It does **not** claim to determine objective truth.

**Screenshot:** problem statement document (or first page of report quoting this file).

---

### 2. Final NoSQL model

**Submit:** `docs/data-model.md`

Collections: `debates`, `claims`, `evidence`, `counterarguments`, `contradictions`, `sources`, `debate_history`, `embeddings`, `audit_logs`.

**Embed vs reference (document this verbally too):**

- **Embedded:** `current_synthesis`, compact `metadata` on debates (read with the debate).
- **Referenced:** sources, evidence, claims, contradictions (independent lifecycle, reused, can grow large).

**Screenshot:** Compass collection list (`02_collection_list`) + one debate document (`03_debate_documents`).

---

### 3. Database implementation (MongoDB)

**Submit:** live `veritas_db` + `backend/app/database.py`

Connection via `MONGODB_URI` / `MONGODB_DB`. Docker Compose service `mongodb` (image `mongo:7`).

**Screenshot:** Compass database overview (`01_database_overview`) and UI `/database-health` showing **CONNECTED** (`29_database_connectivity`).

---

### 4. Sample data

**Submit:** `backend/scripts/seed.py`

Development fixtures (clearly labeled):

- 5 debates (Healthcare, Transportation, Education, Environment, Technology)
- 24 claims, 48 evidence, 24 counterarguments, 13 contradictions, 22 sources, 30 history events, 72 embeddings

Questions include: medical diagnosis AI, autonomous vehicles, generative AI in universities, vehicle restrictions, AI content disclosure.

**Screenshot:** Compass documents for debates / claims / evidence (`03`–`05`).

---

### 5. CRUD

**Submit:** FastAPI routes + Swagger `/docs`

| Entity | Create | Read | Update | Delete |
|--------|--------|------|--------|--------|
| Debates | `POST /api/debates` | `GET /api/debates`, `GET /api/debates/{id}` | `PUT /api/debates/{id}` | `DELETE /api/debates/{id}` |
| Claims | `POST /api/claims` | `GET /api/claims/{id}`, `GET /api/claims/debate/{id}` | `PUT /api/claims/{id}` | `DELETE /api/claims/{id}` |
| Evidence | `POST /api/evidence` | `GET /api/evidence/{id}`, `GET /api/evidence/claim/{id}` | `PUT /api/evidence/{id}` | `DELETE /api/evidence/{id}` |

UI create path: **Start a Debate** → workspace.

**Screenshot:** Swagger Try-it-out for POST/GET/PUT/DELETE (`06`–`09`) plus UI create debate.

---

### 6. Important queries (12)

**Submit:** `backend/app/analytics/queries.py`, `backend/scripts/query_examples.js`, UI `/query-explorer`

| ID | Query | UI / API |
|----|--------|----------|
| Q1 | All debates | Query Explorer `q1` |
| Q2 | Claims for a debate | `q2` (select debate) |
| Q3 | PRO vs CON confidence | `q3` |
| Q4 | Strongest supporting evidence | API `/api/analytics/queries/q4?claim_id=` |
| Q5 | Strongest opposing evidence | `q5` |
| Q6 | High-strength contradictions | `q6` |
| Q7 | Avg reliability by source type | `q7` |
| Q8 | Debate evolution over time | debate workspace timeline + `q8` |
| Q9 | Low-confidence claims | `q9` |
| Q10 | Rank claims by confidence | `q10` |
| Q11 | Evidence-weighted claim scores | `q11` |
| Q12 | Domain statistics | `q12` |

**Screenshot:** Query Explorer for Q1–Q3, Q6–Q12 (`10`–`19`). For Q4/Q5 use Swagger with a `claim_id` from Q2.

---

### 7. Indexing

**Submit:** `backend/scripts/indexes.py`, `docs/indexing.md`, UI `/admin`

| Collection | Index | Why |
|------------|-------|-----|
| debates | `(domain, created_at)` | Filtered listing |
| claims | `(debate_id, position, confidence)` | Workspace ranking |
| evidence | `(claim_id, supports, reliability_score, relevance)` | Evidence ranking |
| contradictions | `(strength)` | High-strength query |
| debate_history | `(debate_id, timestamp)` | Timeline |
| sources | `(source_type, published_at)` | Source filters |
| embeddings | `(entity_type, entity_id)` | Semantic lookup |
| counterarguments | `(claim_id)` | Per-claim load |

**Screenshot:** Admin indexes table (`20_index_list`) or Compass Indexes tab.

---

### 8. Aggregations (5)

**Submit:** `backend/app/analytics/service.py`, `docs/aggregation.md`, UI `/admin`

| ID | Pipeline | Endpoint |
|----|----------|----------|
| A1 | PRO vs CON average confidence | `/api/analytics/aggregations/pro-con-confidence` |
| A2 | Evidence quality by source type | `/api/analytics/aggregations/evidence-quality` |
| A3 | Evidence count per claim | `/api/analytics/aggregations/evidence-per-claim` |
| A4 | Highest-scoring claims | `/api/analytics/aggregations/top-claims` |
| A5 | Contradiction distribution | `/api/analytics/aggregations/contradiction-distribution` |

**Screenshot:** Admin aggregation JSON panels (`21`–`23`).

---

### 9. Application–database connectivity

**Submit:** FastAPI + React + live MongoDB

Flow: UI → `GET/POST /api/...` → PyMongo → `veritas_db` → JSON → UI.

Demo pages: `/database-health`, `/projects/evidence`, `/dashboard`.

Backend tests (11 passed with MongoDB): `cd backend; pytest tests/ -v`

**Screenshot:** `/database-health` CONNECTED + dashboard with live counts (`24`, `29`).

---

### 10. NoSQL concepts

**Submit:** `docs/nosql-concepts.md`

Cover in viva: document model, embedding vs referencing, aggregation (`$group`, `$lookup`), compound indexes, flexible provenance metadata, append-only `debate_history`.

---

### 11. Current status

**Submit:** `docs/status.md`

Report **COMPLETED** for core DA2 items. Mark Atlas Vector Search and replica-set change streams as **IN PROGRESS / EXPERIMENTAL**. Local Docker MongoDB uses **change-stream fallback** (standalone node). LLM synthesis is fallback unless `LLM_API_KEY` is set.

---

### 12. Individual contribution

**Submit:** `docs/contributions.md` — fill teammate names before PDF submission.

Suggested split: (1) MongoDB model + seed + indexes, (2) FastAPI CRUD/queries, (3) scoring + contradiction + history, (4) React dashboard + graph + docs.

---

## Extra application features (helps marks, not fake claims)

- Debate graph (React Flow): `/debates/{id}`
- Temporal PRO/CON/confidence chart
- Evidence scoring: Reliability × Relevance × Independence × Recency (**proposed framework**)
- AI analyze with **local fallback** if no API key (`Generate Analysis`)
- Semantic search foundation (local embeddings after seed)
- Export: `GET /api/debates/{id}/export`

---

## Screenshot capture order (DA2 evidence pack)

Use `docs/SCREENSHOT_CHECKLIST.md`. Suggested 20-minute pass:

1. Compass: database, collections, 1 debate, 1 claim, 1 evidence.
2. Swagger: POST debate, GET, PUT status, DELETE (use a throwaway debate).
3. `/query-explorer`: run Q1, Q2, Q3, Q6, Q7, Q9, Q10, Q12.
4. `/admin`: indexes + aggregations.
5. `/dashboard`, one seeded debate workspace (graph + evidence + timeline).
6. `/database-health`.
7. GitHub / `git log` if you push (`30_github_history`).

Save files under `screenshots/`.

---

## What to say in the demo (2 minutes)

1. Open landing: “debates are stored as knowledge objects, not chat logs.”
2. Dashboard: live MongoDB counts.
3. Open **Should generative AI be used in university education?**
4. Show PRO/CON, evidence cards (fixture labeled), graph, history.
5. Click **Generate Analysis** (fallback labeled if no LLM key).
6. `/query-explorer` Q12 domain stats + `/admin` indexes.
7. `/database-health`: CONNECTED, `veritas_db`.

Close: “Scoring is a proposed framework; synthesis reports uncertainty, not truth.”

---

## Limitations (state honestly)

- Seed data is **development fixtures**, not a scientific corpus.
- Standalone Docker MongoDB: change streams **fallback**.
- Semantic search uses **local hashed embeddings** unless an embedding API key is configured.
- LLM analysis uses **deterministic fallback** without `LLM_API_KEY`.
- The DA2 PDF was not in this repository; this mapping follows the 12 Review-2 items listed in the project specification (`docs/REVIEW_2_RUBRIC_MAPPING.md`). If your PDF has extra rows, align screenshots to those titles using `/projects/evidence`.
