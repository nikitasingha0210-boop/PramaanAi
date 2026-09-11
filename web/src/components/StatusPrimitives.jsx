const STATUS_STYLES = {
  pass: { dot: 'bg-success-400', text: 'text-success-400', bg: 'bg-success-500/10', border: 'border-success-500/25', label: 'Pass' },
  clear: { dot: 'bg-success-400', text: 'text-success-400', bg: 'bg-success-500/10', border: 'border-success-500/25', label: 'Clear' },
  mismatch: { dot: 'bg-danger-400', text: 'text-danger-400', bg: 'bg-danger-500/10', border: 'border-danger-500/25', label: 'Mismatch' },
  fail: { dot: 'bg-danger-400', text: 'text-danger-400', bg: 'bg-danger-500/10', border: 'border-danger-500/25', label: 'Fail' },
  missing: { dot: 'bg-mist-500', text: 'text-mist-400', bg: 'bg-ink-700/60', border: 'border-ink-600', label: 'Missing' },
  expiring: { dot: 'bg-warning-400', text: 'text-warning-400', bg: 'bg-warning-500/10', border: 'border-warning-500/25', label: 'Expiring' },
  review: { dot: 'bg-warning-400', text: 'text-warning-400', bg: 'bg-warning-500/10', border: 'border-warning-500/25', label: 'Review' },

  verified: { dot: 'bg-success-400', text: 'text-success-400', bg: 'bg-success-500/10', border: 'border-success-500/25', label: 'Verified' },
  suspicious: { dot: 'bg-warning-400', text: 'text-warning-400', bg: 'bg-warning-500/10', border: 'border-warning-500/25', label: 'Suspicious' },
  rejected: { dot: 'bg-danger-400', text: 'text-danger-400', bg: 'bg-danger-500/10', border: 'border-danger-500/25', label: 'Rejected' },
  under_review: { dot: 'bg-warning-400', text: 'text-warning-400', bg: 'bg-warning-500/10', border: 'border-warning-500/25', label: 'Under Review' },
  uploaded: { dot: 'bg-verify-400', text: 'text-verify-400', bg: 'bg-verify-500/10', border: 'border-verify-500/25', label: 'Uploaded' },
  processing: { dot: 'bg-verify-400', text: 'text-verify-400', bg: 'bg-verify-500/10', border: 'border-verify-500/25', label: 'Processing' },

  likely_compliant: { dot: 'bg-success-400', text: 'text-success-400', bg: 'bg-success-500/10', border: 'border-success-500/25', label: 'Likely Compliant' },
  requires_review: { dot: 'bg-warning-400', text: 'text-warning-400', bg: 'bg-warning-500/10', border: 'border-warning-500/25', label: 'Requires Review' },
  potentially_non_compliant: { dot: 'bg-danger-400', text: 'text-danger-400', bg: 'bg-danger-500/10', border: 'border-danger-500/25', label: 'Potentially Non-Compliant' },
  not_qualified: { dot: 'bg-danger-400', text: 'text-danger-400', bg: 'bg-danger-500/10', border: 'border-danger-500/25', label: 'Not Qualified — Pending Review' },
  qualified: { dot: 'bg-success-400', text: 'text-success-400', bg: 'bg-success-500/10', border: 'border-success-500/25', label: 'Qualified' },
  submitted: { dot: 'bg-verify-400', text: 'text-verify-400', bg: 'bg-verify-500/10', border: 'border-verify-500/25', label: 'Submitted' },

  draft: { dot: 'bg-mist-500', text: 'text-mist-400', bg: 'bg-ink-700/60', border: 'border-ink-600', label: 'Draft' },
  active: { dot: 'bg-success-400', text: 'text-success-400', bg: 'bg-success-500/10', border: 'border-success-500/25', label: 'Active' },
  under_evaluation: { dot: 'bg-warning-400', text: 'text-warning-400', bg: 'bg-warning-500/10', border: 'border-warning-500/25', label: 'Under Evaluation' },
  closed: { dot: 'bg-mist-500', text: 'text-mist-400', bg: 'bg-ink-700/60', border: 'border-ink-600', label: 'Closed' },
  awarded: { dot: 'bg-seal-400', text: 'text-seal-400', bg: 'bg-seal-500/10', border: 'border-seal-500/25', label: 'Awarded' },
};

export function StatusPill({ status, size = 'sm' }) {
  const s = STATUS_STYLES[status] || { dot: 'bg-mist-500', text: 'text-mist-400', bg: 'bg-ink-700/60', border: 'border-ink-600', label: status };
  const pad = size === 'sm' ? 'px-2 py-0.5 text-[11px]' : 'px-2.5 py-1 text-[12px]';
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border ${s.border} ${s.bg} ${pad} font-medium ${s.text}`}>
      <span className={`h-1.5 w-1.5 rounded-full ${s.dot}`} />
      {s.label}
    </span>
  );
}

const RISK_STYLES = {
  low: { text: 'text-success-400', bg: 'bg-success-500/10', border: 'border-success-500/25', label: 'Low' },
  medium: { text: 'text-warning-400', bg: 'bg-warning-500/10', border: 'border-warning-500/25', label: 'Medium' },
  high: { text: 'text-danger-400', bg: 'bg-danger-500/10', border: 'border-danger-500/25', label: 'High' },
  critical: { text: 'text-danger-300', bg: 'bg-danger-500/20', border: 'border-danger-500/40', label: 'Critical' },
};

export function RiskBadge({ level }) {
  const s = RISK_STYLES[level] || RISK_STYLES.low;
  return (
    <span className={`inline-flex items-center rounded-md border ${s.border} ${s.bg} px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wide ${s.text}`}>
      {s.label} risk
    </span>
  );
}

export function ConfidenceMeter({ value }) {
  const pct = Math.round((value || 0) * 100);
  const color = pct >= 90 ? 'bg-success-400' : pct >= 60 ? 'bg-warning-400' : 'bg-danger-400';
  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 w-14 overflow-hidden rounded-full bg-ink-700">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="font-mono text-[11px] text-mist-400">{pct}%</span>
    </div>
  );
}

export function Card({ className = '', children, ...props }) {
  return (
    <div className={`rounded-xl border border-ink-700 bg-ink-850/70 ${className}`} {...props}>
      {children}
    </div>
  );
}
