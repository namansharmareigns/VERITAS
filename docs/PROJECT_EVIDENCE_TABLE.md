# Project Evidence Table

| Evidence ID | Rubric | Feature | Implementation Location | Screenshot Required | Status | Notes |
|-------------|--------|---------|------------------------|---------------------|--------|-------|
| E01 | Database | MongoDB connection | backend/app/database.py | 29_database_connectivity | COMPLETED | /database-health page |
| E02 | Database | 9 collections | docs/data-model.md | 02_collection_list | COMPLETED | |
| E03 | Database | Debate documents | backend/app/routes/debates.py | 03_debate_documents | COMPLETED | |
| E04 | Database | Claim documents | backend/app/routes/claims.py | 04_claim_documents | COMPLETED | |
| E05 | Database | Evidence documents | backend/app/routes/evidence.py | 05_evidence_documents | COMPLETED | |
| E06 | CRUD | Create operation | POST /api/debates | 06_create_operation | COMPLETED | |
| E07 | CRUD | Read operation | GET /api/debates | 07_read_operation | COMPLETED | |
| E08 | CRUD | Update operation | PUT /api/debates/{id} | 08_update_operation | COMPLETED | |
| E09 | CRUD | Delete operation | DELETE /api/debates/{id} | 09_delete_operation | COMPLETED | |
| E10 | Queries | Q1-Q12 | backend/app/analytics/queries.py | 10-19 | COMPLETED | Query Explorer UI |
| E11 | Indexes | Index list | backend/scripts/indexes.py | 20_index_list | COMPLETED | /admin page |
| E12 | Aggregations | A1-A5 | backend/app/analytics/service.py | 21-23 | COMPLETED | |
| E13 | Application | Dashboard | frontend/src/pages/DashboardPage.tsx | 24_application_dashboard | COMPLETED | |
| E14 | Application | Debate workspace | frontend/src/pages/DebateWorkspacePage.tsx | 25_application_debate | COMPLETED | |
| E15 | Application | Evidence explorer | frontend/src/components/evidence/ | 26_application_evidence | COMPLETED | |
| E16 | Application | Debate graph | frontend/src/components/graph/ | 27_debate_graph | COMPLETED | |
| E17 | Application | Temporal graph | DebateWorkspacePage history chart | 28_temporal_graph | COMPLETED | |
| E18 | AI | Provider abstraction | backend/app/agents/llm_provider.py | — | COMPLETED | |
| E19 | AI | Fallback mode | backend/app/agents/fallback.py | — | COMPLETED | |
| E20 | Seed | Development fixtures | backend/scripts/seed.py | 01_database_overview | COMPLETED | Marked development_fixture |
