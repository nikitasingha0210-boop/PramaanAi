from sqlalchemy.orm import Session

from api.audit.models import AuditEvent
from api.auth.models import User


def record(
    db: Session,
    actor: User,
    action: str,
    entity_type: str,
    entity_id: str | None = None,
    tender_id: str | None = None,
    bidder_id: str | None = None,
    requirement_key: str | None = None,
    old_value: str | None = None,
    new_value: str | None = None,
    reason: str | None = None,
    evidence_ref: str | None = None,
    override: bool = False,
    comment: str | None = None,
) -> AuditEvent:
    event = AuditEvent(
        actor_user_id=actor.id,
        actor_name=actor.full_name,
        actor_role=actor.role.value,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        tender_id=tender_id,
        bidder_id=bidder_id,
        requirement_key=requirement_key,
        old_value=old_value,
        new_value=new_value,
        reason=reason,
        evidence_ref=evidence_ref,
        override=override,
        comment=comment,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
