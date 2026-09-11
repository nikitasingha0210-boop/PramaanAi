"""
Requirement extraction from free-text tender documents.

This performs deterministic, keyword/pattern-based extraction (no
document text is ever treated as an instruction — see PRD §34). Output
is always a set of DRAFT requirements that a human procurement officer
must review and confirm (Checkpoint 1, PRD §13) before they govern a
tender. Nothing extracted here is applied automatically.
"""
import re

PATTERNS: list[tuple[str, str, str, str]] = [
    # (regex, key, label, category)
    (r"udyam", "UDYAM_VALID", "Valid Udyam Registration", "statutory"),
    (r"\bgst\b|gstin", "GSTIN_MATCH", "Valid & Matching GSTIN", "statutory"),
    (r"\bpan\b", "PAN_VALID", "Valid PAN", "statutory"),
    (r"incorporat|certificate of incorporation|\bcin\b", "INCORPORATION_VALID", "Valid Incorporation (MCA21)", "statutory"),
    (r"oem authoriz|original equipment manufacturer", "OEM_AUTH_REQUIRED", "OEM Authorization", "oem"),
    (r"local content|make in india|domestic content", "LOCAL_CONTENT_DECLARED", "Local Content Declaration", "local_content"),
    (r"blacklist|debarr", "DEBARMENT_CLEAR", "Not Blacklisted / Debarred", "eligibility"),
    (r"startup india|dpiit", "STARTUP_INDIA_REGISTERED", "Startup India / DPIIT Registration", "certification"),
    (r"epfo|esic|provident fund", "EPFO_ESIC_REGISTERED", "EPFO / ESIC Registration", "statutory"),
    (r"nsic", "NSIC_REGISTERED", "NSIC Registration", "certification"),
]

EXPERIENCE_RE = re.compile(r"minimum\s+(\d+)\s*(?:\+)?\s*years?", re.IGNORECASE)


def extract_requirements(text: str) -> list[dict]:
    """Returns a list of draft requirement dicts, each with a source_text sentence."""
    sentences = re.split(r"(?<=[.;])\s+", text.strip())
    drafts: list[dict] = []
    seen_keys = set()

    for sentence in sentences:
        lower = sentence.lower()
        for pattern, key, label, category in PATTERNS:
            if key in seen_keys:
                continue
            if re.search(pattern, lower):
                drafts.append({
                    "key": key,
                    "label": label,
                    "category": category,
                    "mandatory": True,
                    "expected_value": None,
                    "source_text": sentence.strip(),
                    "confirmed": False,
                })
                seen_keys.add(key)

        exp_match = EXPERIENCE_RE.search(sentence)
        if exp_match and "EXPERIENCE_MIN_YEARS" not in seen_keys:
            drafts.append({
                "key": "EXPERIENCE_MIN_YEARS",
                "label": f"Minimum {exp_match.group(1)} Years Relevant Experience",
                "category": "experience",
                "mandatory": True,
                "expected_value": exp_match.group(1),
                "source_text": sentence.strip(),
                "confirmed": False,
            })
            seen_keys.add("EXPERIENCE_MIN_YEARS")

    # Debarment check is always applied, even if not explicitly worded in the tender text
    if "DEBARMENT_CLEAR" not in seen_keys:
        drafts.append({
            "key": "DEBARMENT_CLEAR", "label": "Not Blacklisted / Debarred", "category": "eligibility",
            "mandatory": True, "expected_value": None,
            "source_text": "Applied by default to every tender regardless of wording.",
            "confirmed": False,
        })

    return drafts
