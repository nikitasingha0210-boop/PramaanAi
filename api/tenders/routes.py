from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.db.session import get_db
from api.deps import get_current_user, require_permission
from api.auth.models import User
from api.tenders.models import Tender, TenderRequirement, Bidder, BidderSubmission, TenderStatus
from api.compliance.requirement_extraction import extract_requirements
from api.compliance.evidence import run_evaluation
from api.audit import service as audit_service

router = APIRouter(prefix="/tenders", tags=["tenders"])


# ---------- Schemas ----------

class TenderCreate(BaseModel):
    code: str
    title: str
    department: str
    description: str = ""
    raw_tender_text: str = ""
    deadline: datetime | None = None


class RequirementExtractRequest(BaseModel):
    text: str


class RequirementConfirm(BaseModel):
    requirement_ids: list[str]


class RequirementUpdate(BaseModel):
    label: str | None = None
    mandatory: bool | None = None
    expected_value: str | None = None
    weight: float | None = None


class BidderCreate(BaseModel):
    name: str
    category: str = "MSME"
    pan: str | None = None
    gstin: str | None = None
    cin: str | None = None
    udyam: str | None = None


class SubmissionCreate(BaseModel):
    bidder_id: str


def _serialize_tender(t: Tender) -> dict:
    return {
        "id": t.id, "code": t.code, "title": t.title, "department": t.department,
        "description": t.description, "status": t.status.value, "rule_version": t.rule_version,
        "deadline": t.deadline.isoformat() if t.deadline else None,
        "created_at": t.created_at.isoformat(),
        "requirement_count": len(t.requirements),
        "confirmed_requirement_count": len([r for r in t.requirements if r.confirmed]),
        "submission_count": len(t.submissions),
    }


def _serialize_requirement(r: TenderRequirement) -> dict:
    return {
        "id": r.id, "key": r.key, "label": r.label, "category": r.category.value,
        "mandatory": r.mandatory, "expected_value": r.expected_value,
        "source_text": r.source_text, "confirmed": r.confirmed, "weight": r.weight,
    }


def _serialize_submission(s: BidderSubmission) -> dict:
    return {
        "id": s.id, "tender_id": s.tender_id, "bidder_id": s.bidder_id,
        "bidder_name": s.bidder.name, "bidder_category": s.bidder.category,
        "status": s.status.value, "compliance_score": s.compliance_score,
        "risk_level": s.risk_level.value, "ai_recommendation": s.ai_recommendation,
        "submitted_at": s.submitted_at.isoformat(),
    }


# ---------- Tender CRUD ----------

@router.get("")
def list_tenders(db: Session = Depends(get_db), user: User = Depends(require_permission("tender:read"))):
    tenders = db.query(Tender).order_by(Tender.created_at.desc()).all()
    return [_serialize_tender(t) for t in tenders]


@router.post("")
def create_tender(payload: TenderCreate, db: Session = Depends(get_db),
                   user: User = Depends(require_permission("tender:create"))):
    if db.query(Tender).filter(Tender.code == payload.code).first():
        raise HTTPException(400, "A tender with this code already exists.")
    tender = Tender(**payload.model_dump(), assigned_officer_id=user.id, status=TenderStatus.ACTIVE)
    db.add(tender)
    db.commit()
    db.refresh(tender)
    audit_service.record(db, user, "tender.create", "tender", tender.id, tender_id=tender.id,
                          new_value=tender.title, reason="Tender created.")
    return _serialize_tender(tender)


@router.get("/{tender_id}")
def get_tender(tender_id: str, db: Session = Depends(get_db),
                user: User = Depends(require_permission("tender:read"))):
    tender = db.get(Tender, tender_id)
    if not tender:
        raise HTTPException(404, "Tender not found")
    data = _serialize_tender(tender)
    data["requirements"] = [_serialize_requirement(r) for r in tender.requirements]
    data["submissions"] = [_serialize_submission(s) for s in tender.submissions]
    return data


# ---------- Requirement extraction (Checkpoint 1) ----------

