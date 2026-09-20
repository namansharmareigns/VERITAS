"""Show MongoDB collection record counts."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import get_db, ping_db


def main() -> None:
    ping = ping_db()
    db = get_db()
    collections = [
        "debates", "claims", "evidence", "counterarguments",
        "contradictions", "sources", "debate_history", "embeddings", "audit_logs",
    ]
    print(f"Database: {db.name} (connected={ping['connected']}, latency={ping['latency_ms']}ms)\n")
    total = 0
    for name in collections:
        count = db[name].count_documents({})
        total += count
        print(f"  {name:20} {count}")
    print(f"\n  {'TOTAL':20} {total}")


if __name__ == "__main__":
    main()
