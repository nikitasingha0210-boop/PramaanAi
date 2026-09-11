import { useEffect, useState } from 'react';
import {
  X, FileText, Globe2, GitCompareArrows, ScrollText, ShieldAlert,
  CheckCircle2, XCircle, MessageSquareWarning, FlagOff, ArrowUpCircle, Loader2,
} from 'lucide-react';
import { api } from '../lib/api';
import { useAuth } from '../context/AuthContext';
import { getPermissions } from '../lib/permissions';
import { RiskBadge, ConfidenceMeter, StatusPill } from './StatusPrimitives';
import { DiffValue } from '../lib/diff';

// `permission` maps each action to its key in lib/permissions.js — this is
// the single place action visibility is decided (frontend UI only; the
// backend enforces its own permissions independently, see api/auth/rbac.py).
const ACTIONS = [
  { key: 'approve', label: 'Approve finding', icon: CheckCircle2, tone: 'success', permission: 'approve' },
  { key: 'reject', label: 'Reject finding', icon: XCircle, tone: 'danger', needsReason: true, permission: 'reject' },
  { key: 'override', label: 'Override', icon: ShieldAlert, tone: 'warning', needsReason: true, permission: 'override' },
  { key: 'request_clarification', label: 'Request clarification', icon: MessageSquareWarning, tone: 'verify', permission: 'request_clarification' },
  { key: 'mark_false_positive', label: 'Mark false positive', icon: FlagOff, tone: 'mist', permission: 'mark_false_positive' },
  { key: 'escalate', label: 'Escalate', icon: ArrowUpCircle, tone: 'seal', permission: 'escalate' },
];

const TONE_CLASSES = {
  success: 'border-success-500/30 text-success-400 hover:bg-success-500/10',
  danger: 'border-danger-500/30 text-danger-400 hover:bg-danger-500/10',
  warning: 'border-warning-500/30 text-warning-400 hover:bg-warning-500/10',
  verify: 'border-verify-500/30 text-verify-400 hover:bg-verify-500/10',
  seal: 'border-seal-500/30 text-seal-400 hover:bg-seal-500/10',
  mist: 'border-ink-600 text-mist-400 hover:bg-ink-800',
};

