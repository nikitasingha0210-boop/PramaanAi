import enum
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Text, Float, Boolean, ForeignKey, Enum as SAEnum

from api.db.session import Base
from api.auth.models import gen_id


class ComplianceStatus(str, enum.Enum):
    PASS = "pass"
    MISMATCH = "mismatch"
    MISSING = "missing"
    EXPIRING = "expiring"
    REVIEW = "review"
    FAIL = "fail"
    CLEAR = "clear"


class ComplianceResult(Base):
    """
    The Evidence Chain, materialized as a row:
    Requirement -> Evidence -> Verification -> Rule -> Result -> Confidence -> Human Action
    """
    __tablename__ = "compliance_results"

    id = Column(String, primary_key=True, default=gen_id)
    submission_id = Column(String, ForeignKey("bidder_submissions.id"), nullable=False)
    requirement_id = Column(String, ForeignKey("tender_requirements.id"), nullable=False)

    status = Column(SAEnum(ComplianceStatus), default=ComplianceStatus.REVIEW)
    evidence_document_id = Column(String, ForeignKey("documents.id"), nullable=True)
    source = Column(String, nullable=True)  # e.g. "GSTN Mock API", "Document", "Debarment DB"

    document_value = Column(String, nullable=True)   # value as extracted from the uploaded doc
    portal_value = Column(String, nullable=True)      # value as returned by the mock connector
    confidence = Column(Float, default=0.0)
    risk_level = Column(String, default="low")
    reasons_json = Column(Text, default="[]")  # list[str] explaining the risk/result
    rule_version = Column(String, default="v1")
    rule_fired = Column(String, nullable=True)  # human-readable description of the rule that fired

    # human-in-the-loop state
    human_action = Column(String, nullable=True)  # approve / reject / override / clarification_requested / false_positive / escalated
    override_reason = Column(Text, nullable=True)
    reviewer_comment = Column(Text, nullable=True)
    resolved = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
