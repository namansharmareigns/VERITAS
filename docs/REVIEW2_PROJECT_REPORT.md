# BCSE406L – NoSQL Databases
# Digital Assignment 2 — Review 2
# Updated Project Report + Evidence Guide

**Course:** BCSE406L – NoSQL Databases  
**Semester:** Fall 2026–27  
**Faculty:** Dr. S. Geetha  
**Due:** 20.09.2026  
**Marks:** 10  

**Project title:** VERITAS — An Evidence-Aware, Temporal and Explainable Database for Evolving AI Debates  

**Tagline:** From answering questions to understanding how positions evolve.

**GitHub repository:** *[ADD REPOSITORY URL after you push]*  

**Important academic note:** Development seed records are marked `development_fixture: true`. They demonstrate database implementation. They are **not** scientific experimental evidence. VERITAS is a **proposed framework**. It does **not** determine objective truth.

---

# PART 0 — Complete technical description of the implemented system

Copy this section into Chapter 1–3 of the report as “System Overview”. Every claim below matches the code in this repository.

## 0.1 What VERITAS is

VERITAS is a full-stack academic web application that stores a **debate as a persistent MongoDB knowledge object**, not as a temporary chatbot transcript.

A user submits a **question** (for example: “Should generative AI be used in university education?”). The system creates a `debates` document. Related **PRO claims**, **CON claims**, **evidence**, **counterarguments**, **contradictions**, **sources**, and **temporal history** are stored as collections that reference one another by ObjectId.

The application layer (FastAPI) reads and writes MongoDB. The frontend (React) displays:

- dashboard statistics queried live from MongoDB  
- debate workspace (PRO / CON panels)  
- evidence explorer  
- debate graph (React Flow)  
- temporal evolution chart (Recharts)  
- query explorer (prebuilt safe queries)  
- database health (connection, collection counts, latency)  
- admin analytics (indexes + aggregations)

AI is optional. If `LLM_API_KEY` is empty, analysis uses **deterministic fallback** logic and labels the output as fallback. Scoring arithmetic is done in Python, not by an LLM.

## 0.2 Why MongoDB (NoSQL justification)

A debate is an evolving, nested, heterogeneous object:

- A debate has compact current scores (natural to **embed**).  
- Evidence, sources, and contradictions grow independently and are reused (natural to **reference**).  
- Provenance fields differ by generator (`user`, `ai`, `retrieval`).  
- History is append-only time-stamped events.  
- Analytics need `$group`, `$lookup`, `$avg`, `$sort`.

A rigid relational schema would force many join tables for tags, provenance, and evolving synthesis. MongoDB’s document model matches the domain.

## 0.3 Architecture (implemented)

```
User
  → React + TypeScript + Vite + Tailwind  (http://127.0.0.1:5173)
       REST/JSON
  → FastAPI + Pydantic + PyMongo          (http://127.0.0.1:8000)
       Debate engine | Scoring | Queries | Aggregations | Search | AI agents
  → MongoDB 7 (Docker container veritas-mongo)
       Database: veritas_db
```

**Not used (intentionally):** Kubernetes, Kafka, Redis clusters, microservices. The course requirement is NoSQL database implementation plus an application, not enterprise ops.

## 0.4 Technology stack (actual)

| Layer | Technology |
|-------|------------|
| Frontend | React 19, Vite 8, TypeScript, Tailwind CSS 4, TanStack Query, React Router, React Hook Form, Zod, Recharts, React Flow, Lucide |
| Backend | Python 3.12, FastAPI 0.115, Pydantic 2, PyMongo 4, Uvicorn |
| Database | MongoDB 7 (Docker), database name `veritas_db` |
| AI | OpenAI-compatible HTTP provider + local fallback (`backend/app/agents/`) |
| Tests | pytest — 11 API tests passed against MongoDB |

## 0.5 Repository layout

```
VERITAS/
├── backend/
│   ├── app/                 FastAPI application
│   │   ├── main.py          App, CORS, Mongo error handling
│   │   ├── config.py        Environment settings
│   │   ├── database.py      PyMongo client, ping, health
│   │   ├── routes/          REST endpoints
│   │   ├── schemas/         Pydantic request/response models
│   │   ├── services/        Scoring, temporal history, contradictions
│   │   ├── analytics/       12 queries + 5 aggregations
│   │   ├── agents/          LLM abstraction + fallback + analysis pipeline
│   │   └── search/          Keyword + semantic search
│   ├── scripts/
│   │   ├── seed.py          Development fixtures
│   │   ├── indexes.py       Index creation
│   │   ├── query_examples.js  mongosh query text
│   │   ├── counts.py        Collection counts
│   │   └── embed_seed.py    Local embeddings
│   ├── tests/test_api.py
│   └── requirements.txt
├── frontend/src/pages/      Home, Dashboard, Debates, Workspace, Search, Admin, Health, Query Explorer, Evidence
├── docs/                    This report sources
├── docker-compose.yml       mongo:7 on port 27017
├── data/                    Export folder
└── screenshots/             Place DA2 screenshots here
```

