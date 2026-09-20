import json

from fastapi import APIRouter, HTTPException, UploadFile, File

from app.database import get_db
from app.utils.serialization import serialize_doc

router = APIRouter(prefix="/api/import", tags=["import"])


@router.post("/debate")
async def import_debate(file: UploadFile = File(...)):
    """Controlled JSON import for development. Validates structure before insert."""
    if not file.filename or not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="JSON file required")

    content = await file.read()
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    if "debate" not in data:
        raise HTTPException(status_code=400, detail="Import must contain 'debate' object")

    debate = data["debate"]
    required = ["question", "domain"]
    for field in required:
        if field not in debate:
            raise HTTPException(status_code=400, detail=f"Missing required field: {field}")

    db = get_db()
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    doc = {
        "question": debate["question"],
        "domain": debate["domain"],
        "description": debate.get("description"),
        "status": debate.get("status", "active"),
        "created_at": now,
        "updated_at": now,
        "current_synthesis": debate.get("current_synthesis", {
            "summary": None, "confidence": 0.0, "pro_score": 0.0, "con_score": 0.0, "uncertainty": 1.0,
        }),
        "metadata": {**debate.get("metadata", {}), "imported": True},
    }
    result = db.debates.insert_one(doc)
    return {"imported": True, "debate": serialize_doc({**doc, "_id": result.inserted_id})}
