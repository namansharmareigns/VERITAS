# VERITAS Data Model

Database: `veritas_db`

## Collections

### debates
Core debate object with embedded `current_synthesis` and `metadata`.

### claims
Referenced by debate_id. Contains evidence_ids and counterargument_ids arrays.

### evidence
Referenced by claim_id and optionally source_id. Stores VERITAS evidence scores.

### counterarguments
Referenced by claim_id.

### contradictions
References two claim ObjectIds with context_dimensions.

### sources
Independent source catalog, referenced by evidence.

### debate_history
Temporal snapshots of debate state changes.

### embeddings
Vector representations for semantic retrieval.

### audit_logs
System audit trail.

## Embed vs Reference

| Embed | Reference |
|-------|-----------|
| current_synthesis | sources |
| metadata | evidence |
| provenance (compact) | claims |
| | contradictions |

## Evidence Score

VERITAS proposed framework:

```
Evidence Score = Reliability × Relevance × Independence × Recency
```

Normalized 0.0–1.0. To be evaluated academically.
