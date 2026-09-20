# VERITAS Architecture

## Layers

1. **Frontend** — React SPA with TanStack Query for data fetching
2. **API** — FastAPI REST endpoints with Pydantic validation
3. **Services** — Scoring, temporal, contradiction, search
4. **Agents** — LLM provider abstraction, debate analysis pipeline
5. **Analytics** — Query service and aggregation pipelines
6. **Database** — MongoDB document store

## Key Flows

### Debate Creation
User → POST /api/debates → MongoDB debates → debate_history event

### AI Analysis
POST /api/ai/analyze → DebateAnalysisPipeline → claims/evidence/counterarguments → contradiction detection → score recalculation → synthesis → history

### Evidence Scoring
Evidence create/update → compute_evidence_score → recalculate claim strength → recalculate debate scores → history snapshot
