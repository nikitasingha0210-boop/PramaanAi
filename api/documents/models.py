import enum
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Text, Float, ForeignKey, Enum as SAEnum

from api.db.session import Base
from api.auth.models import gen_id


class DocumentType(str, enum.Enum):
    GST_CERTIFICATE = "gst_certificate"
    UDYAM_CERTIFICATE = "udyam_certificate"
    PAN_CARD = "pan_card"
    INCORPORATION_CERTIFICATE = "incorporation_certificate"
    STARTUP_INDIA_CERTIFICATE = "startup_india_certificate"
    OEM_AUTHORIZATION = "oem_authorization"
    LOCAL_CONTENT_DECLARATION = "local_content_declaration"
    EPFO_ESIC_DOCUMENT = "epfo_esic_document"
    NSIC_CERTIFICATE = "nsic_certificate"
    TENDER_DECLARATION = "tender_declaration"
    AFFIDAVIT = "affidavit"


class DocumentStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    VERIFIED = "verified"
    SUSPICIOUS = "suspicious"
    REJECTED = "rejected"
    UNDER_REVIEW = "under_review"


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=gen_id)
    submission_id = Column(String, ForeignKey("bidder_submissions.id"), nullable=False)
    doc_type = Column(SAEnum(DocumentType), nullable=False)
    filename = Column(String, nullable=False)
    storage_path = Column(String, nullable=True)
    status = Column(SAEnum(DocumentStatus), default=DocumentStatus.UPLOADED)
    extracted_fields_json = Column(Text, default="{}")  # JSON string of extracted key/value fields
    confidence = Column(Float, default=0.0)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
