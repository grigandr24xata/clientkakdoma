from fastapi import APIRouter, Query

from backend.audit.service import get_audit_log, get_recent_actions, serialize_entries

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/")
def list_audit_entries(
    entity_type: str | None = None,
    entity_id: str | None = None,
    actor_id: str | None = None,
    limit: int = Query(default=50, ge=1, le=500),
) -> list[dict]:
    entries = get_audit_log(
        entity_type=entity_type,
        entity_id=entity_id,
        actor_id=actor_id,
        limit=limit,
    )
    return serialize_entries(entries)


@router.get("/recent")
def recent_audit_entries(limit: int = Query(default=20, ge=1, le=500)) -> list[dict]:
    return serialize_entries(get_recent_actions(limit=limit))