## 0.6 Database collections (conceptual tree)

```
DEBATE
 ├── CLAIMS (PRO | CON)
 │     ├── EVIDENCE  → SOURCE (optional)
 │     └── COUNTERARGUMENTS
 ├── CONTRADICTIONS (claim_a ↔ claim_b)
 ├── HISTORY (append-only snapshots)
 └── EMBEDDINGS (claim | evidence vectors)
```

## 0.7 Hybrid embed vs reference (implemented)

**Embedded inside `debates`:** `current_synthesis` (summary, confidence, pro_score, con_score, uncertainty) and compact `metadata`. These are always shown with the debate header.

**Referenced by ObjectId:**

- `claims.debate_id`  
- `evidence.claim_id`, `evidence.source_id`  
- `counterarguments.claim_id`  
- `contradictions.claim_a`, `claim_b`  
- `debate_history.debate_id`  
- `embeddings.entity_id`  

Claims also store `evidence_ids[]` and `counterargument_ids[]` as a convenience cache; the source of truth for listing evidence is still the `evidence` collection.

## 0.8 Scoring (proposed framework — do not claim scientific validation)

**Evidence score** (`backend/app/services/scoring.py`):

```
Evidence Score = Reliability × Relevance × Independence × Recency
```

Values are clipped to [0.0, 1.0]. Example from live seed: reliability 0.5 × relevance 0.55 × independence 0.55 × recency 0.6 = **0.0908**.

**Claim strength (conceptual):** supporting evidence contribution − opposing evidence penalty − counterargument penalty − contradiction penalty, then normalized.

**Debate scores:** average PRO claim confidence vs average CON claim confidence; uncertainty is high when scores are close (live Healthcare debate: pro 0.625, con 0.61, uncertainty 0.985).

## 0.9 Frontend pages (routes)

| Route | Purpose for DA2 |
|-------|-----------------|
| `/` | Landing / problem statement in product language |
| `/dashboard` | Live counts + domain / source charts |
| `/debates` | List debates from MongoDB |
| `/debates/new` | CREATE debate (CRUD) |
| `/debates/:id` | Workspace: claims, evidence, graph, history, synthesis |
| `/search` | Keyword / semantic search |
| `/admin` | Indexes + aggregation JSON (A1, A2, A5) |
| `/query-explorer` | Q1–Q12 execution + timing |
| `/database-health` | CONNECTED, `veritas_db`, counts, latency |
| `/projects/evidence` | Rubric feature map |

## 0.10 How to run (for screenshots)

