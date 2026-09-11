"""
Mock government portal connectors.

Each connector simulates what the REAL portal would say about a bidder,
independent of what the bidder's uploaded DOCUMENT says. The rules
engine compares document-extracted values against these portal values,
which is what powers discrepancy detection (e.g. the PAN/GSTIN
mismatch "wow moment").

This is fictional demo data only — no real organizations or people.
"""
from api.connectors.base import ConnectorResponse

# Keyed by bidder name (fictional demo orgs only). In a real integration
# this data would come from a live, authorized government API call keyed
# by the identifier the user supplies (PAN, GSTIN, CIN, Udyam number).
MOCK_PORTAL_DB: dict[str, dict] = {
    "Compliant Technologies Pvt Ltd": {
        "gstn": {"gstin": "27AABCT1234C1Z5", "status": "Active", "legal_name": "Compliant Technologies Private Limited"},
        "pan": {"pan": "AABCT1234C", "status": "Valid", "name_match": True},
        "udyam": {"udyam_number": "UDYAM-MH-01-1234567", "category": "Small", "status": "Active"},
        "mca21": {"cin": "U72200MH2015PTC123456", "status": "Active", "incorporation_date": "2015-06-12"},
        "epfo_esic": {"epfo_registered": True, "esic_registered": True},
        "startup_india": {"registered": False},
        "nsic": {"registered": True, "certificate_no": "NSIC/2023/44210"},
        "debarment": {"debarred": False},
    },
    "ABC Industrial Systems Pvt Ltd": {
        # Intentional mismatch: last character differs from the document (wow-moment bidder)
        "gstn": {"gstin": "33ABCDE1234F1Z6", "status": "Active", "legal_name": "ABC Industrial Systems Private Limited"},
        "pan": {"pan": "ABCDE1234F", "status": "Valid", "name_match": True},
        "udyam": {"udyam_number": "UDYAM-TN-03-0098765", "category": "Medium", "status": "Active"},
        "mca21": {"cin": "U29100TN2012PTC087654", "status": "Active", "incorporation_date": "2012-03-22"},
        "epfo_esic": {"epfo_registered": True, "esic_registered": True},
        "startup_india": {"registered": False},
        "nsic": {"registered": False},
        "debarment": {"debarred": False},
    },
    "Bharat Equipment Solutions Pvt Ltd": {
        "gstn": {"gstin": "24BEQPS5678G1Z2", "status": "Active", "legal_name": "Bharat Equipment Solutions Private Limited"},
        "pan": {"pan": "BEQPS5678G", "status": "Valid", "name_match": True},
        "udyam": {"udyam_number": "UDYAM-GJ-02-0054321", "category": "Small", "status": "Active"},
        "mca21": {"cin": "U29253GJ2018PTC101234", "status": "Active", "incorporation_date": "2018-11-02"},
        "epfo_esic": {"epfo_registered": True, "esic_registered": False},
        "startup_india": {"registered": False},
        "nsic": {"registered": True, "certificate_no": "NSIC/2021/33107"},
        "debarment": {"debarred": False},
    },
    "National Engineering Supplies Pvt Ltd": {
        "gstn": {"gstin": "07NESPL9012H1Z8", "status": "Active", "legal_name": "National Engineering Supplies Private Limited"},
        "pan": {"pan": "NESPL9012H", "status": "Valid", "name_match": True},
        "udyam": {"udyam_number": "UDYAM-DL-05-0012398", "category": "Micro", "status": "Active"},
        "mca21": {"cin": "U31300DL2019PTC356789", "status": "Active", "incorporation_date": "2019-07-19"},
        "epfo_esic": {"epfo_registered": True, "esic_registered": True},
        "startup_india": {"registered": True, "certificate_no": "DIPP/2020/88213"},
        "nsic": {"registered": False},
        "debarment": {"debarred": False},
    },
    "Secure Industrial Systems Pvt Ltd": {
        "gstn": {"gstin": "29SISPL3456K1Z1", "status": "Active", "legal_name": "Secure Industrial Systems Private Limited"},
        "pan": {"pan": "SISPL3456K", "status": "Valid", "name_match": True},
        "udyam": {"udyam_number": "UDYAM-KA-04-0076543", "category": "Small", "status": "Active"},
        "mca21": {"cin": "U28920KA2011PTC061122", "status": "Active", "incorporation_date": "2011-01-30"},
        "epfo_esic": {"epfo_registered": True, "esic_registered": True},
        "startup_india": {"registered": False},
        "nsic": {"registered": False},
        "debarment": {"debarred": True, "reason": "Flagged in state debarment list (2024) — pending manual review", "list_ref": "DBL-2024-0417"},
    },
}


def _wrap(bidder_name: str, source_key: str, source_label: str) -> ConnectorResponse:
    record = MOCK_PORTAL_DB.get(bidder_name, {}).get(source_key)
    if record is None:
        return ConnectorResponse(found=False, source=source_label, confidence=0.0,
                                  raw_note="No record found in mock portal for this identifier.")
    return ConnectorResponse(found=True, source=source_label, fields=record,
                              confidence=0.97, as_of="2026-09-04T00:00:00Z")


class GSTNConnector:
    name = "GSTN Mock API"

    def lookup(self, identifier: str, context: dict | None = None) -> ConnectorResponse:
        return _wrap(identifier, "gstn", self.name)


class PANConnector:
    name = "PAN Mock API"

    def lookup(self, identifier: str, context: dict | None = None) -> ConnectorResponse:
        return _wrap(identifier, "pan", self.name)


class UdyamConnector:
    name = "Udyam Mock API"

    def lookup(self, identifier: str, context: dict | None = None) -> ConnectorResponse:
        return _wrap(identifier, "udyam", self.name)


class MCA21Connector:
    name = "MCA21 Mock API"

    def lookup(self, identifier: str, context: dict | None = None) -> ConnectorResponse:
        return _wrap(identifier, "mca21", self.name)


class EPFOESICConnector:
    name = "EPFO/ESIC Mock API"

    def lookup(self, identifier: str, context: dict | None = None) -> ConnectorResponse:
        return _wrap(identifier, "epfo_esic", self.name)


class StartupIndiaConnector:
    name = "DPIIT / Startup India Mock API"

    def lookup(self, identifier: str, context: dict | None = None) -> ConnectorResponse:
        return _wrap(identifier, "startup_india", self.name)


class NSICConnector:
    name = "NSIC Mock API"

    def lookup(self, identifier: str, context: dict | None = None) -> ConnectorResponse:
        return _wrap(identifier, "nsic", self.name)


class DigiLockerConnector:
    name = "DigiLocker Mock API"

    def lookup(self, identifier: str, context: dict | None = None) -> ConnectorResponse:
        # DigiLocker is used to re-fetch/attest a document rather than a registry field
        return ConnectorResponse(found=True, source=self.name, fields={"attested": True},
                                  confidence=0.9, as_of="2026-09-04T00:00:00Z")


class DebarmentConnector:
    name = "Debarment / Blacklisting Registry (Mock)"

    def lookup(self, identifier: str, context: dict | None = None) -> ConnectorResponse:
        return _wrap(identifier, "debarment", self.name)
