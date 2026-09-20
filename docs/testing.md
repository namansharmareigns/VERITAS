# Testing

## Backend

```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

Requires MongoDB on localhost:27017 (uses `veritas_test_db`).

## Frontend

```bash
cd frontend
npm run build
```

Build verification serves as frontend compile test.