```powershell
cd c:\Users\NAMAN\Projects\VERITAS
docker compose up -d mongodb
cd backend
.\venv\Scripts\activate
python scripts\indexes.py
python scripts\seed.py
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Second terminal:

```powershell
cd c:\Users\NAMAN\Projects\VERITAS\frontend
npm run dev
```

App: http://127.0.0.1:5173  
Swagger: http://127.0.0.1:8000/docs  

---

# PART A — Updated Project Report (paste into PDF in this order)

Use the headings below as the official DA2 table of contents.

---

## A1. Finalised Problem Statement

### Context

Large language models are often used as **debate chatbots**. A user asks a question; the model produces a fluent PRO/CON answer. When the session ends, three things are typically lost:

1. the **structured argument graph** (which claim is supported by which evidence);  
2. **provenance** (who generated the claim, from which source type, when);  
3. **temporal evolution** (how confidence changed after new evidence).

That design treats a debate as a conversation. It does not treat a debate as a **database object**.

### Research gap (academic wording)

There is a gap between (a) ephemeral LLM conversations and (b) persistent NoSQL representations of evolving, evidence-aware arguments with explainable scores. Existing tools may store chat logs or isolated documents; they rarely store **claims, evidence, contradictions, and history as first-class collections** with aggregation over time.

### Proposed framework

**VERITAS** proposes to represent each debate as a **persistent, evidence-aware, temporal knowledge structure in MongoDB**:

- Question and domain live in `debates`.  
- Positions live in `claims` (`PRO` | `CON`).  
- Support/oppose material lives in `evidence`, linked to `sources`.  
- Attacks live in `counterarguments`.  
- Conflicts live in `contradictions` with an explanation.  
- Every major change appends a snapshot to `debate_history` (history is never deleted).  
- A **proposed scoring framework** computes evidence scores and debate-level PRO/CON confidence.  
- Synthesis **must state uncertainty** (for example: “Current evidence moderately supports this position, but significant uncertainty remains.”).

### What VERITAS does not claim

- It does **not** determine objective truth.  
- It does **not** eliminate hallucinations.  
- Seed data is **not** a peer-reviewed evidence corpus.  
- Formulae are **proposed**, **to be evaluated**, not scientifically proven.

### Scope of Review 2

Review 2 demonstrates **database implementation and application progress**: collections, sample documents, CRUD, ≥10 queries, indexes, aggregations, and a working React–FastAPI–MongoDB pipeline.

---

## A2. Final NoSQL Data Model

**Database name:** `veritas_db`  
**Engine:** MongoDB 7 (document store)  
**Deployment used for this review:** Docker Compose service `mongodb`, container `veritas-mongo`, port `27017`.

### Collection catalogue

| Collection | Role | Cardinality (live seed) |
|------------|------|------------------------:|
| debates | Root debate object | 5 |
| claims | PRO/CON statements | 24 |
| evidence | Support/oppose material | 48 |
| counterarguments | Attacks / qualifications | 24 |
| contradictions | Pairwise claim conflicts | 13 |
| sources | Bibliographic / source catalogue | 22 |
| debate_history | Temporal snapshots | 30 |
| embeddings | Vectors for semantic retrieval | 72 |
| audit_logs | Reserved audit trail | 0 |

`audit_logs` exists in the design and health endpoint; it is unused in seed (count 0). Do not invent documents for it.

### Schema — debates

```json
{
  "_id": "ObjectId",
  "question": "string",
  "domain": "string",
  "description": "string|null",
  "status": "active|completed|archived",
  "created_at": "Date",
  "updated_at": "Date",
  "current_synthesis": {
    "summary": "string|null",
    "confidence": 0.0,
    "pro_score": 0.0,
    "con_score": 0.0,
    "uncertainty": 0.0
  },
  "metadata": {
    "created_by": "string|null",
    "language": "en",
    "development_fixture": true
  }
}
```

### Schema — claims

```json
{
  "_id": "ObjectId",
  "debate_id": "ObjectId",
  "position": "PRO|CON",
  "text": "string",
  "normalized_text": "string",
  "confidence": 0.0,
  "status": "active|challenged|superseded",
  "tags": ["string"],
  "evidence_ids": ["ObjectId"],
  "counterargument_ids": ["ObjectId"],
  "provenance": { "generated_by": "user|ai|retrieval|agent", "source_context": "string|null" },
  "created_at": "Date",
  "updated_at": "Date"
}
```

### Schema — evidence

```json
{
  "_id": "ObjectId",
  "claim_id": "ObjectId",
  "source_id": "ObjectId|null",
  "title": "string",
  "content": "string",
  "source_type": "research_paper|institutional|news|dataset|web|user_provided",
  "supports": true,
  "relevance": 0.0,
  "reliability_score": 0.0,
  "independence_score": 0.0,
  "recency_score": 0.0,
  "evidence_score": 0.0,
  "url": "string|null",
  "published_at": "Date|null",
  "added_at": "Date",
  "provenance": {}
}
```

### Schema — counterarguments, contradictions, sources, history, embeddings

Counterarguments: `claim_id`, `text`, `strength`, `type` (`rebuttal|qualification|counterclaim`), `generated_by`, `created_at`.

Contradictions: `claim_a`, `claim_b`, `strength`, `type` (`direct_contradiction|contextual_disagreement|potential_conflict`), `explanation`, `context_dimensions` (population, geography, methodology, time_period, dataset), `created_at`.

Sources: `title`, `authors[]`, `publisher`, `source_type`, `url`, `published_at`, `reliability`, `metadata`.

History: `debate_id`, `timestamp`, `pro_score`, `con_score`, `confidence`, `evidence_count`, `contradiction_count`, `event_type`, `change_summary`.

Embeddings: `entity_type` (`claim|evidence|counterargument`), `entity_id`, `embedding[]`, `model`, `created_at`.

### Design decisions (write these in your own words in viva)

1. **Embed synthesis** because the dashboard always shows PRO/CON scores with the question.  
2. **Reference evidence** because many evidence items exist per claim and scores are updated independently.  
3. **Reference sources** so one source can theoretically support multiple evidence items.  
4. **Append-only history** so temporal graphs never lose past states.  
5. Flexible `provenance` objects because generators differ.

---

## A3. Database Implementation

### Database name

`veritas_db`

### Connection (application)

Environment (`backend/.env`):

```
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=veritas_db
DEMO_MODE=true
```

Code: `backend/app/database.py` uses a shared `MongoClient`, `ping` via `admin.command("ping")`, and live `count_documents` for health (counts are **never hard-coded**).

Docker: `docker-compose.yml` image `mongo:7`, container name `veritas-mongo`.

### Collections / record types / live counts

Captured from the running instance used for this report:

| Collection | Type of records | Count |
|------------|-----------------|------:|
| debates | Debate documents | 5 |
| claims | Argument claims | 24 |
| evidence | Evidence items | 48 |
| counterarguments | Counterarguments | 24 |
| contradictions | Contradiction pairs | 13 |
| sources | Source catalogue | 22 |
| debate_history | Temporal events | 30 |
| embeddings | Vector documents | 72 |
| audit_logs | Audit (empty) | 0 |
| **Total (listed)** | | **238** |

Health API also reports latency (example ~15 ms on localhost).

### Seeded debate questions (development only)

1. Should AI be used for medical diagnosis? (Healthcare)  
2. Should autonomous vehicles be widely deployed in cities? (Transportation)  
3. Should generative AI be used in university education? (Education)  
4. Should cities impose stricter restrictions on private vehicles? (Environment)  
5. Should AI-generated content require mandatory disclosure? (Technology)  

### Scripts that create the implementation

```
python scripts/indexes.py
python scripts/seed.py
python scripts/counts.py
```

---

## A4. Sample Data

**Caption for every screenshot:** “Development fixture from `scripts/seed.py`. Not experimental evidence.”

### Sample debate (live document)

Database: `veritas_db` · Collection: `debates` · `_id`: `6aaeee47bba2e3c0b46e2e74`

```json
{
  "question": "Should AI be used for medical diagnosis?",
  "domain": "Healthcare",
  "description": "Examining AI-assisted diagnostic tools in clinical settings.",
  "status": "active",
  "current_synthesis": {
    "summary": "Development fixture synthesis — to be evaluated with real evidence corpus.",
    "confidence": 0.6175,
    "pro_score": 0.625,
    "con_score": 0.61,
    "uncertainty": 0.985
  },
  "metadata": {
    "created_by": "seed_script",
    "language": "en",
    "development_fixture": true
  }
}
```

### Sample claim (live)

`_id`: `6aaeee47bba2e3c0b46e2e76` · `debate_id`: `6aaeee47bba2e3c0b46e2e74`

```json
{
  "position": "PRO",
  "text": "Evidence suggests significant benefits in Healthcare contexts when properly validated.",
  "confidence": 0.6,
  "status": "active",
  "tags": ["healthcare"],
  "provenance": {
    "generated_by": "retrieval",
    "source_context": "seed_script",
    "development_fixture": true
  }
}
```

### Sample evidence (live)

```json
{
  "title": "Fixture evidence for PRO claim 1",
  "content": "Development fixture evidence content supporting analysis in Healthcare. Not experimental evidence.",
  "source_type": "research_paper",
  "supports": true,
  "relevance": 0.55,
  "reliability_score": 0.5,
  "independence_score": 0.55,
  "recency_score": 0.6,
  "evidence_score": 0.0908,
  "url": null
}
```

`url` is `null` on purpose: the system **does not fabricate source URLs**.

### How to screenshot sample data

MongoDB Compass: connect `mongodb://localhost:27017` → `veritas_db` → each collection → Documents tab.  
Alternatively mongosh:

