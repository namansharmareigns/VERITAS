"""Graceful change stream monitoring with fallback for local MongoDB."""

import logging
import threading
from typing import Any, Callable

from app.database import get_db

logger = logging.getLogger(__name__)

_stream_active = False
_fallback_mode = True


def start_change_streams(on_event: Callable[[dict[str, Any]], None] | None = None) -> dict[str, Any]:
    """Start change stream listeners or return fallback status."""
    global _stream_active, _fallback_mode

    db = get_db()
    try:
        # Test if change streams are supported
        with db.debates.watch([], max_await_time_ms=1000) as stream:
            stream.close()

        def _watch_collection(collection_name: str) -> None:
            try:
                for change in db[collection_name].watch(full_document="updateLookup"):
                    logger.info("Change stream event on %s: %s", collection_name, change.get("operationType"))
                    if on_event:
                        on_event({"collection": collection_name, **change})
            except Exception as e:
                logger.warning("Change stream on %s stopped: %s", collection_name, e)

        for coll in ["evidence", "claims", "debates"]:
            t = threading.Thread(target=_watch_collection, args=(coll,), daemon=True)
            t.start()

        _stream_active = True
        _fallback_mode = False
        return {"enabled": True, "mode": "change_stream", "collections": ["evidence", "claims", "debates"]}
    except Exception as e:
        logger.info("Change streams unavailable, using fallback: %s", e)
        _stream_active = False
        _fallback_mode = True
        return {"enabled": False, "mode": "fallback", "reason": str(e)}


def get_change_stream_status() -> dict[str, Any]:
    return {"active": _stream_active, "fallback_mode": _fallback_mode}