export default function EvidenceViewer({ resultId, onClose, onActionDone }) {
  const { user } = useAuth();
  const permissions = getPermissions(user?.role);
  const visibleActions = ACTIONS.filter((a) => permissions[a.permission]);

  const [data, setData] = useState(null);
  const [pendingAction, setPendingAction] = useState(null);
  const [reason, setReason] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [revealed, setRevealed] = useState(false);

  useEffect(() => {
    setRevealed(false);
    api.getEvidence(resultId).then((d) => {
      setData(d);
      setTimeout(() => setRevealed(true), 120);
    });
  }, [resultId]);

  async function submitAction(actionKey) {
    setSubmitting(true);
    try {
      await api.takeAction(resultId, actionKey, { reason: reason || undefined, comment: reason || undefined });
      setPendingAction(null);
      setReason('');
      const fresh = await api.getEvidence(resultId);
      setData(fresh);
      onActionDone?.();
    } finally {
      setSubmitting(false);
    }
  }

  const res = data?.result;
  const isMismatch = res?.status === 'mismatch';

  return (
    <div className="fixed inset-0 z-[200] flex justify-end bg-black/70 backdrop-blur-sm" onClick={onClose}>
      <div
        onClick={(e) => e.stopPropagation()}
        className="h-full w-full max-w-lg overflow-y-auto border-l border-ink-600 bg-ink-900 shadow-2xl animate-rise-in"
        style={{ animationDuration: '0.35s' }}
      >
        {!data ? (
          <div className="flex h-full items-center justify-center text-mist-600">
            <Loader2 className="animate-spin" />
          </div>
        ) : (
          <div className="p-6">
            <div className="mb-5 flex items-start justify-between">
              <div>
                <p className="text-[11px] uppercase tracking-wide text-mist-600">Evidence Viewer</p>
                <h3 className="mt-0.5 font-display text-[17px] font-bold text-mist-100">{res.requirement_label}</h3>
              </div>
              <button onClick={onClose} className="text-mist-600 hover:text-mist-300"><X size={18} /></button>
            </div>

            <div className="mb-5 flex flex-wrap items-center gap-2">
              <StatusPill status={res.status} size="md" />
              <RiskBadge level={res.risk_level} />
              {res.mandatory && <span className="rounded-md border border-ink-600 px-2 py-0.5 text-[11px] text-mist-400">Mandatory</span>}
            </div>

            {/* Document vs Portal comparison — the wow moment */}
            <div className="mb-5 space-y-3">
              <p className="flex items-center gap-1.5 text-[11.5px] font-medium uppercase tracking-wide text-mist-600">
                <GitCompareArrows size={13} /> Document vs. portal record
              </p>
              <div className={`grid grid-cols-2 gap-3 rounded-xl border p-4 transition-all duration-500 ${
                isMismatch ? (revealed ? 'border-danger-500/50 bg-danger-500/5' : 'border-ink-700 bg-ink-850/60') : 'border-ink-700 bg-ink-850/60'
              }`}>
                <div>
                  <p className="mb-1.5 flex items-center gap-1.5 text-[11px] text-mist-600"><FileText size={12} /> Uploaded document</p>
                  <p className="text-[15px]">
                    {revealed ? (
                      <DiffValue value={res.document_value} compareTo={isMismatch ? res.portal_value : null} />
                    ) : (
                      <span className="font-mono text-mist-500">{res.document_value}</span>
                    )}
                  </p>
                </div>
                <div>
                  <p className="mb-1.5 flex items-center gap-1.5 text-[11px] text-mist-600"><Globe2 size={12} /> {res.source || 'Portal'}</p>
                  <p className="text-[15px]">
                    {revealed ? (
                      <DiffValue value={res.portal_value} compareTo={isMismatch ? res.document_value : null} />
                    ) : (
                      <span className="font-mono text-mist-500">{res.portal_value}</span>
                    )}
                  </p>
                </div>
              </div>
              {isMismatch && revealed && (
                <div className="rounded-lg border border-danger-500/25 bg-danger-500/10 px-3.5 py-2.5 text-[12.5px] text-danger-300 animate-rise-in">
                  Discrepancy detected — the highlighted character differs between the document and the live portal record.
                </div>
              )}
            </div>

            {/* Confidence */}
            <div className="mb-5 flex items-center justify-between rounded-lg border border-ink-700 bg-ink-850/50 px-4 py-3">
              <span className="text-[12.5px] text-mist-400">Confidence</span>
              <ConfidenceMeter value={res.confidence} />
            </div>

            {/* Rule fired */}
            <div className="mb-5">
              <p className="mb-1.5 flex items-center gap-1.5 text-[11.5px] font-medium uppercase tracking-wide text-mist-600">
                <ScrollText size={13} /> Rule applied
              </p>
              <p className="rounded-lg border border-ink-700 bg-ink-850/50 px-3.5 py-2.5 font-mono text-[12px] text-mist-400">
                {res.rule_fired} <span className="text-mist-600">({res.rule_version})</span>
              </p>
            </div>

            {/* Reasons */}
            <div className="mb-6">
              <p className="mb-1.5 text-[11.5px] font-medium uppercase tracking-wide text-mist-600">Why</p>
              <ul className="space-y-1.5">
                {res.reasons.map((r, i) => (
                  <li key={i} className="flex gap-2 text-[13px] text-mist-300">
                    <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-mist-600" /> {r}
                  </li>
                ))}
              </ul>
            </div>

            {/* Human action */}
            {res.resolved ? (
              <div className="rounded-lg border border-success-500/25 bg-success-500/10 px-4 py-3 text-[13px] text-success-400">
                Resolved — {res.human_action?.replaceAll('_', ' ')}
                {res.override_reason && <p className="mt-1 text-mist-400">Reason: {res.override_reason}</p>}
              </div>
            ) : visibleActions.length === 0 ? (
              <div className="rounded-lg border border-ink-700 bg-ink-800/60 px-4 py-3 text-[12.5px] text-mist-500">
                Your role does not have an available action for this finding.
              </div>
            ) : (
              <div>
                <p className="mb-2 text-[11.5px] font-medium uppercase tracking-wide text-mist-600">Human action required</p>
                <div className="grid grid-cols-2 gap-2">
                  {visibleActions.map((a) => (
                    <button
                      key={a.key}
                      onClick={() => (a.needsReason ? setPendingAction(a.key) : submitAction(a.key))}
                      disabled={submitting}
                      className={`flex items-center gap-1.5 rounded-lg border px-3 py-2 text-[12px] font-medium transition ${TONE_CLASSES[a.tone]} disabled:opacity-50`}
                    >
                      <a.icon size={13} /> {a.label}
                    </button>
                  ))}
                </div>

                {pendingAction && (
                  <div className="mt-3 rounded-lg border border-ink-600 bg-ink-850 p-3.5">
                    <p className="mb-2 text-[12px] text-mist-400">Reason required for this action:</p>
                    <textarea
                      rows={2}
                      value={reason}
                      onChange={(e) => setReason(e.target.value)}
                      className="w-full rounded-md border border-ink-600 bg-ink-900/70 px-2.5 py-2 text-[12.5px] text-mist-200 outline-none focus:border-verify-500/60"
                      placeholder="e.g. Verified with department head via phone, discrepancy is a clerical error…"
                    />
                    <div className="mt-2 flex justify-end gap-2">
                      <button onClick={() => setPendingAction(null)} className="rounded-md px-3 py-1.5 text-[12px] text-mist-500 hover:text-mist-300">Cancel</button>
                      <button
                        onClick={() => submitAction(pendingAction)}
                        disabled={!reason.trim() || submitting}
                        className="rounded-md bg-gradient-to-b from-seal-400 to-seal-600 px-3.5 py-1.5 text-[12px] font-semibold text-ink-950 disabled:opacity-50"
                      >
                        Confirm
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
