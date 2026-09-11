"""
Cross-document matching & recommendation summary.

Builds a plain-language explanation strictly from ComplianceResult
rows already computed by the rules engine (api/compliance/rules.py).
This module never fabricates facts — it only summarizes what the
deterministic checks already found, in the interest of giving the
human reviewer a fast, evidence-linked overview.
"""
import json


def summarize(results: list, requirements_by_id: dict) -> dict:
    failed_rules = []
    uncertain_fields = []
    passed = []

    for r in results:
        req = requirements_by_id.get(r.requirement_id)
        label = req.label if req else r.requirement_id
        if r.status.value in ("fail", "mismatch", "missing") and not r.resolved:
            failed_rules.append({"requirement": label, "reasons": json.loads(r.reasons_json), "confidence": r.confidence})
        elif r.status.value in ("review", "expiring") and not r.resolved:
            uncertain_fields.append({"requirement": label, "reasons": json.loads(r.reasons_json), "confidence": r.confidence})
        elif r.status.value in ("pass", "clear"):
            passed.append(label)

    return {
        "failed_rules": failed_rules,
        "uncertain_fields": uncertain_fields,
        "passed": passed,
    }
