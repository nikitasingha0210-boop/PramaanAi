import json

from sqlalchemy.orm import Session

from api.compliance.models import ComplianceResult, ComplianceStatus
from api.compliance.rules import CHECKS
from api.compliance.scoring import compute_score
from api.tenders.models import BidderSubmission, SubmissionStatus, RiskLevel
from api.documents.models import Document


def run_evaluation(db: Session, submission: BidderSubmission) -> BidderSubmission:
    """
    Executes every confirmed requirement's rule against the bidder's
    documents + mock portal data, and (re)materializes the Evidence
    Chain as ComplianceResult rows. Existing human-in-the-loop
    decisions (resolved/human_action/override_reason) are preserved
    across re-evaluation.
    """
    tender = submission.tender
    bidder = submission.bidder
    documents = db.query(Document).filter(Document.submission_id == submission.id).all()

    existing = {
        r.requirement_id: r
        for r in db.query(ComplianceResult).filter(ComplianceResult.submission_id == submission.id).all()
    }

    results = []
    for requirement in tender.requirements:
        if not requirement.confirmed:
            continue
        check_fn = CHECKS.get(requirement.key)
        if not check_fn:
            continue
        outcome = check_fn(bidder, requirement, documents)

        row = existing.get(requirement.id)
        if row is None:
            row = ComplianceResult(submission_id=submission.id, requirement_id=requirement.id)
            db.add(row)

        row.status = ComplianceStatus(outcome.status)
        row.source = outcome.source
        row.document_value = outcome.document_value
        row.portal_value = outcome.portal_value
        row.confidence = outcome.confidence
        row.risk_level = outcome.risk_level
        row.reasons_json = json.dumps(outcome.reasons)
        row.rule_fired = outcome.rule_fired
        row.rule_version = tender.rule_version

        # find matching evidence document if one exists for this requirement's category
        matching_doc = next((d for d in documents if _matches_requirement(d, requirement.key)), None)
        row.evidence_document_id = matching_doc.id if matching_doc else None

        results.append(row)

    db.flush()

    summary = compute_score(results, [r for r in tender.requirements if r.confirmed])
    submission.compliance_score = summary["score"]
    submission.risk_level = RiskLevel(summary["risk_level"])
    submission.ai_recommendation = summary["recommendation"]
    submission.status = SubmissionStatus(summary["status"])

    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


def _matches_requirement(document: Document, requirement_key: str) -> bool:
    mapping = {
        "GSTIN_MATCH": "gst_certificate",
        "PAN_VALID": "pan_card",
        "UDYAM_VALID": "udyam_certificate",
        "INCORPORATION_VALID": "incorporation_certificate",
        "OEM_AUTH_REQUIRED": "oem_authorization",
        "LOCAL_CONTENT_DECLARED": "local_content_declaration",
        "EXPERIENCE_MIN_YEARS": "incorporation_certificate",
        "STARTUP_INDIA_REGISTERED": "startup_india_certificate",
        "NSIC_REGISTERED": "nsic_certificate",
    }
    return document.doc_type.value == mapping.get(requirement_key)
