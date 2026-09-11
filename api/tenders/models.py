import enum
from datetime import datetime

from sqlalchemy import Column, String, Boolean, DateTime, Text, Float, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship

from api.db.session import Base
from api.auth.models import gen_id


class TenderStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    UNDER_EVALUATION = "under_evaluation"
    CLOSED = "closed"
    AWARDED = "awarded"


class Tender(Base):
    __tablename__ = "tenders"

    id = Column(String, primary_key=True, default=gen_id)
    code = Column(String, unique=True, nullable=False)  # e.g. CPCL/2026/DEMO/001
    title = Column(String, nullable=False)
    department = Column(String, nullable=False)
    description = Column(Text, default="")
    raw_tender_text = Column(Text, default="")  # pasted source text for requirement extraction
    status = Column(SAEnum(TenderStatus), default=TenderStatus.ACTIVE)
    rule_version = Column(String, default="v1")
    assigned_officer_id = Column(String, ForeignKey("users.id"), nullable=True)
    deadline = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    requirements = relationship("TenderRequirement", back_populates="tender", cascade="all, delete-orphan")
    submissions = relationship("BidderSubmission", back_populates="tender", cascade="all, delete-orphan")


class RequirementCategory(str, enum.Enum):
    STATUTORY = "statutory"
    FINANCIAL = "financial"
    TECHNICAL = "technical"
    ELIGIBILITY = "eligibility"
    CERTIFICATION = "certification"
    EXPERIENCE = "experience"
    LOCAL_CONTENT = "local_content"
    OEM = "oem"


class TenderRequirement(Base):
    """
    A single extracted / confirmed compliance rule for a tender.
    `key` matches a rule the compliance engine knows how to evaluate
    (see api/compliance/rules.py CHECKS registry).
    """
    __tablename__ = "tender_requirements"

    id = Column(String, primary_key=True, default=gen_id)
    tender_id = Column(String, ForeignKey("tenders.id"), nullable=False)
    key = Column(String, nullable=False)  # e.g. GST_VALID, PAN_MATCH, OEM_AUTH_REQUIRED
    label = Column(String, nullable=False)  # human readable
    category = Column(SAEnum(RequirementCategory), nullable=False)
    mandatory = Column(Boolean, default=True)
    expected_value = Column(String, nullable=True)  # e.g. "3" for min years experience
    source_text = Column(Text, default="")  # the sentence it was extracted from
    confirmed = Column(Boolean, default=False)  # Checkpoint 1 - officer must confirm
    weight = Column(Float, default=1.0)  # scoring weight, configurable per tender

    tender = relationship("Tender", back_populates="requirements")


class Bidder(Base):
    __tablename__ = "bidders"

    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String, nullable=False)
    category = Column(String, default="MSME")  # MSME / Startup / Large Enterprise
    pan = Column(String, nullable=True)
    gstin = Column(String, nullable=True)
    cin = Column(String, nullable=True)
    udyam = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class SubmissionStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    UNDER_VERIFICATION = "under_verification"
    UNDER_REVIEW = "under_review"
    LIKELY_COMPLIANT = "likely_compliant"
    REQUIRES_REVIEW = "requires_review"
    POTENTIALLY_NON_COMPLIANT = "potentially_non_compliant"
    NOT_QUALIFIED = "not_qualified"
    QUALIFIED = "qualified"


class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BidderSubmission(Base):
    """A bidder's participation / bid within a specific tender."""
    __tablename__ = "bidder_submissions"

    id = Column(String, primary_key=True, default=gen_id)
    tender_id = Column(String, ForeignKey("tenders.id"), nullable=False)
    bidder_id = Column(String, ForeignKey("bidders.id"), nullable=False)
    status = Column(SAEnum(SubmissionStatus), default=SubmissionStatus.SUBMITTED)
    compliance_score = Column(Float, default=0.0)
    risk_level = Column(SAEnum(RiskLevel), default=RiskLevel.LOW)
    ai_recommendation = Column(String, default="Requires Review")
    submitted_at = Column(DateTime, default=datetime.utcnow)

    tender = relationship("Tender", back_populates="submissions")
    bidder = relationship("Bidder")
