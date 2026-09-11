from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.db.session import get_db
from api.deps import require_permission
from api.auth.models import User
from api.tenders.models import Tender, BidderSubmission, TenderStatus
from api.compliance.models import ComplianceResult
from api.documents.models import Document

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview")
def overview(db: Session = Depends(get_db), user: User = Depends(require_permission("compliance:read"))):
    tenders = db.query(Tender).all()
    submissions = db.query(BidderSubmission).all()
    results = db.query(ComplianceResult).all()
    documents = db.query(Document).all()

    active_tenders = len([t for t in tenders if t.status in (TenderStatus.ACTIVE, TenderStatus.UNDER_EVALUATION)])
    under_review = len([s for s in submissions if s.status.value in ("requires_review", "under_review")])
    verified_bidders = len({s.bidder_id for s in submissions if s.compliance_score >= 80})
    pending_verification = len([r for r in results if not r.resolved and r.status.value in ("review", "mismatch", "missing")])
    high_risk = len([s for s in submissions if s.risk_level.value in ("high", "critical")])
    critical_discrepancies = len([r for r in results if r.risk_level == "critical" and not r.resolved])

    status_dist = Counter(s.status.value for s in submissions)
    risk_dist = Counter(s.risk_level.value for s in submissions)

    return {
        "active_tenders": active_tenders,
        "bids_under_review": under_review,
        "verified_bidders": verified_bidders,
        "pending_verification": pending_verification,
        "high_risk_bidders": high_risk,
        "critical_discrepancies": critical_discrepancies,
        "avg_verification_minutes": 6.4,
        "estimated_effort_saved_hours": round(len(documents) * 0.75, 1),
        "compliance_distribution": dict(status_dist),
        "risk_distribution": dict(risk_dist),
        "documents_processed": len(documents),
    }
