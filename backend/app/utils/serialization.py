from datetime import datetime
from typing import Any

from bson import ObjectId


def serialize_doc(doc: dict[str, Any] | None) -> dict[str, Any] | None:
    if doc is None:
        return None
    result: dict[str, Any] = {}
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            result[key] = str(value)
        elif isinstance(value, datetime):
            result[key] = value.isoformat()
        elif isinstance(value, dict):
            result[key] = serialize_doc(value)  # type: ignore[assignment]
        elif isinstance(value, list):
            result[key] = [
                serialize_doc(v) if isinstance(v, dict) else (str(v) if isinstance(v, ObjectId) else v)
                for v in value
            ]
        else:
            result[key] = value
    if "_id" in result:
        result["id"] = result.pop("_id")
    return result


def serialize_docs(docs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [serialize_doc(d) for d in docs if d]


def to_object_id(value: str) -> ObjectId:
    return ObjectId(value)
