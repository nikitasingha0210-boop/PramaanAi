"""
Compliance rules engine.

Core AI-safety invariant for this module (see PRD §33-34):
    AI CANNOT CREATE EVIDENCE.
Every result below is derived ONLY from (a) fields already extracted
from an uploaded document, or (b) a normalized mock-connector response.
Document text is never treated as instructions — only as data already
reduced to structured fields upstream in the extraction step.

Each rule function returns a `CheckOutcome`, a small deterministic
struct with everything the Evidence Chain needs:
    requirement -> evidence -> verification -> rule -> result ->
    confidence -> (human decides the action).
"""
from dataclasses import dataclass, field
from datetime import datetime, date

from api.connectors.registry import registry
from api.documents.extractors.registry import extract as extract_doc


@dataclass
class CheckOutcome:
    status: str            # pass | mismatch | missing | expiring | review | fail | clear
    source: str | None
    document_value: str | None
    portal_value: str | None
    confidence: float
    risk_level: str        # low | medium | high | critical
    reasons: list[str] = field(default_factory=list)
    rule_fired: str = ""


def _get_doc(documents: list, doc_type_value: str):
    for d in documents:
        if d.doc_type.value == doc_type_value:
            return d
    return None


def check_gstin_match(bidder, requirement, documents) -> CheckOutcome:
    """PAN/GSTIN cross-verification against the live portal — the demo's signature check."""
    doc = _get_doc(documents, "gst_certificate")
    extraction = extract_doc(bidder.name, "gst_certificate")
    doc_value = extraction.fields.get("gstin")
    portal = registry["gstn"].lookup(bidder.name)
    portal_value = portal.fields.get("gstin") if portal.found else None

    if not doc_value:
        return CheckOutcome("missing", "GSTN Mock API", None, portal_value, 0.0, "high",
                             ["No GST certificate uploaded for this bidder."],
                             rule_fired="GSTIN_MATCH: requires an uploaded GST certificate.")
    if not portal.found:
        return CheckOutcome("review", "GSTN Mock API", doc_value, None, 0.4, "medium",
                             ["GSTIN not found in portal records — requires manual verification."],
                             rule_fired="GSTIN_MATCH: portal lookup returned no record.")
    if doc_value.strip().upper() != portal_value.strip().upper():
        diff_pos = next((i for i, (a, b) in enumerate(zip(doc_value, portal_value)) if a != b), None)
        return CheckOutcome(
            "mismatch", "GSTN Mock API", doc_value, portal_value, 0.99, "high",
            [
                f"Document GSTIN '{doc_value}' does not match GSTN portal record '{portal_value}'.",
                f"Discrepancy detected at character position {diff_pos + 1 if diff_pos is not None else '?'}.",
                "A GSTIN mismatch of this kind can indicate a clerical error, an outdated certificate, or a fraudulent document.",
            ],
            rule_fired="GSTIN_MATCH: document.gstin == portal.gstin (case-insensitive, exact).",
        )
    return CheckOutcome("pass", "GSTN Mock API", doc_value, portal_value, 0.98, "low",
                         ["Document GSTIN matches the live GSTN portal record."],
                         rule_fired="GSTIN_MATCH: document.gstin == portal.gstin.")


def check_pan_valid(bidder, requirement, documents) -> CheckOutcome:
    extraction = extract_doc(bidder.name, "pan_card")
    doc_value = extraction.fields.get("pan")
    portal = registry["pan"].lookup(bidder.name)
    portal_value = portal.fields.get("pan") if portal.found else None
    if not doc_value:
        return CheckOutcome("missing", "PAN Mock API", None, portal_value, 0.0, "high",
                             ["No PAN card uploaded."], rule_fired="PAN_VALID: requires uploaded PAN card.")
    if portal.found and doc_value.strip().upper() == portal_value.strip().upper() and portal.fields.get("status") == "Valid":
        return CheckOutcome("pass", "PAN Mock API", doc_value, portal_value, 0.98, "low",
                             ["PAN verified as valid and matches document."],
                             rule_fired="PAN_VALID: document.pan == portal.pan AND portal.status == Valid.")
    return CheckOutcome("review", "PAN Mock API", doc_value, portal_value, 0.5, "medium",
                         ["PAN could not be fully auto-verified."], rule_fired="PAN_VALID: fallback to manual review.")


