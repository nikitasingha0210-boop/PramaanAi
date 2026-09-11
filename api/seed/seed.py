"""
Seeds the database with:
  - 6 demo user accounts (one per role)
  - The CPCL Demo Tender 2026 with confirmed requirements
  - 5 fictional bidders covering every PRD demo scenario
  - Uploaded documents for each bidder
  - A fully computed Evidence Chain (ComplianceResult rows) per bidder

Run with:  python -m api.seed.seed
Safe to re-run — it is idempotent (skips anything already present).
"""
import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from api.db.session import Base, engine, SessionLocal
from api.auth.models import User, Role
from api.auth.routes import hash_password
from api.tenders.models import Tender, TenderRequirement, Bidder, BidderSubmission, TenderStatus
from api.documents.models import Document, DocumentType, DocumentStatus
from api.documents.extractors.registry import extract as extract_doc
from api.compliance.evidence import run_evaluation
from api.compliance.requirement_extraction import extract_requirements
from api.audit import service as audit_service

Base.metadata.create_all(bind=engine)

DEMO_USERS = [
    ("procurement.officer@pramaanai.gov.in", "Ananya Verma", Role.PROCUREMENT_OFFICER, "Procurement"),
    ("procurement.admin@pramaanai.gov.in", "Rajeev Malhotra", Role.PROCUREMENT_ADMIN, "Procurement"),
    ("compliance.reviewer@pramaanai.gov.in", "Priya Nair", Role.COMPLIANCE_REVIEWER, "Compliance"),
    ("department.admin@pramaanai.gov.in", "Suresh Iyer", Role.DEPARTMENT_ADMIN, "CPCL Procurement Dept."),
    ("audit.officer@pramaanai.gov.in", "Meera Krishnan", Role.AUDIT_OFFICER, "Internal Audit"),
    ("approving.authority@pramaanai.gov.in", "Vikram Chandra", Role.SENIOR_APPROVING_AUTHORITY, "Executive Office"),
]
DEMO_PASSWORD = "Pramaan@2026"

TENDER_TEXT = (
    "Bidder must have valid Udyam registration and minimum 3 years of relevant supply experience. "
    "A valid and matching GST registration (GSTIN) is mandatory for all bidders. "
    "A valid PAN card matching the bidder's legal name must be submitted. "
    "OEM authorization is mandatory for all branded equipment supplied under this tender. "
    "Bidders must declare local content in compliance with Make in India guidelines, with a minimum "
    "of 20 percent domestic value addition. "
    "The bidder must not be blacklisted or debarred by any central or state government entity. "
    "Certificate of incorporation from MCA21 must be submitted to establish the bidding entity."
)

BIDDERS = [
    {"name": "Compliant Technologies Pvt Ltd", "category": "MSME",
     "pan": "AABCT1234C", "gstin": "27AABCT1234C1Z5", "cin": "U72200MH2015PTC123456", "udyam": "UDYAM-MH-01-1234567"},
    {"name": "ABC Industrial Systems Pvt Ltd", "category": "MSME",
     "pan": "ABCDE1234F", "gstin": "33ABCDE1234F1Z5", "cin": "U29100TN2012PTC087654", "udyam": "UDYAM-TN-03-0098765"},
    {"name": "Bharat Equipment Solutions Pvt Ltd", "category": "MSME",
     "pan": "BEQPS5678G", "gstin": "24BEQPS5678G1Z2", "cin": "U29253GJ2018PTC101234", "udyam": "UDYAM-GJ-02-0054321"},
    {"name": "National Engineering Supplies Pvt Ltd", "category": "MSME",
     "pan": "NESPL9012H", "gstin": "07NESPL9012H1Z8", "cin": "U31300DL2019PTC356789", "udyam": "UDYAM-DL-05-0012398"},
    {"name": "Secure Industrial Systems Pvt Ltd", "category": "Large Enterprise",
     "pan": "SISPL3456K", "gstin": "29SISPL3456K1Z1", "cin": "U28920KA2011PTC061122", "udyam": "UDYAM-KA-04-0076543"},
]

