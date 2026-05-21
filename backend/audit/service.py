from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class AuditEntry:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    entity_type: str = ""
    entity_id: str = ""
    action: str = ""
    actor_id: str = "system"
    payload: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))


_audit_log: list[AuditEntry] = []


def log_action(
    *,
    entity_type: str,
    entity_id: str,
    action: str,
    actor_id: str = "system",
    payload: dict | None = None,
) -> AuditEntry:
    entry = AuditEntry(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        actor_id=actor_id,
        payload=payload or {},
    )
    _audit_log.append(entry)
    return entry


def get_audit_log(
    *,
    entity_type: str | None = None,
    entity_id: str | None = None,
    actor_id: str | None = None,
    limit: int = 50,
) -> list[AuditEntry]:
    result = _audit_log
    if entity_type:
        result = [e for e in result if e.entity_type == entity_type]
    if entity_id:
        result = [e for e in result if e.entity_id == entity_id]
    if actor_id:
        result = [e for e in result if e.actor_id == actor_id]
    return sorted(result, key=lambda e: e.created_at, reverse=True)[:limit]


def get_recent_actions(limit: int = 20) -> list[AuditEntry]:
    return sorted(_audit_log, key=lambda e: e.created_at, reverse=True)[:limit]


def serialize_entries(entries: list[AuditEntry]) -> list[dict]:
    return [asdict(entry) for entry in entries]
