import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.db.session import get_db
from api.deps import require_permission
from api.auth.models import User
from api.compliance.models import ComplianceResult
from api.tenders.models import BidderSubmission, TenderRequirement

router = APIRouter(prefix="/alerts", tags=["alerts"])

SEVERITY_MAP = {"critical": "critical", "high": "warning", "medium": "warning", "low": "information"}


@router.get("")
def list_alerts(db: Session = Depends(get_db), user: User = Depends(require_permission("compliance:read"))):
    results = db.query(ComplianceResult).all()
    alerts = []
    for r in results:
        submission = db.get(BidderSubmission, r.submission_id)
        req = db.get(TenderRequirement, r.requirement_id)
        if r.resolved:
            alerts.append({
                "id": r.id, "type": "resolved", "severity": "resolved",
                "title": f"{req.label if req else 'Requirement'} resolved for {submission.bidder.name}",
                "detail": r.human_action, "tender_id": submission.tender_id, "bidder_id": submission.bidder_id,
            })
            continue
        if r.status.value in ("mismatch", "fail", "missing", "expiring", "review"):
            reasons = json.loads(r.reasons_json or "[]")
            alerts.append({
                "id": r.id,
                "type": r.status.value,
                "severity": SEVERITY_MAP.get(r.risk_level, "information"),
                "title": f"{req.label if req else 'Requirement'} — {submission.bidder.name}",
                "detail": reasons[0] if reasons else "",
                "tender_id": submission.tender_id, "bidder_id": submission.bidder_id,
            })
    order = {"critical": 0, "warning": 1, "information": 2, "resolved": 3}
    alerts.sort(key=lambda a: order.get(a["severity"], 9))
    return alerts
