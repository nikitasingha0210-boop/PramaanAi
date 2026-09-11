"""
Compliance scoring.

A numeric score is useful for ranking, but it must never be allowed to
paper over a mandatory failure. If any mandatory requirement is
FAIL/MISMATCH/MISSING and unresolved, the submission is surfaced as
"NOT QUALIFIED — PENDING OFFICER REVIEW" regardless of its numeric
score (PRD §21).
"""
PASS_LIKE = {"pass", "clear"}
BLOCKING = {"fail", "mismatch", "missing"}


def compute_score(results: list, requirements: list) -> dict:
    req_by_id = {r.id: r for r in requirements}
    total_weight = sum(r.weight for r in requirements) or 1.0
    earned = 0.0
    mandatory_blocking = []
    unresolved_review = []

    for res in results:
        req = req_by_id.get(res.requirement_id)
        if not req:
            continue
        if res.status.value in PASS_LIKE:
            earned += req.weight
        elif res.status.value == "expiring":
            earned += req.weight * 0.6
        elif res.status.value == "review" and res.resolved:
            earned += req.weight * 0.5

        if req.mandatory and res.status.value in BLOCKING and not res.resolved:
            mandatory_blocking.append(req.label)
        if res.status.value in ("review", "expiring") and not res.resolved:
            unresolved_review.append(req.label)

    score = round(100 * earned / total_weight, 1)

    if mandatory_blocking:
        submission_status = "not_qualified"
        recommendation = "Potentially Non-Compliant"
    elif unresolved_review:
        submission_status = "requires_review"
        recommendation = "Requires Review"
    else:
        submission_status = "likely_compliant"
        recommendation = "Likely Compliant"

    # risk level rolls up from the worst unresolved finding
    risk_order = {"low": 0, "medium": 1, "high": 2, "critical": 3}
    worst = "low"
    for res in results:
        if not res.resolved and risk_order.get(res.risk_level, 0) > risk_order.get(worst, 0):
            worst = res.risk_level

    return {
        "score": score,
        "status": submission_status,
        "recommendation": recommendation,
        "risk_level": worst,
        "mandatory_blocking": mandatory_blocking,
        "unresolved_review": unresolved_review,
    }
