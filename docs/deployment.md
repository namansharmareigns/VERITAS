# VERITAS Deployment Guide

## Local Development

### Requirements
- Node.js 18+
- Python 3.11+
- MongoDB 6+ (local or Atlas)

### Quick Start (Windows)

```powershell
.\scripts\dev.ps1
```

### Manual Start

**Backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python scripts/indexes.py
python scripts/seed.py
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## MongoDB Atlas

1. Create a free Atlas cluster
2. Set `MONGODB_URI` in `backend/.env` to your connection string
3. Run `python scripts/indexes.py` and `python scripts/seed.py`

## Production Build

```bash
cd frontend && npm run build
cd ../backend && uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Serve `frontend/dist` via nginx or configure FastAPI static files.

## Environment Variables

See `backend/.env.example` for all required variables.

## Health Checks

- API: `GET /api/health`
- Database: `GET /api/analytics/database-health`
- UI: `/database-health`
