import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.db.session import get_db
from api.deps import require_permission
from api.auth.models import User
from api.tenders.models import BidderSubmission, TenderRequirement
from api.documents.models import Document
from api.compliance.models import ComplianceResult
from api.compliance.evidence import run_evaluation
from api.compliance.ai_match import summarize
from api.audit import service as audit_service

router = APIRouter(prefix="/compliance", tags=["compliance"])


def _serialize_result(res: ComplianceResult, req: TenderRequirement) -> dict:
    return {
        "id": res.id,
        "requirement_id": res.requirement_id,
        "requirement_key": req.key if req else None,
        "requirement_label": req.label if req else None,
        "mandatory": req.mandatory if req else None,
        "category": req.category.value if req else None,
        "status": res.status.value,
        "source": res.source,
        "document_value": res.document_value,
        "portal_value": res.portal_value,
        "confidence": res.confidence,
        "risk_level": res.risk_level,
        "reasons": json.loads(res.reasons_json or "[]"),
        "rule_fired": res.rule_fired,
        "rule_version": res.rule_version,
        "evidence_document_id": res.evidence_document_id,
        "human_action": res.human_action,
        "override_reason": res.override_reason,
        "reviewer_comment": res.reviewer_comment,
        "resolved": res.resolved,
        "updated_at": res.updated_at.isoformat(),
    }


@router.get("/submission/{submission_id}/matrix")
def get_matrix(submission_id: str, db: Session = Depends(get_db),
                user: User = Depends(require_permission("compliance:read"))):
    submission = db.get(BidderSubmission, submission_id)
    if not submission:
        raise HTTPException(404, "Submission not found")
    req_by_id = {r.id: r for r in submission.tender.requirements}
    results = db.query(ComplianceResult).filter(ComplianceResult.submission_id == submission_id).all()
    matrix = [_serialize_result(r, req_by_id.get(r.requirement_id)) for r in results]
    summary = summarize(results, req_by_id)
    return {
        "submission_id": submission_id,
        "compliance_score": submission.compliance_score,
        "status": submission.status.value,
        "risk_level": submission.risk_level.value,
        "ai_recommendation": submission.ai_recommendation,
        "matrix": matrix,
        "summary": summary,
    }


@router.post("/submission/{submission_id}/evaluate")
def re_evaluate(submission_id: str, db: Session = Depends(get_db),
                 user: User = Depends(require_permission("compliance:read"))):
    submission = db.get(BidderSubmission, submission_id)
    if not submission:
        raise HTTPException(404, "Submission not found")
    run_evaluation(db, submission)
    return {"status": "re-evaluated", "compliance_score": submission.compliance_score}


@router.get("/results/{result_id}/evidence")
def get_evidence(result_id: str, db: Session = Depends(get_db),
                  user: User = Depends(require_permission("evidence:read"))):
    res = db.get(ComplianceResult, result_id)
    if not res:
        raise HTTPException(404, "Result not found")
    req = db.get(TenderRequirement, res.requirement_id)
    document = db.get(Document, res.evidence_document_id) if res.evidence_document_id else None
    return {
        "result": _serialize_result(res, req),
        "document": {
            "id": document.id, "filename": document.filename, "doc_type": document.doc_type.value,
            "status": document.status.value, "confidence": document.confidence,
            "extracted_fields": json.loads(document.extracted_fields_json or "{}"),
        } if document else None,
    }


# ---------- Human-in-the-loop actions ----------

class ActionPayload(BaseModel):
    comment: str | None = None
    reason: str | None = None  # required for override / reject


ACTION_PERMISSION = {
    "approve": "action:approve_finding",
    "reject": "action:reject_finding",
    "override": "compliance:override",
    "request_clarification": "action:request_clarification",
    "mark_false_positive": "action:mark_false_positive",
    "escalate": "action:escalate",
}


@router.post("/results/{result_id}/action/{action}")
def take_action(result_id: str, action: str, payload: ActionPayload, db: Session = Depends(get_db),
                 user: User = Depends(require_permission("compliance:read"))):
    if action not in ACTION_PERMISSION:
        raise HTTPException(400, f"Unknown action '{action}'")
    from api.auth.rbac import has_permission
    from api.auth.models import Role
    if not has_permission(Role(user.role), ACTION_PERMISSION[action]):
        raise HTTPException(403, f"Role lacks permission for action '{action}'")

    res = db.get(ComplianceResult, result_id)
    if not res:
        raise HTTPException(404, "Result not found")
    if action in ("override", "reject") and not payload.reason:
        raise HTTPException(400, "A reason is required for this action.")

    old_status = res.status.value
    req = db.get(TenderRequirement, res.requirement_id)

    if action == "approve":
        res.resolved = True
        res.human_action = "approved"
    elif action == "reject":
        res.resolved = True
        res.human_action = "rejected"
        res.override_reason = payload.reason
    elif action == "override":
        res.resolved = True
        res.human_action = "overridden"
        res.override_reason = payload.reason
    elif action == "request_clarification":
        res.human_action = "clarification_requested"
    elif action == "mark_false_positive":
        res.resolved = True
        res.human_action = "false_positive"
    elif action == "escalate":
        res.human_action = "escalated"

    if payload.comment:
        res.reviewer_comment = payload.comment

    db.add(res)
    db.commit()
    db.refresh(res)

    submission = db.get(BidderSubmission, res.submission_id)
    audit_service.record(
        db, user, f"compliance.{action}", "compliance_result", res.id,
        tender_id=submission.tender_id, bidder_id=submission.bidder_id,
        requirement_key=req.key if req else None,
        old_value=old_status, new_value=res.status.value,
        reason=payload.reason or payload.comment, comment=payload.comment,
        override=action == "override",
    )

    # Overrides/resolutions can change the aggregate score
    run_evaluation(db, submission)
    return _serialize_result(res, req)
