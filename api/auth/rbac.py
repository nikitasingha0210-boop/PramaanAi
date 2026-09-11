"""
Role-based access control.

Each role maps to a set of permission strings. Routes declare the
permission(s) they require via `require_permission` in api/deps.py.
Auditors are intentionally read-only across the entire system.
"""
from api.auth.models import Role

PERMISSIONS: dict[Role, set[str]] = {
    Role.PROCUREMENT_OFFICER: {
        "tender:create", "tender:read", "tender:update_own",
        "requirement:extract", "requirement:confirm",
        "document:upload", "document:read",
        "compliance:read",
        "evidence:read",
        "action:request_clarification", "action:comment", "action:escalate",
        "audit:read", "analytics:read",
    },
    Role.PROCUREMENT_ADMIN: {
        "tender:create", "tender:read", "tender:update", "tender:delete",
        "requirement:extract", "requirement:confirm",
        "document:upload", "document:read",
        "compliance:read", "compliance:override",
        "evidence:read",
        "action:request_clarification", "action:comment", "action:escalate",
        "user:manage", "audit:read", "analytics:read",
    },
    Role.COMPLIANCE_REVIEWER: {
        "tender:read",
        "document:upload", "document:read",
        "compliance:read", "compliance:override",
        "evidence:read",
        "action:request_clarification", "action:comment",
        "action:approve_finding", "action:reject_finding", "action:mark_false_positive",
        "audit:read", "analytics:read",
    },
    Role.DEPARTMENT_ADMIN: {
        "tender:create", "tender:read", "tender:update", "tender:delete",
        "requirement:extract", "requirement:confirm",
        "document:read",
        "compliance:read", "compliance:override",
        "evidence:read",
        "action:escalate", "action:comment",
        "user:manage", "analytics:read",
    },
    Role.AUDIT_OFFICER: {
        "tender:read", "document:read", "compliance:read", "evidence:read",
        "audit:read", "analytics:read",
    },
    Role.SENIOR_APPROVING_AUTHORITY: {
        "tender:read", "document:read", "compliance:read", "evidence:read",
        "action:finalize_review", "action:approve_finding", "action:reject_finding",
        "action:escalate", "action:comment",
        "analytics:read", "audit:read",
    },
}


def has_permission(role: Role, permission: str) -> bool:
    return permission in PERMISSIONS.get(role, set())