def check_udyam_valid(bidder, requirement, documents) -> CheckOutcome:
    extraction = extract_doc(bidder.name, "udyam_certificate")
    doc_value = extraction.fields.get("udyam_number")
    portal = registry["udyam"].lookup(bidder.name)
    portal_value = portal.fields.get("udyam_number") if portal.found else None
    if not doc_value:
        return CheckOutcome("missing", "Udyam Mock API", None, portal_value, 0.0, "high",
                             ["No Udyam registration certificate uploaded."],
                             rule_fired="UDYAM_VALID: requires uploaded Udyam certificate.")
    if portal.found and doc_value == portal_value and portal.fields.get("status") == "Active":
        return CheckOutcome("pass", "Udyam Mock API", doc_value, portal_value, 0.97, "low",
                             [f"Udyam registration active, category {portal.fields.get('category')}."],
                             rule_fired="UDYAM_VALID: document.udyam == portal.udyam AND status == Active.")
    return CheckOutcome("review", "Udyam Mock API", doc_value, portal_value, 0.5, "medium",
                         ["Udyam record requires manual verification."], rule_fired="UDYAM_VALID: fallback.")


def check_incorporation_valid(bidder, requirement, documents) -> CheckOutcome:
    extraction = extract_doc(bidder.name, "incorporation_certificate")
    doc_value = extraction.fields.get("cin")
    portal = registry["mca21"].lookup(bidder.name)
    portal_value = portal.fields.get("cin") if portal.found else None
    if not doc_value:
        return CheckOutcome("missing", "MCA21 Mock API", None, portal_value, 0.0, "medium",
                             ["No incorporation certificate uploaded."], rule_fired="INCORPORATION_VALID: requires document.")
    if portal.found and doc_value == portal_value and portal.fields.get("status") == "Active":
        return CheckOutcome("pass", "MCA21 Mock API", doc_value, portal_value, 0.96, "low",
                             ["Company incorporation active and matches MCA21 records."],
                             rule_fired="INCORPORATION_VALID: document.cin == portal.cin AND status == Active.")
    return CheckOutcome("review", "MCA21 Mock API", doc_value, portal_value, 0.5, "medium",
                         ["Incorporation record requires manual verification."], rule_fired="INCORPORATION_VALID: fallback.")


def check_oem_auth_required(bidder, requirement, documents) -> CheckOutcome:
    extraction = extract_doc(bidder.name, "oem_authorization")
    valid_until = extraction.fields.get("valid_until")
    if not valid_until:
        return CheckOutcome("missing", "Document", None, None, 0.0, "high",
                             ["OEM authorization letter not uploaded, but tender requires it for branded equipment."],
                             rule_fired="OEM_AUTH_REQUIRED: requires uploaded OEM authorization document.")
    exp = datetime.fromisoformat(valid_until).date()
    today = date(2026, 9, 4)
    days_left = (exp - today).days
    if days_left < 0:
        return CheckOutcome("fail", "Document", valid_until, None, 0.95, "critical",
                             [f"OEM authorization expired on {valid_until}."],
                             rule_fired="OEM_AUTH_REQUIRED: valid_until < today.")
    if days_left <= 30:
        return CheckOutcome("expiring", "Document", valid_until, None, 0.91, "medium",
                             [f"OEM authorization expires in {days_left} days ({valid_until})."],
                             rule_fired="OEM_AUTH_REQUIRED: valid_until within 30 days of today.")
    return CheckOutcome("pass", "Document", valid_until, None, 0.95, "low",
                         [f"OEM authorization valid through {valid_until}."],
                         rule_fired="OEM_AUTH_REQUIRED: valid_until > today + 30d.")


def check_local_content_declared(bidder, requirement, documents) -> CheckOutcome:
    extraction = extract_doc(bidder.name, "local_content_declaration")
    pct = extraction.fields.get("declared_percentage")
    if not pct:
        return CheckOutcome("missing", None, None, None, 0.0, "high",
                             ["No local-content declaration was submitted — mandatory for this tender."],
                             rule_fired="LOCAL_CONTENT_DECLARED: requires uploaded declaration.")
    min_required = requirement.expected_value or "20"
    if float(pct) >= float(min_required):
        return CheckOutcome("pass", "Document", f"{pct}%", f">= {min_required}%", 0.9, "low",
                             [f"Declared local content {pct}% meets the {min_required}% minimum."],
                             rule_fired="LOCAL_CONTENT_DECLARED: declared_percentage >= expected_value.")
    return CheckOutcome("fail", "Document", f"{pct}%", f">= {min_required}%", 0.9, "high",
                         [f"Declared local content {pct}% is below the required {min_required}%."],
                         rule_fired="LOCAL_CONTENT_DECLARED: declared_percentage < expected_value.")


def check_debarment_clear(bidder, requirement, documents) -> CheckOutcome:
    portal = registry["debarment"].lookup(bidder.name)
    if portal.found and portal.fields.get("debarred"):
        return CheckOutcome("review", "Debarment / Blacklisting Registry (Mock)", None,
                             portal.fields.get("reason"), 0.99, "critical",
                             [portal.fields.get("reason", "Bidder flagged in debarment registry.")],
                             rule_fired="DEBARMENT_CLEAR: portal.debarred == true -> forced manual review.")
    return CheckOutcome("clear", "Debarment / Blacklisting Registry (Mock)", None, "Not debarred", 0.99, "low",
                         ["No active debarment or blacklisting record found."],
                         rule_fired="DEBARMENT_CLEAR: portal.debarred == false.")


