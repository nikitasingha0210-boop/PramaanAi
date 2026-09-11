from datetime import datetime

from sqlalchemy import Column, String, DateTime, Text, Boolean, ForeignKey

from api.db.session import Base
from api.auth.models import gen_id


class AuditEvent(Base):
    """
    Append-only audit log. Rows are never updated or deleted by the
    application layer — only inserted. This is enforced at the service
    layer (api/audit/service.py); there is deliberately no update/delete
    route anywhere in the API for this table.
    """
    __tablename__ = "audit_events"

    id = Column(String, primary_key=True, default=gen_id)
    actor_user_id = Column(String, ForeignKey("users.id"), nullable=True)
    actor_name = Column(String, nullable=False)
    actor_role = Column(String, nullable=False)
    action = Column(String, nullable=False)  # e.g. "compliance.override", "document.upload"
    entity_type = Column(String, nullable=False)  # tender / bidder / document / compliance_result
    entity_id = Column(String, nullable=True)

    tender_id = Column(String, nullable=True)
    bidder_id = Column(String, nullable=True)
    requirement_key = Column(String, nullable=True)

    old_value = Column(String, nullable=True)
    new_value = Column(String, nullable=True)
    reason = Column(Text, nullable=True)
    evidence_ref = Column(String, nullable=True)
    override = Column(Boolean, default=False)
    comment = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