```javascript
use veritas_db
db.debates.find().pretty()
db.claims.find().limit(1).pretty()
db.evidence.find().limit(1).pretty()
```

---

## A5. CRUD Operations

Implementation: `backend/app/routes/debates.py`, `claims.py`, `evidence.py`.  
UI CREATE: http://127.0.0.1:5173/debates/new  
API: http://127.0.0.1:8000/docs  

Use a **throwaway** debate for UPDATE/DELETE screenshots so you do not wipe the five seed debates needed for queries.

### Create

**HTTP:** `POST /api/debates`  

**Code (application):**

```python
result = db.debates.insert_one(doc)
record_history_event(debate_id, "debate_created", ...)
```

**mongosh equivalent:**

```javascript
db.debates.insertOne({
  question: "Should VERITAS CRUD be demonstrated?",
  domain: "Technology",
  description: "Throwaway document for DA2 screenshots",
  status: "active",
  created_at: new Date(),
  updated_at: new Date(),
  current_synthesis: { summary: null, confidence: 0, pro_score: 0, con_score: 0, uncertainty: 1 },
  metadata: { created_by: "da2_demo", language: "en", development_fixture: true }
})
```

**Output to screenshot:** Swagger 200 JSON with new `id`, plus UI redirect to debate workspace.

### Read

**HTTP:** `GET /api/debates` and `GET /api/debates/{id}`  

```javascript
db.debates.find().sort({ created_at: -1 })
db.debates.findOne({ _id: ObjectId("6aaeee47bba2e3c0b46e2e74") })
```

**Output:** list with `total: 5` (or 6 after create) and one full document.

### Update

**HTTP:** `PUT /api/debates/{id}` body `{ "status": "completed" }`  

```javascript
db.debates.updateOne(
  { _id: ObjectId("THROWAY_ID") },
  { $set: { status: "completed", updated_at: new Date() } }
)
```