# Which document types each fictional bidder has "uploaded" for the demo
BIDDER_DOC_TYPES = {
    "Compliant Technologies Pvt Ltd": [
        DocumentType.GST_CERTIFICATE, DocumentType.PAN_CARD, DocumentType.UDYAM_CERTIFICATE,
        DocumentType.INCORPORATION_CERTIFICATE, DocumentType.OEM_AUTHORIZATION, DocumentType.LOCAL_CONTENT_DECLARATION,
    ],
    "ABC Industrial Systems Pvt Ltd": [
        DocumentType.GST_CERTIFICATE, DocumentType.PAN_CARD, DocumentType.UDYAM_CERTIFICATE,
        DocumentType.INCORPORATION_CERTIFICATE, DocumentType.OEM_AUTHORIZATION, DocumentType.LOCAL_CONTENT_DECLARATION,
    ],
    "Bharat Equipment Solutions Pvt Ltd": [
        DocumentType.GST_CERTIFICATE, DocumentType.PAN_CARD, DocumentType.UDYAM_CERTIFICATE,
        DocumentType.INCORPORATION_CERTIFICATE, DocumentType.OEM_AUTHORIZATION, DocumentType.LOCAL_CONTENT_DECLARATION,
    ],
    "National Engineering Supplies Pvt Ltd": [
        DocumentType.GST_CERTIFICATE, DocumentType.PAN_CARD, DocumentType.UDYAM_CERTIFICATE,
        DocumentType.INCORPORATION_CERTIFICATE, DocumentType.OEM_AUTHORIZATION,
        # local content declaration intentionally NOT uploaded -> MISSING status
    ],
    "Secure Industrial Systems Pvt Ltd": [
        DocumentType.GST_CERTIFICATE, DocumentType.PAN_CARD, DocumentType.UDYAM_CERTIFICATE,
        DocumentType.INCORPORATION_CERTIFICATE, DocumentType.OEM_AUTHORIZATION, DocumentType.LOCAL_CONTENT_DECLARATION,
    ],
}


def seed_users(db):
    created = []
    for email, name, role, dept in DEMO_USERS:
        if db.query(User).filter(User.email == email).first():
            continue
        u = User(email=email, full_name=name, role=role, department=dept,
                 hashed_password=hash_password(DEMO_PASSWORD))
        db.add(u)
        created.append(u)
    db.commit()
    return created


def seed_tender(db, officer: User) -> Tender:
    existing = db.query(Tender).filter(Tender.code == "CPCL/2026/DEMO/001").first()
    if existing:
        return existing

    tender = Tender(
        code="CPCL/2026/DEMO/001",
        title="Supply, Installation & Commissioning of Industrial Process Equipment",
        department="Chennai Petroleum Corporation Limited (CPCL) — Demo",
        description="Fictional demo tender for evaluating PramaanAI's evidence-driven bidder verification.",
        raw_tender_text=TENDER_TEXT,
        status=TenderStatus.UNDER_EVALUATION,
        assigned_officer_id=officer.id,
    )
    db.add(tender)
    db.commit()
    db.refresh(tender)

    drafts = extract_requirements(TENDER_TEXT)
    for d in drafts:
        req = TenderRequirement(tender_id=tender.id, confirmed=True, **{k: v for k, v in d.items() if k != "confirmed"})
        db.add(req)
    db.commit()
    db.refresh(tender)

    audit_service.record(db, officer, "tender.create", "tender", tender.id, tender_id=tender.id,
                          new_value=tender.title, reason="Seeded CPCL Demo Tender 2026.")
    audit_service.record(db, officer, "requirement.confirm", "tender", tender.id, tender_id=tender.id,
                          new_value=f"{len(tender.requirements)} requirements confirmed",
                          reason="Seed script pre-confirmed extracted requirements for the demo.")
    return tender


def seed_bidders_and_submissions(db, tender: Tender, officer: User):
    for b in BIDDERS:
        bidder = db.query(Bidder).filter(Bidder.name == b["name"]).first()
        if not bidder:
            bidder = Bidder(**b)
            db.add(bidder)
            db.commit()
            db.refresh(bidder)

        submission = db.query(BidderSubmission).filter(
            BidderSubmission.tender_id == tender.id, BidderSubmission.bidder_id == bidder.id
        ).first()
        if submission:
            continue

        submission = BidderSubmission(tender_id=tender.id, bidder_id=bidder.id)
        db.add(submission)
        db.commit()
        db.refresh(submission)

        for doc_type in BIDDER_DOC_TYPES.get(bidder.name, []):
            extraction = extract_doc(bidder.name, doc_type.value)
            doc = Document(
                submission_id=submission.id,
                doc_type=doc_type,
                filename=f"{doc_type.value}_{bidder.name.split()[0].lower()}.pdf",
                storage_path=None,
                status=DocumentStatus.VERIFIED,
                extracted_fields_json=json.dumps(extraction.fields),
                confidence=extraction.confidence,
            )
            db.add(doc)
        db.commit()

        audit_service.record(db, officer, "submission.create", "bidder_submission", submission.id,
                              tender_id=tender.id, bidder_id=bidder.id,
                              new_value="submitted", reason=f"Seeded bid submission for {bidder.name}.")

        run_evaluation(db, submission)


def main():
    db = SessionLocal()
    try:
        users = seed_users(db)
        officer = db.query(User).filter(User.role == Role.PROCUREMENT_OFFICER).first()
        tender = seed_tender(db, officer)
        seed_bidders_and_submissions(db, tender, officer)

        print("Seed complete.")
        print(f"Users created this run: {len(users)}")
        print(f"Demo tender: {tender.code} — {tender.title}")
        print("\nDemo credentials (all use password: %s)" % DEMO_PASSWORD)
        for email, name, role, dept in DEMO_USERS:
            print(f"  {role.value:28s} {email}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