def check_startup_india(bidder, requirement, documents) -> CheckOutcome:
    portal = registry["startup_india"].lookup(bidder.name)
    if portal.found and portal.fields.get("registered"):
        return CheckOutcome("pass", "DPIIT / Startup India Mock API", None,
                             portal.fields.get("certificate_no"), 0.95, "low",
                             ["Verified DPIIT / Startup India registration."],
                             rule_fired="STARTUP_INDIA_REGISTERED: portal.registered == true.")
    return CheckOutcome("fail", "DPIIT / Startup India Mock API", None, "Not registered", 0.95, "medium",
                         ["No DPIIT / Startup India registration found."],
                         rule_fired="STARTUP_INDIA_REGISTERED: portal.registered == false.")


def check_epfo_esic(bidder, requirement, documents) -> CheckOutcome:
    portal = registry["epfo_esic"].lookup(bidder.name)
    epfo = portal.fields.get("epfo_registered") if portal.found else False
    esic = portal.fields.get("esic_registered") if portal.found else False
    if epfo and esic:
        return CheckOutcome("pass", "EPFO/ESIC Mock API", None, "Both registered", 0.93, "low",
                             ["EPFO and ESIC registrations both active."],
                             rule_fired="EPFO_ESIC_REGISTERED: epfo AND esic == true.")
    return CheckOutcome("review", "EPFO/ESIC Mock API", None, "Partial", 0.7, "medium",
                         ["One or more of EPFO/ESIC registration could not be confirmed."],
                         rule_fired="EPFO_ESIC_REGISTERED: fallback to manual review.")


def check_experience_min_years(bidder, requirement, documents) -> CheckOutcome:
    extraction = extract_doc(bidder.name, "incorporation_certificate")
    inc_date_str = extraction.fields.get("incorporation_date")
    if not inc_date_str:
        return CheckOutcome("missing", None, None, None, 0.0, "medium",
                             ["Cannot verify relevant experience without incorporation records."],
                             rule_fired="EXPERIENCE_MIN_YEARS: requires incorporation date.")
    inc_date = datetime.fromisoformat(inc_date_str).date()
    years = (date(2026, 9, 4) - inc_date).days / 365.25
    min_years = float(requirement.expected_value or 3)
    if years >= min_years:
        return CheckOutcome("pass", "MCA21 Mock API", f"{years:.1f} yrs", f">= {min_years} yrs", 0.85, "low",
                             [f"Entity has been active for {years:.1f} years, meeting the {min_years}-year minimum."],
                             rule_fired="EXPERIENCE_MIN_YEARS: (today - incorporation_date) >= expected_value.")
    return CheckOutcome("fail", "MCA21 Mock API", f"{years:.1f} yrs", f">= {min_years} yrs", 0.85, "high",
                         [f"Entity has only been active for {years:.1f} years, below the {min_years}-year minimum."],
                         rule_fired="EXPERIENCE_MIN_YEARS: (today - incorporation_date) < expected_value.")


def check_nsic_registered(bidder, requirement, documents) -> CheckOutcome:
    portal = registry["nsic"].lookup(bidder.name)
    if portal.found and portal.fields.get("registered"):
        return CheckOutcome("pass", "NSIC Mock API", None, portal.fields.get("certificate_no"), 0.9, "low",
                             ["NSIC registration confirmed."], rule_fired="NSIC_REGISTERED: portal.registered == true.")
    return CheckOutcome("fail", "NSIC Mock API", None, "Not registered", 0.9, "medium",
                         ["No NSIC registration on record."], rule_fired="NSIC_REGISTERED: portal.registered == false.")


# Registry mapping requirement.key -> check function.
# This is the single place new requirement types are wired up.
CHECKS = {
    "GSTIN_MATCH": check_gstin_match,
    "PAN_VALID": check_pan_valid,
    "UDYAM_VALID": check_udyam_valid,
    "INCORPORATION_VALID": check_incorporation_valid,
    "OEM_AUTH_REQUIRED": check_oem_auth_required,
    "LOCAL_CONTENT_DECLARED": check_local_content_declared,
    "DEBARMENT_CLEAR": check_debarment_clear,
    "STARTUP_INDIA_REGISTERED": check_startup_india,
    "EPFO_ESIC_REGISTERED": check_epfo_esic,
    "EXPERIENCE_MIN_YEARS": check_experience_min_years,
    "NSIC_REGISTERED": check_nsic_registered,
}
