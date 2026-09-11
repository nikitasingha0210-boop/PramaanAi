"""
Extractor registry.

In production this dispatches uploaded files to real OCR / layout
models per document type. For this prototype, extraction is
deterministic and seeded per fictional demo bidder so the compliance
engine has realistic document-side values to compare against the mock
portal (api/connectors/mock.py) — including the intentional GSTIN
mismatch, an expiring OEM authorization, and a missing local-content
declaration used in the demo script.

IMPORTANT (prompt-injection defense): whatever text appears inside an
uploaded document is treated purely as DATA to extract fields from. It
is never interpreted as an instruction, and it can never alter rules,
prompts, or application behavior — see api/compliance/rules.py.
"""
from datetime import datetime, timedelta

from api.documents.extractors.base import ExtractionResult
from api.documents.models import DocumentType

_NOW = datetime(2026, 9, 4)

DOCUMENT_EXTRACTIONS: dict[str, dict[str, dict]] = {
    "Compliant Technologies Pvt Ltd": {
        DocumentType.GST_CERTIFICATE.value: {"gstin": "27AABCT1234C1Z5", "legal_name": "Compliant Technologies Private Limited"},
        DocumentType.PAN_CARD.value: {"pan": "AABCT1234C", "name": "Compliant Technologies Private Limited"},
        DocumentType.UDYAM_CERTIFICATE.value: {"udyam_number": "UDYAM-MH-01-1234567", "category": "Small"},
        DocumentType.INCORPORATION_CERTIFICATE.value: {"cin": "U72200MH2015PTC123456", "incorporation_date": "2015-06-12"},
        DocumentType.OEM_AUTHORIZATION.value: {"valid_until": (_NOW + timedelta(days=210)).date().isoformat(), "oem_name": "Siemens India"},
        DocumentType.LOCAL_CONTENT_DECLARATION.value: {"declared_percentage": "48", "signed": True},
    },
    "ABC Industrial Systems Pvt Ltd": {
        # Document shows ...1Z5, live portal shows ...1Z6 — single-character discrepancy (wow moment)
        DocumentType.GST_CERTIFICATE.value: {"gstin": "33ABCDE1234F1Z5", "legal_name": "ABC Industrial Systems Private Limited"},
        DocumentType.PAN_CARD.value: {"pan": "ABCDE1234F", "name": "ABC Industrial Systems Private Limited"},
        DocumentType.UDYAM_CERTIFICATE.value: {"udyam_number": "UDYAM-TN-03-0098765", "category": "Medium"},
        DocumentType.INCORPORATION_CERTIFICATE.value: {"cin": "U29100TN2012PTC087654", "incorporation_date": "2012-03-22"},
        DocumentType.OEM_AUTHORIZATION.value: {"valid_until": (_NOW + timedelta(days=180)).date().isoformat(), "oem_name": "ABB Ltd"},
        DocumentType.LOCAL_CONTENT_DECLARATION.value: {"declared_percentage": "35", "signed": True},
    },
    "Bharat Equipment Solutions Pvt Ltd": {
        DocumentType.GST_CERTIFICATE.value: {"gstin": "24BEQPS5678G1Z2", "legal_name": "Bharat Equipment Solutions Private Limited"},
        DocumentType.PAN_CARD.value: {"pan": "BEQPS5678G", "name": "Bharat Equipment Solutions Private Limited"},
        DocumentType.UDYAM_CERTIFICATE.value: {"udyam_number": "UDYAM-GJ-02-0054321", "category": "Small"},
        DocumentType.INCORPORATION_CERTIFICATE.value: {"cin": "U29253GJ2018PTC101234", "incorporation_date": "2018-11-02"},
        # Expires within 21 days of "today" in the demo -> EXPIRING status
        DocumentType.OEM_AUTHORIZATION.value: {"valid_until": (_NOW + timedelta(days=18)).date().isoformat(), "oem_name": "L&T Construction Equipment"},
        DocumentType.LOCAL_CONTENT_DECLARATION.value: {"declared_percentage": "52", "signed": True},
    },
    "National Engineering Supplies Pvt Ltd": {
        DocumentType.GST_CERTIFICATE.value: {"gstin": "07NESPL9012H1Z8", "legal_name": "National Engineering Supplies Private Limited"},
        DocumentType.PAN_CARD.value: {"pan": "NESPL9012H", "name": "National Engineering Supplies Private Limited"},
        DocumentType.UDYAM_CERTIFICATE.value: {"udyam_number": "UDYAM-DL-05-0012398", "category": "Micro"},
        DocumentType.INCORPORATION_CERTIFICATE.value: {"cin": "U31300DL2019PTC356789", "incorporation_date": "2019-07-19"},
        DocumentType.OEM_AUTHORIZATION.value: {"valid_until": (_NOW + timedelta(days=300)).date().isoformat(), "oem_name": "Kirloskar Brothers"},
        # No local content declaration document uploaded at all -> MISSING status
    },
    "Secure Industrial Systems Pvt Ltd": {
        DocumentType.GST_CERTIFICATE.value: {"gstin": "29SISPL3456K1Z1", "legal_name": "Secure Industrial Systems Private Limited"},
        DocumentType.PAN_CARD.value: {"pan": "SISPL3456K", "name": "Secure Industrial Systems Private Limited"},
        DocumentType.UDYAM_CERTIFICATE.value: {"udyam_number": "UDYAM-KA-04-0076543", "category": "Small"},
        DocumentType.INCORPORATION_CERTIFICATE.value: {"cin": "U28920KA2011PTC061122", "incorporation_date": "2011-01-30"},
        DocumentType.OEM_AUTHORIZATION.value: {"valid_until": (_NOW + timedelta(days=240)).date().isoformat(), "oem_name": "Bharat Heavy Electricals"},
        DocumentType.LOCAL_CONTENT_DECLARATION.value: {"declared_percentage": "40", "signed": True},
    },
}


def extract(bidder_name: str, doc_type: str) -> ExtractionResult:
    fields = DOCUMENT_EXTRACTIONS.get(bidder_name, {}).get(doc_type)
    if not fields:
        return ExtractionResult(fields={}, confidence=0.0, authenticity_flags=["no_seeded_extraction"])
    return ExtractionResult(fields=fields, confidence=0.94)