@router.post("/{tender_id}/requirements/extract")
def extract_tender_requirements(tender_id: str, payload: RequirementExtractRequest,
                                 db: Session = Depends(get_db),
                                 user: User = Depends(require_permission("requirement:extract"))):
    tender = db.get(Tender, tender_id)
    if not tender:
        raise HTTPException(404, "Tender not found")

    tender.raw_tender_text = payload.text
    drafts = extract_requirements(payload.text)

    created = []
    existing_keys = {r.key for r in tender.requirements}
    for d in drafts:
        if d["key"] in existing_keys:
            continue
        req = TenderRequirement(tender_id=tender.id, **d)
        db.add(req)
        created.append(req)
    db.commit()

    audit_service.record(db, user, "requirement.extract", "tender", tender.id, tender_id=tender.id,
                          new_value=f"{len(created)} draft requirement(s) extracted",
                          reason="Automated extraction from pasted tender text — pending officer confirmation.")
    return [_serialize_requirement(r) for r in created]


@router.post("/{tender_id}/requirements/confirm")
def confirm_requirements(tender_id: str, payload: RequirementConfirm, db: Session = Depends(get_db),
                          user: User = Depends(require_permission("requirement:confirm"))):
    tender = db.get(Tender, tender_id)
    if not tender:
        raise HTTPException(404, "Tender not found")
    confirmed = []
    for req in tender.requirements:
        if req.id in payload.requirement_ids:
            req.confirmed = True
            confirmed.append(req)
            audit_service.record(db, user, "requirement.confirm", "tender_requirement", req.id,
                                  tender_id=tender.id, requirement_key=req.key,
                                  old_value="draft", new_value="confirmed",
                                  reason="Officer confirmed extracted rule as governing this tender.")
    db.commit()
    # Re-evaluate every existing submission now that new rules are active
    for submission in tender.submissions:
        run_evaluation(db, submission)
    return [_serialize_requirement(r) for r in confirmed]


@router.patch("/{tender_id}/requirements/{requirement_id}")
def update_requirement(tender_id: str, requirement_id: str, payload: RequirementUpdate,
                        db: Session = Depends(get_db),
                        user: User = Depends(require_permission("requirement:confirm"))):
    req = db.get(TenderRequirement, requirement_id)
    if not req or req.tender_id != tender_id:
        raise HTTPException(404, "Requirement not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(req, field, value)
    db.commit()
    db.refresh(req)
    return _serialize_requirement(req)


# ---------- Bidders & submissions ----------

@router.post("/bidders")
def create_bidder(payload: BidderCreate, db: Session = Depends(get_db),
                   user: User = Depends(get_current_user)):
    bidder = Bidder(**payload.model_dump())
    db.add(bidder)
    db.commit()
    db.refresh(bidder)
    return {"id": bidder.id, "name": bidder.name}


@router.get("/bidders/all")
def list_bidders(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    bidders = db.query(Bidder).all()
    return [{"id": b.id, "name": b.name, "category": b.category, "pan": b.pan,
              "gstin": b.gstin, "cin": b.cin, "udyam": b.udyam} for b in bidders]


@router.post("/{tender_id}/submissions")
def create_submission(tender_id: str, payload: SubmissionCreate, db: Session = Depends(get_db),
                       user: User = Depends(require_permission("tender:create"))):
    tender = db.get(Tender, tender_id)
    if not tender:
        raise HTTPException(404, "Tender not found")
    submission = BidderSubmission(tender_id=tender_id, bidder_id=payload.bidder_id)
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return _serialize_submission(submission)


@router.get("/{tender_id}/submissions")
def list_submissions(tender_id: str, db: Session = Depends(get_db),
                      user: User = Depends(require_permission("tender:read"))):
    tender = db.get(Tender, tender_id)
    if not tender:
        raise HTTPException(404, "Tender not found")
    return [_serialize_submission(s) for s in tender.submissions]


@router.get("/submissions/{submission_id}")
def get_submission(submission_id: str, db: Session = Depends(get_db),
                    user: User = Depends(require_permission("tender:read"))):
    submission = db.get(BidderSubmission, submission_id)
    if not submission:
        raise HTTPException(404, "Submission not found")
    data = _serialize_submission(submission)
    data["tender"] = _serialize_tender(submission.tender)
    data["bidder"] = {
        "id": submission.bidder.id, "name": submission.bidder.name,
        "category": submission.bidder.category, "pan": submission.bidder.pan,
        "gstin": submission.bidder.gstin, "cin": submission.bidder.cin, "udyam": submission.bidder.udyam,
    }
    return data
