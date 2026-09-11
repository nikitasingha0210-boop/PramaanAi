"""
Document processing pipeline:
upload -> validation -> classification -> extraction -> confidence ->
compliance evaluation (triggered by the caller after ingest).
"""
import json
import os
import uuid

from sqlalchemy.orm import Session

from api.config import settings
from api.documents.models import Document, DocumentStatus, DocumentType
from api.documents.extractors.registry import extract as extract_doc
from api.tenders.models import BidderSubmission

UPLOAD_DIR = "/home/claude/pramaanai/var/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class UploadValidationError(Exception):
    pass


def validate_upload(filename: str, size_bytes: int) -> None:
    ext = os.path.splitext(filename)[1].lower()
    if ext not in settings.ALLOWED_UPLOAD_EXTENSIONS:
        raise UploadValidationError(f"Unsupported file type '{ext}'. Allowed: {settings.ALLOWED_UPLOAD_EXTENSIONS}")
    max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
    if size_bytes > max_bytes:
        raise UploadValidationError(f"File exceeds the {settings.MAX_UPLOAD_MB}MB limit.")


def ingest_document(
    db: Session,
    submission: BidderSubmission,
    doc_type: DocumentType,
    filename: str,
    content: bytes,
) -> Document:
    validate_upload(filename, len(content))

    stored_name = f"{uuid.uuid4().hex}_{filename}"
    storage_path = os.path.join(UPLOAD_DIR, stored_name)
    with open(storage_path, "wb") as f:
        f.write(content)

    document = Document(
        submission_id=submission.id,
        doc_type=doc_type,
        filename=filename,
        storage_path=storage_path,
        status=DocumentStatus.PROCESSING,
    )
    db.add(document)
    db.flush()

    # Classification + OCR + field extraction (seeded deterministic extraction for the demo)
    extraction = extract_doc(submission.bidder.name, doc_type.value)
    document.extracted_fields_json = json.dumps(extraction.fields)
    document.confidence = extraction.confidence
    document.status = DocumentStatus.VERIFIED if extraction.confidence >= 0.6 else DocumentStatus.UNDER_REVIEW

    db.add(document)
    db.commit()
    db.refresh(document)
    return document