**Output:** document with `"status": "completed"`.

### Delete

**HTTP:** `DELETE /api/debates/{id}`  

Application also deletes related claims, evidence, counterarguments, and history for that debate (cascading cleanup in `delete_debate`).

```javascript
db.debates.deleteOne({ _id: ObjectId("THROWAY_ID") })
```

**Output:** `{ "deleted": true, "id": "..." }` then GET returns 404.

### Claims and evidence CRUD (mention briefly)

- `POST /api/claims` inserts a claim, recalculates strength, writes history.  
- `POST /api/evidence` computes `evidence_score`, pushes `evidence_ids`, updates debate scores.

---

## A6. Important Queries (12)

All implemented in `backend/app/analytics/queries.py` and runnable in:

- UI: http://127.0.0.1:5173/query-explorer  
- API: `GET /api/analytics/queries/q1` … `q12`  
- mongosh: `backend/scripts/query_examples.js`

**Screenshot recipe:** for each query: (1) mongosh or Query Explorer showing the query name, (2) execution time, (3) result JSON.

Replace `DEBATE_ID` with `6aaeee47bba2e3c0b46e2e74` (Healthcare debate) unless you reseed.

### Q1 — Fetch all debates

```javascript
db.debates.find().sort({ created_at: -1 }).limit(50)
```

**Live output:** 5 documents (Healthcare, Transportation, Education, Environment, Technology).

### Q2 — Claims for a debate

```javascript
db.claims.find({ debate_id: ObjectId("6aaeee47bba2e3c0b46e2e74") }).sort({ confidence: -1 })
```

**Live output:** 4 claims (2 PRO, 2 CON) for the medical diagnosis debate.

### Q3 — Compare PRO vs CON confidence (aggregation)

```javascript
db.claims.aggregate([
  { $match: { debate_id: ObjectId("6aaeee47bba2e3c0b46e2e74"), status: { $ne: "superseded" } } },
  { $group: { _id: "$position", avg_confidence: { $avg: "$confidence" }, count: { $sum: 1 } } }
])
```

**Live output:**

```json
[
  { "_id": "CON", "avg_confidence": 0.61, "count": 2 },
  { "_id": "PRO", "avg_confidence": 0.625, "count": 2 }
]
```

### Q4 — Strongest supporting evidence for a claim

```javascript
db.evidence.find({ claim_id: ObjectId("CLAIM_ID"), supports: true }).sort({ evidence_score: -1 }).limit(5)
```

Use a `claim_id` from Q2. **Output:** evidence documents with `supports: true` ranked by `evidence_score`.

### Q5 — Strongest opposing evidence

```javascript
db.evidence.find({ claim_id: ObjectId("CLAIM_ID"), supports: false }).sort({ evidence_score: -1 }).limit(5)
```

Seed inserts two evidence items per claim (one support, one oppose). **Output:** opposing item(s).

### Q6 — High-strength contradictions

Fixture contradiction strengths are **0.35** (`potential_conflict`). A threshold of `0.5` returns **0 documents** (this is a valid result — screenshot it and explain). For a non-empty demo:

```javascript
db.contradictions.find({ strength: { $gte: 0.3 } }).sort({ strength: -1 })
```

**Live:** 13 documents, type `potential_conflict`, strength 0.35.

### Q7 — Average evidence reliability by source type

```javascript
db.evidence.aggregate([
  { $group: { _id: "$source_type", avg_reliability: { $avg: "$reliability_score" }, count: { $sum: 1 } } },
  { $sort: { avg_reliability: -1 } }
])
```

**Live output:**

| source_type | avg_reliability | count |
|-------------|----------------:|------:|
| dataset | 0.80 | 10 |
| news | 0.70 | 10 |
| institutional | 0.6167 | 12 |
| research_paper | 0.5444 | 9 |
| web | 0.50 | 7 |

### Q8 — Debate evolution over time

```javascript
db.debate_history.find({ debate_id: ObjectId("6aaeee47bba2e3c0b46e2e74") }).sort({ timestamp: 1 })
```

**Live:** 6 events per debate (created + five named events). Fields include `pro_score`, `con_score`, `confidence`, `event_type`. UI chart: debate workspace → Temporal Evolution.

### Q9 — Low-confidence claims

```javascript
db.claims.find({ confidence: { $lt: 0.4 }, status: "active" }).sort({ confidence: 1 })
```

Seed confidences are mostly 0.58–0.70, so this may return **empty**. Screenshot empty result and explain the predicate. To show matches, use `$lt: 0.65` for DA2 demo only and state the threshold.

### Q10 — Rank claims by confidence

```javascript
db.claims.find({ status: { $ne: "superseded" } }).sort({ confidence: -1 }).limit(20)
```

