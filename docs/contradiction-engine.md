# Contradiction Engine

Two-stage workflow in `backend/app/services/contradiction_engine.py`:

## Stage 1 — Semantic Similarity
Jaccard token overlap between claim texts retrieves potentially related PRO/CON pairs.

## Stage 2 — Conflict Analysis
Evaluates negation patterns and topical overlap to classify:

- `direct_contradiction`
- `contextual_disagreement`
- `potential_conflict`

Context dimensions (population, geography, methodology, time_period, dataset) stored for explanation.
