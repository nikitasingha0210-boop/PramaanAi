from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.db.session import get_db
from api.deps import require_permission
from api.auth.models import User
from api.audit.models import AuditEvent

router = APIRouter(prefix="/audit", tags=["audit"])


def _serialize(e: AuditEvent) -> dict:
    return {
        "id": e.id, "actor_name": e.actor_name, "actor_role": e.actor_role, "action": e.action,
        "entity_type": e.entity_type, "entity_id": e.entity_id,
        "tender_id": e.tender_id, "bidder_id": e.bidder_id, "requirement_key": e.requirement_key,
        "old_value": e.old_value, "new_value": e.new_value, "reason": e.reason,
        "evidence_ref": e.evidence_ref, "override": e.override, "comment": e.comment,
        "created_at": e.created_at.isoformat(),
    }


@router.get("")
def list_audit_events(
    tender_id: str | None = None,
    bidder_id: str | None = None,
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("audit:read")),
):
    q = db.query(AuditEvent)
    if tender_id:
        q = q.filter(AuditEvent.tender_id == tender_id)
    if bidder_id:
        q = q.filter(AuditEvent.bidder_id == bidder_id)
    events = q.order_by(AuditEvent.created_at.desc()).limit(limit).all()
    return [_serialize(e) for e in events]
