# MongoDB Queries

Implemented in `backend/app/analytics/queries.py` and exposed via `/api/analytics/queries/{name}`.

| ID | Description |
|----|-------------|
| Q1 | Fetch all debates |
| Q2 | Claims for debate |
| Q3 | PRO vs CON confidence |
| Q4 | Strongest supporting evidence |
| Q5 | Strongest opposing evidence |
| Q6 | High-strength contradictions |
| Q7 | Avg reliability by source type |
| Q8 | Debate evolution over time |
| Q9 | Low-confidence claims |
| Q10 | Rank claims by confidence |
| Q11 | Evidence-weighted claim scores |
| Q12 | Domain statistics |

Shell examples: `backend/scripts/query_examples.js`