**Live top:** claims with `confidence: 0.7`, e.g. PRO “Peer-reviewed studies support cautious but affirmative deployment.”

### Q11 — Evidence-weighted claim score (`$lookup`)

```javascript
db.claims.aggregate([
  { $match: { debate_id: ObjectId("6aaeee47bba2e3c0b46e2e74") } },
  { $lookup: { from: "evidence", localField: "_id", foreignField: "claim_id", as: "evidence_items" } },
  { $addFields: {
      weighted_score: {
        $sum: {
          $map: {
            input: "$evidence_items",
            as: "e",
            in: { $cond: ["$$e.supports", "$$e.evidence_score", { $multiply: ["$$e.evidence_score", -0.5] }] }
          }
        }
      }
    }
  },
  { $sort: { weighted_score: -1 } }
])
```

This is a **cross-collection** query (referencing + aggregation). Screenshot Query Explorer `q11` with the Healthcare debate selected.

### Q12 — Domain statistics

```javascript
db.debates.aggregate([
  { $group: {
      _id: "$domain",
      debate_count: { $sum: 1 },
      avg_confidence: { $avg: "$current_synthesis.confidence" },
      avg_pro: { $avg: "$current_synthesis.pro_score" },
      avg_con: { $avg: "$current_synthesis.con_score" }
    }
  },
  { $sort: { debate_count: -1 } }
])
```

**Live:** one debate per domain; Environment and Transportation avg_confidence **0.645**; Healthcare, Education, Technology **0.6175**.

---

## A7. Indexing

Created by `python scripts/indexes.py`. Verified with `list_indexes()` on the live database.

| Collection | Index name | Keys | Why required | Query that uses it |
|------------|------------|------|----------------|-------------------|
| debates | `domain_1_created_at_-1` | domain ASC, created_at DESC | Filter debates by domain and show newest first | Dashboard / `GET /api/debates?domain=` |
| claims | `debate_id_1_position_1_confidence_-1` | debate_id, position, confidence DESC | Load PRO/CON panels ranked by confidence | Q2, Q3, workspace |
| evidence | `claim_id_1_supports_1_reliability_score_-1_relevance_-1` | claim_id, supports, reliability, relevance | Rank supporting vs opposing evidence | Q4, Q5 |
| contradictions | `strength_-1` | strength DESC | High-strength contradiction scan | Q6 |
| debate_history | `debate_id_1_timestamp_1` | debate_id, timestamp ASC | Timeline in order | Q8 |
| sources | `source_type_1_published_at_-1` | source_type, published_at DESC | Filter catalogue | source listing |
| embeddings | `entity_type_1_entity_id_1` | entity_type, entity_id | Semantic lookup without collection scan | semantic search |
| counterarguments | `claim_id_1` | claim_id | Load attacks for a claim | claim detail |
| (all) | `_id_` | `_id` | Default unique primary key | GET by id |

**Demonstration:** screenshot http://127.0.0.1:5173/admin indexes table **and** Compass Indexes tab. Optional mongosh:

```javascript
db.claims.getIndexes()
db.claims.find({ debate_id: ObjectId("6aaeee47bba2e3c0b46e2e74") }).explain("executionStats")
```

Write one sentence: the compound index supports the equality prefix `debate_id` then sort on `confidence`.

Indexes were **not** created blindly: each matches a documented access pattern.

---

## A8. Aggregation / Advanced Operations

Rubric asks 2–3; the project implements **five** plus Q3/Q7/Q11/Q12.

### A1 — PRO vs CON average confidence

Endpoint: `/api/analytics/aggregations/pro-con-confidence`  
UI: Admin page JSON panel.  
Uses `$match` + `$group` on `claims.position`.

### A2 — Evidence quality by source type

`$group` on `evidence.source_type` with `$avg` of `reliability_score` and `evidence_score`.  
Live reliability ranking: dataset > news > institutional > research_paper > web.

### A3 — Evidence count per claim

`$group` by `claim_id`, `$sum: 1`, `$avg` evidence_score.

### A4 — Highest-scoring claims

`$sort` confidence DESC, `$limit` 10, `$project` text/position/confidence.

### A5 — Contradiction distribution

**Live:**

```json
[{ "_id": "potential_conflict", "count": 13, "avg_strength": 0.35 }]
```

**Advanced:** Q11 `$lookup` from claims to evidence (join-like operation in MongoDB).

Screenshot Admin aggregations **and** mongosh pipelines.

---

## A9. Application–Database Connectivity

### Pipeline

```
React (TanStack Query)
  → fetch('/api/...')
  → FastAPI route
  → get_db() PyMongo
  → veritas_db collection
  → serialize ObjectId/Date to JSON
  → UI cards/charts
```

### Evidence to screenshot (mandatory)

