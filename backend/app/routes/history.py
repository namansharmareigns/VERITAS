from bson import ObjectId
from fastapi import APIRouter, HTTPException

from app.database import get_db
from app.utils.serialization import serialize_docs

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("/{debate_id}")
def get_debate_history(debate_id: str):
    db = get_db()
    try:
        docs = list(db.debate_history.find({"debate_id": ObjectId(debate_id)}).sort("timestamp", 1))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid debate ID")
    return serialize_docs(docs)
