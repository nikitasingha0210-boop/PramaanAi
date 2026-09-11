import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { ChevronRight, Building2, RefreshCw, AlertOctagon } from 'lucide-react';
import { api } from '../lib/api';
import { Card, StatusPill, RiskBadge, ConfidenceMeter } from '../components/StatusPrimitives';
import EvidenceViewer from '../components/EvidenceViewer';

const ID_FIELDS = [
  { key: 'pan', label: 'PAN' },
  { key: 'gstin', label: 'GSTIN' },
  { key: 'cin', label: 'CIN' },
  { key: 'udyam', label: 'Udyam' },
];

export default function SubmissionDetail() {
  const { id } = useParams();
  const [submission, setSubmission] = useState(null);
  const [matrix, setMatrix] = useState(null);
  const [activeResultId, setActiveResultId] = useState(null);
  const [reEvaluating, setReEvaluating] = useState(false);

  function refresh() {
    api.getSubmission(id).then(setSubmission);
    api.getMatrix(id).then(setMatrix);
  }
  useEffect(refresh, [id]);

  async function handleReEvaluate() {
    setReEvaluating(true);
    try {
      await api.reEvaluate(id);
      refresh();
    } finally {
      setReEvaluating(false);
    }
  }

  if (!submission || !matrix) return <p className="text-mist-500">Loading…</p>;

  const isNotQualified = matrix.status === 'not_qualified';

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      {/* Breadcrumb */}
      <div className="flex items-center gap-1.5 text-[12px] text-mist-600">
        <span>{submission.tender.code}</span> <ChevronRight size={12} /> <span className="text-mist-400">{submission.bidder_name}</span>
      </div>

      {/* Passport header */}
      <Card className="overflow-hidden p-0">
        <div className="flex flex-col justify-between gap-5 border-b border-ink-700/70 bg-gradient-to-br from-ink-800/60 to-transparent p-6 sm:flex-row sm:items-center">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl border border-seal-500/25 bg-seal-500/10">
              <Building2 size={20} className="text-seal-400" />
            </div>
            <div>
              <p className="text-[11px] uppercase tracking-wide text-mist-600">Compliance Passport</p>
              <h2 className="font-display text-[18px] font-bold text-mist-100">{submission.bidder_name}</h2>
              <p className="text-[12px] text-mist-500">{submission.bidder_category} · {submission.tender.title}</p>
            </div>
          </div>
          <div className="flex items-center gap-6">
            <div className="text-right">
              <p className="font-display text-2xl font-bold text-mist-100">{submission.compliance_score}%</p>
              <p className="text-[11px] text-mist-600">Compliance score</p>
            </div>
            <RiskBadge level={submission.risk_level} />
          </div>
        </div>

        <div className="flex flex-wrap gap-4 px-6 py-4">
          {ID_FIELDS.map((f) => (
            <div key={f.key} className="min-w-[120px]">
              <p className="text-[10.5px] uppercase tracking-wide text-mist-600">{f.label}</p>
              <p className="font-mono text-[13px] text-mist-300">{submission.bidder[f.key] || '—'}</p>
            </div>
          ))}
        </div>

        {isNotQualified && (
          <div className="mx-6 mb-5 flex items-start gap-3 rounded-lg border border-danger-500/30 bg-danger-500/10 px-4 py-3">
            <AlertOctagon size={16} className="mt-0.5 shrink-0 text-danger-400" />
            <div>
              <p className="text-[13px] font-semibold text-danger-300">NOT QUALIFIED — PENDING OFFICER REVIEW</p>
              <p className="mt-0.5 text-[12px] text-danger-400/80">
                {matrix.summary.failed_rules.length} mandatory requirement(s) failed or are unresolved. A numeric score cannot override a mandatory failure.
              </p>
            </div>
          </div>
        )}
      </Card>

      {/* AI recommendation strip */}
      <Card className="flex flex-col justify-between gap-3 p-5 sm:flex-row sm:items-center">
        <div>
          <p className="text-[11px] uppercase tracking-wide text-mist-600">AI recommendation</p>
          <p className="mt-0.5 font-display text-[15px] font-bold text-mist-100">{matrix.ai_recommendation}</p>
          <p className="mt-1 text-[12px] text-mist-500">
            {matrix.summary.passed.length} passed · {matrix.summary.uncertain_fields.length} need review · {matrix.summary.failed_rules.length} failed
          </p>
        </div>
        <button
          onClick={handleReEvaluate}
          disabled={reEvaluating}
          className="flex items-center gap-1.5 self-start rounded-lg border border-ink-600 px-3 py-2 text-[12.5px] font-medium text-mist-300 transition hover:border-verify-500/40 hover:text-verify-300 disabled:opacity-50"
        >
          <RefreshCw size={13} className={reEvaluating ? 'animate-spin' : ''} /> Re-evaluate
        </button>
      </Card>

      {/* Compliance Matrix */}
      <Card className="overflow-hidden p-0">
        <div className="border-b border-ink-700/70 px-6 py-4">
          <h3 className="font-display text-[15px] font-bold text-mist-100">Compliance matrix</h3>
          <p className="mt-0.5 text-[12px] text-mist-500">Every result traces to evidence — click a row to open the Evidence Viewer.</p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-[13px]">
            <thead>
              <tr className="border-b border-ink-700 text-[11px] uppercase tracking-wide text-mist-600">
                <th className="px-6 py-3 font-medium">Requirement</th>
                <th className="px-3 py-3 font-medium">Status</th>
                <th className="px-3 py-3 font-medium">Source</th>
                <th className="px-3 py-3 font-medium">Confidence</th>
                <th className="px-3 py-3 font-medium">Risk</th>
                <th className="px-3 py-3 font-medium">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-ink-700/50">
              {matrix.matrix.map((row) => (
                <tr
                  key={row.id}
                  onClick={() => setActiveResultId(row.id)}
                  className={`group cursor-pointer transition hover:bg-ink-800/50 ${
                    row.status === 'mismatch' ? 'bg-danger-500/[0.04]' : ''
                  }`}
                >
                  <td className="px-6 py-3.5">
                    <p className="font-medium text-mist-200">{row.requirement_label}</p>
                    {row.mandatory && <span className="text-[10.5px] uppercase tracking-wide text-mist-600">Mandatory</span>}
                  </td>
                  <td className="px-3 py-3.5"><StatusPill status={row.status} /></td>
                  <td className="px-3 py-3.5 text-mist-500">{row.source || '—'}</td>
                  <td className="px-3 py-3.5"><ConfidenceMeter value={row.confidence} /></td>
                  <td className="px-3 py-3.5"><RiskBadge level={row.risk_level} /></td>
                  <td className="px-3 py-3.5">
                    {row.resolved ? (
                      <span className="text-[11.5px] text-success-400">{row.human_action?.replaceAll('_', ' ')}</span>
                    ) : row.status === 'mismatch' || row.status === 'fail' || row.status === 'missing' ? (
                      <span className="text-[11.5px] font-medium text-danger-400 group-hover:underline">Review →</span>
                    ) : (
                      <span className="text-[11.5px] text-mist-600">None</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {activeResultId && (
        <EvidenceViewer
          resultId={activeResultId}
          onClose={() => setActiveResultId(null)}
          onActionDone={refresh}
        />
      )}
    </div>
  );
}