1. http://127.0.0.1:5173/database-health — **CONNECTED**, database `veritas_db`, collection counts matching Compass.  
2. http://127.0.0.1:5173/dashboard — Total debates **5**, claims **24**, evidence **48**.  
3. http://127.0.0.1:5173/debates — list loaded from `GET /api/debates`.  
4. Open Healthcare debate — PRO/CON from `GET /api/claims/debate/{id}`.  
5. Create debate in UI — new document appears in Compass.  
6. Swagger `/docs` Try-it-out.  
7. Query Explorer execution time + result count.

### Tests proving connectivity

```
cd backend
pytest tests/ -v
```

**Result on this machine:** 11 passed (health, create/get/list/update/delete debate, create claim, list claims, create evidence, aggregations, history, database-summary).

---

## A10. NoSQL Concepts Used

Do **not** paste Wikipedia definitions. Tie each concept to **this** project.

### Flexible schema

`provenance` and `metadata` objects differ by generator. Claims may include `strength_explanation` after recalculation; seed claims may omit it. `url` may be `null`. MongoDB stores these without ALTER TABLE.

### Embedding

`current_synthesis` is embedded in `debates` so one `findOne` returns question + scores for the dashboard header.

### Referencing

Evidence is a separate collection keyed by `claim_id`. Contradictions reference two claims. This avoids huge nested arrays and allows independent updates.

### Indexing

Eight application indexes plus `_id` (see A7). Built for equality + sort patterns actually used by the API.

### Aggregation

`$group`, `$avg`, `$sum`, `$match`, `$sort`, `$lookup`, `$addFields`, `$map`, `$cond` in analytics and Q11.

### Horizontal scalability / distribution (honest)

MongoDB **can** shard collections in production. **This Review 2 deployment is a single Docker node** for a university-scale demo. Do **not** claim you implemented a sharded cluster. State: “architecture is compatible with replica sets/sharding; current evidence is a single-node implementation.”

### Change streams (honest)

Code exists (`backend/app/services/change_streams.py`). Standalone MongoDB does not support change streams; the app uses **fallback**. Do not mark this as completed production.

### Document-oriented modelling

The debate tree is a graph of documents, not normalized 3NF tables.

---

## A11. Current Status

### Completed (Review 2 scope)

- MongoDB `veritas_db` with collections, seed, indexes  
- FastAPI CRUD for debates, claims, evidence  
- 12 named queries + Query Explorer  
- 5 aggregations + Admin page  
- React application connected to MongoDB  
- Evidence scoring, contradiction detection, temporal history  
- Database health page with live counts  
- Backend tests (11 passed)  
- Documentation and evidence table  

### In progress / experimental

- Atlas Vector Search (needs Atlas)  
- Change streams (needs replica set)  
- LLM synthesis (needs `LLM_API_KEY`; fallback works)  

### Pending / future work

- Filling teammate names in contributions  
- GitHub push + commit history screenshot  
- PDF screenshot pack (`screenshots/` folder currently a placeholder)  
- Production hosting  
- Real (non-fixture) evidence corpus  

---

## A12. Individual Contribution

**Fill real names and register numbers before PDF submit.** Faculty will reject placeholders.

Suggested split (edit to match who actually did the work):

| Member (Name, Reg. No.) | Implemented |
|-------------------------|-------------|
| Member 1 | NoSQL model, `indexes.py`, `seed.py`, Compass evidence, collection design |
| Member 2 | FastAPI routes (CRUD), `QueryService` Q1–Q12, aggregations, pytest |
| Member 3 | Scoring, contradiction engine, temporal history, AI fallback pipeline |
| Member 4 | React pages (dashboard, workspace, graph, query explorer, database health), report |

If you are a solo submitter, write: “Individual implementation of database, API, UI, and documentation as listed in the evidence table,” and still itemize modules.

---

# PART B — Evidence of Implementation (how to assemble the PDF appendix)

Faculty: *“Generic explanations of NoSQL concepts will not be considered as evidence.”*  
Every appendix figure must show **your** Compass / Swagger / UI.

## B1. Database evidence

| Figure | Capture |
|--------|---------|
| B1.1 | Compass: connection `localhost:27017`, database `veritas_db` |
| B1.2 | Collection list (8 populated collections) |
| B1.3 | debates document (Healthcare) |
| B1.4 | claims document |
| B1.5 | evidence document |
| B1.6 | `python scripts/counts.py` terminal OR `/database-health` counts |

Caption counts: debates 5, claims 24, evidence 48, counterarguments 24, contradictions 13, sources 22, debate_history 30, embeddings 72.

## B2. Query screenshots (10+)

For Q1–Q12: Query Explorer **or** mongosh. Include **query text + output**. Q9/Q6 empty results are acceptable if you explain the predicate.

## B3. Application screenshots

Landing, dashboard, create debate, debate workspace (PRO/CON + evidence + graph + timeline), admin indexes, database health CONNECTED, query explorer.

