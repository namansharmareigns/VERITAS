import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017")
os.environ.setdefault("MONGODB_DB", "veritas_test_db")
os.environ.setdefault("DEMO_MODE", "true")


@pytest.fixture(scope="session")
def mongo_available():
    try:
        from app.database import ping_db
        ping_db()
        return True
    except Exception:
        return False


@pytest.fixture(autouse=True)
def require_mongo(mongo_available):
    if not mongo_available:
        pytest.skip("MongoDB not available on localhost:27017")
