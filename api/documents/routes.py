import json

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from api.db.session import get_db
from api.deps import require_permission
from api.auth.models import User
from api.tenders.models import BidderSubmission
from api.documents.models import Document, DocumentType
from api.documents.pipeline import ingest_document, UploadValidationError
from api.compliance.evidence import run_evaluation
from api.audit import service as audit_service

router = APIRouter(prefix="/documents", tags=["documents"])


def _serialize(d: Document) -> dict:
    return {
        "id": d.id, "submission_id": d.submission_id, "doc_type": d.doc_type.value,
        "filename": d.filename, "status": d.status.value, "confidence": d.confidence,
        "extracted_fields": json.loads(d.extracted_fields_json or "{}"),
        "uploaded_at": d.uploaded_at.isoformat(),
    }


@router.post("/upload")
async def upload_document(
    submission_id: str = Form(...),
    doc_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("document:upload")),
):
    submission = db.get(BidderSubmission, submission_id)
    if not submission:
        raise HTTPException(404, "Submission not found")
    try:
        dt = DocumentType(doc_type)
    except ValueError:
        raise HTTPException(400, f"Unknown document type '{doc_type}'")

    content = await file.read()
    try:
        document = ingest_document(db, submission, dt, file.filename, content)
    except UploadValidationError as e:
        raise HTTPException(400, str(e))

    audit_service.record(db, user, "document.upload", "document", document.id,
                          tender_id=submission.tender_id, bidder_id=submission.bidder_id,
                          new_value=document.status.value,
                          reason=f"Uploaded {doc_type} ({document.filename}).")

    run_evaluation(db, submission)
    return _serialize(document)


@router.get("/submission/{submission_id}")
def list_documents(submission_id: str, db: Session = Depends(get_db),
                    user: User = Depends(require_permission("document:read"))):
    docs = db.query(Document).filter(Document.submission_id == submission_id).all()
    return [_serialize(d) for d in docs]


@router.get("/{document_id}")
def get_document(document_id: str, db: Session = Depends(get_db),
                  user: User = Depends(require_permission("document:read"))):
    d = db.get(Document, document_id)
    if not d:
        raise HTTPException(404, "Document not found")
    return _serialize(d)