## B4. Relevant code snippets (short — not whole files)

Include in appendix:

1. `insert_one` from `routes/debates.py`  
2. Index list from `scripts/indexes.py`  
3. One aggregation from `analytics/queries.py` (Q3 or Q11)  
4. `compute_evidence_score` from `services/scoring.py`  
5. `get_db()` from `database.py`  

## B5. GitHub (currently missing — do this before submit)

The folder is **not yet a git repository**. Every member must submit a link. Run:

```powershell
cd c:\Users\NAMAN\Projects\VERITAS
git init
git add .
git commit -m "feat: VERITAS NoSQL debate database and application for DA2"
```

Create a GitHub repo, `git remote add origin URL`, `git push -u origin main`.

Screenshot: GitHub code tab + **Commits** page. README is already in the project.

Placeholder in report: `GitHub Repository: [ADD REPOSITORY URL]`

## B6. Schema / dataset export

```
GET http://127.0.0.1:8000/api/debates/6aaeee47bba2e3c0b46e2e74/export
```

Save JSON into `data/healthcare_debate_export.json` and attach a screenshot of the file header. Seed script `backend/scripts/seed.py` is the dataset generator.

## B7. Project Evidence Table (submit this table in the PDF)

| Evidence ID | Rubric item | Feature | Implementation location | Screenshot | Status |
|-------------|-------------|---------|-------------------------|------------|--------|
| E01 | A3 / B1 | MongoDB connection | `backend/app/database.py` | database-health CONNECTED | Done |
| E02 | A2 / A3 | Collections + counts | Compass + `scripts/counts.py` | collection list | Done |
| E03 | A4 | Debate documents | `debates` collection | sample debate JSON | Done |
| E04 | A4 | Claim documents | `claims` | sample claim | Done |
| E05 | A4 | Evidence documents | `evidence` | sample evidence | Done |
| E06 | A5 | Create | `POST /api/debates` | Swagger + UI | Done |
| E07 | A5 | Read | `GET /api/debates` | Swagger / debates list | Done |
| E08 | A5 | Update | `PUT /api/debates/{id}` | Swagger | Done |
| E09 | A5 | Delete | `DELETE /api/debates/{id}` | Swagger | Done |
| E10 | A6 / B2 | Queries Q1–Q12 | `analytics/queries.py` + `/query-explorer` | 10+ query outputs | Done |
| E11 | A7 | Indexes | `scripts/indexes.py` + `/admin` | index table | Done |
| E12 | A8 | Aggregations A1–A5 | `analytics/service.py` + `/admin` | aggregation JSON | Done |
| E13 | A9 | Dashboard | `DashboardPage.tsx` | live counts | Done |
| E14 | A9 | Debate workspace | `DebateWorkspacePage.tsx` | PRO/CON + evidence | Done |
| E15 | A9 | Graph + history | React Flow + Recharts | graph, timeline | Done |
| E16 | A10 | Embed vs reference | `docs/data-model.md` | debate vs evidence docs | Done |
| E17 | A11 | Status | `docs/status.md` | this report section | Done |
| E18 | A12 | Contribution | `docs/contributions.md` | filled names | **Fill names** |
| E19 | B5 | GitHub | remote repo | commit history | **Push required** |
| E20 | B6 | Export | `GET /api/debates/{id}/export` | JSON file | Optional attach |

---

## Screenshot capture order (do this in 25 minutes)

1. Compass overview + collections + 3 documents.  
2. `/database-health`, `/dashboard`, `/admin`.  
3. `/query-explorer`: Q1, Q2 (select Healthcare), Q3, Q6 or Q6 with note, Q7, Q8, Q10, Q11, Q12 (nine). Add Swagger Q4/Q5 with claim id (eleven).  
4. `/debates/new` create → workspace. Swagger PUT + DELETE on throwaway id.  
5. GitHub after push.

---

## Cover page text (copy)

**Vellore Institute of Technology**  
School of Computer Science and Engineering  
**BCSE406L – NoSQL Databases**  
Digital Assignment – 2 | Review 2 – Database Implementation & Progress  

**Title:** VERITAS — An Evidence-Aware, Temporal and Explainable Database for Evolving AI Debates  

**Team members:** [Name, Reg. No.] …  
**Faculty:** Dr. S. Geetha  
**Date:** 20 September 2026  

---

## Closing paragraph (report)

VERITAS implements a MongoDB-centred debate database (`veritas_db`) with eight populated collections, hybrid embedding/referencing, eight application indexes, twelve application queries, five aggregations, and a React–FastAPI client that reads and writes the same data. Sample records are development fixtures. Scoring is a proposed framework. Review 2 evidence is generated from this implementation (Compass, Swagger, and the running UI), not from generic NoSQL notes.
