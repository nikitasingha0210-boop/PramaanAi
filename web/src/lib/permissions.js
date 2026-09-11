/**
 * Centralized FRONTEND role → UI permission map.
 *
 * IMPORTANT: This controls which action buttons/menu items are RENDERED.
 * It is NOT a security boundary — the backend (api/auth/rbac.py) is the
 * real enforcement point and is completely independent of this file.
 * Hiding a button here only improves the UI for a role; a user who calls
 * the API directly is still governed by the backend's own permission
 * checks. Do not treat this file as authorization.
 *
 * Keys match the exact role strings issued by the backend JWT (see
 * api/auth/models.py Role enum) so this can key off `user.role` directly
 * with no translation layer.
 */

export const ROLE_PERMISSIONS = {
  procurement_officer: {
    request_clarification: true,
    escalate: true,
    approve: false,
    reject: false,
    override: false,
    mark_false_positive: false,
    create_tender: true,
  },
  procurement_admin: {
    request_clarification: true,
    escalate: true,
    approve: true,
    reject: true,
    override: true,
    mark_false_positive: true,
    create_tender: true,
  },
  compliance_reviewer: {
    request_clarification: false,
    escalate: false,
    approve: true,
    reject: true,
    override: true,
    mark_false_positive: false,
    create_tender: false,
  },
  department_admin: {
    request_clarification: true, // "Request" — reuses existing Request Clarification action
    escalate: true,
    approve: true,
    reject: true,
    override: true,
    mark_false_positive: true,
    create_tender: true,
  },
  senior_approving_authority: {
    request_clarification: true,
    escalate: true,
    approve: true,
    reject: true,
    override: true,
    mark_false_positive: true,
    // Not granted tender:create on the backend (api/auth/rbac.py), so the
    // frontend does not surface an action that would only fail on submit.
    create_tender: false,
  },
  // Audit Officer is removed from the frontend entirely (login picker,
  // and — defensively, should a token for this role ever be used — every
  // action here resolves to hidden). The role still exists unmodified on
  // the backend.
  audit_officer: {
    request_clarification: false,
    escalate: false,
    approve: false,
    reject: false,
    override: false,
    mark_false_positive: false,
    create_tender: false,
  },
};

const EMPTY_PERMISSIONS = {
  request_clarification: false,
  escalate: false,
  approve: false,
  reject: false,
  override: false,
  mark_false_positive: false,
  create_tender: false,
};

/** Returns the UI permission set for a given backend role string. */
export function getPermissions(role) {
  return ROLE_PERMISSIONS[role] || EMPTY_PERMISSIONS;
}
