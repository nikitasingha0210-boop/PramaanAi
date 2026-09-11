import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Sparkles, CheckCircle2, ArrowUpRight, ShieldQuestion, Plus } from 'lucide-react';
import { api } from '../lib/api';
import { Card, StatusPill, RiskBadge } from '../components/StatusPrimitives';

export default function TenderDetail() {
  const { id } = useParams();
  const [tender, setTender] = useState(null);
  const [text, setText] = useState('');
  const [extracting, setExtracting] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [selected, setSelected] = useState(new Set());
  const [bidders, setBidders] = useState([]);
  const [addingBidderId, setAddingBidderId] = useState('');

  function refresh() {
    api.getTender(id).then((t) => {
      setTender(t);
      setText(t.raw_tender_text || '');
    });
  }
  useEffect(refresh, [id]);
  useEffect(() => {
    fetch('/api/tenders/bidders/all', { headers: { Authorization: `Bearer ${localStorage.getItem('pramaanai_token')}` } })
      .then((r) => r.json()).then(setBidders).catch(() => {});
  }, []);

  if (!tender) return <p className="text-mist-500">Loading…</p>;

  const draftRequirements = tender.requirements.filter((r) => !r.confirmed);
  const confirmedRequirements = tender.requirements.filter((r) => r.confirmed);

  async function handleExtract() {
    setExtracting(true);
    try {
      await api.extractRequirements(id, text);
      refresh();
    } finally {
      setExtracting(false);
    }
  }

  function toggle(reqId) {
    setSelected((s) => {
      const next = new Set(s);
      next.has(reqId) ? next.delete(reqId) : next.add(reqId);
      return next;
    });
  }

  async function handleConfirm() {
    if (selected.size === 0) return;
    setConfirming(true);
    try {
      await api.confirmRequirements(id, Array.from(selected));
      setSelected(new Set());
      refresh();
    } finally {
      setConfirming(false);
    }
  }

  async function addBidderSubmission() {
    if (!addingBidderId) return;
    await fetch(`/api/tenders/${id}/submissions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('pramaanai_token')}` },
      body: JSON.stringify({ bidder_id: addingBidderId }),
    });
    setAddingBidderId('');
    refresh();
  }

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <div>
        <p className="font-mono text-[11.5px] text-mist-600">{tender.code}</p>
        <h2 className="mt-1 font-display text-xl font-bold text-mist-100">{tender.title}</h2>
        <p className="mt-1 text-[13px] text-mist-500">{tender.department}</p>
        <div className="mt-3 flex items-center gap-3">
          <StatusPill status={tender.status} />
          <span className="text-[12px] text-mist-600">Rule version {tender.rule_version}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
        {/* Requirement extraction — Checkpoint 1 */}
        <Card className="p-6">
          <div className="mb-3 flex items-center gap-2">
            <ShieldQuestion size={16} className="text-verify-400" />
            <h3 className="font-display text-[14.5px] font-bold text-mist-100">Requirement extraction</h3>
          </div>
          <p className="mb-3 text-[12px] text-mist-500">
            Paste tender text below. PramaanAI extracts draft rules — nothing governs this tender until an officer confirms it.
          </p>
          <textarea
            rows={6}
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste tender eligibility text here…"
            className="w-full rounded-lg border border-ink-600 bg-ink-900/70 px-3 py-2.5 text-[13px] text-mist-200 outline-none focus:border-verify-500/60"
          />
          <button
            onClick={handleExtract}
            disabled={extracting || !text.trim()}
            className="mt-3 flex items-center gap-1.5 rounded-lg border border-verify-500/30 bg-verify-500/10 px-3.5 py-2 text-[13px] font-medium text-verify-300 transition hover:bg-verify-500/20 disabled:opacity-50"
          >
            <Sparkles size={14} /> {extracting ? 'Extracting…' : 'Extract draft requirements'}
          </button>

          {draftRequirements.length > 0 && (
            <div className="mt-5 space-y-2 border-t border-ink-700 pt-4">
              <p className="text-[11.5px] font-medium uppercase tracking-wide text-mist-600">
                Draft rules — pending confirmation
              </p>
              {draftRequirements.map((r) => (
                <label key={r.id} className="flex cursor-pointer items-start gap-2.5 rounded-lg border border-warning-500/20 bg-warning-500/5 p-3">
                  <input
                    type="checkbox"
                    checked={selected.has(r.id)}
                    onChange={() => toggle(r.id)}
                    className="mt-0.5 accent-seal-500"
                  />
                  <div className="min-w-0">
                    <p className="text-[13px] font-medium text-mist-200">{r.label}</p>
                    <p className="mt-0.5 text-[11.5px] italic text-mist-600">"{r.source_text}"</p>
                  </div>
                </label>
              ))}
              <button
                onClick={handleConfirm}
                disabled={confirming || selected.size === 0}
                className="mt-2 flex items-center gap-1.5 rounded-lg bg-gradient-to-b from-seal-400 to-seal-600 px-3.5 py-2 text-[13px] font-semibold text-ink-950 disabled:opacity-50"
              >
                <CheckCircle2 size={14} /> Confirm {selected.size > 0 ? selected.size : ''} rule{selected.size !== 1 ? 's' : ''}
              </button>
            </div>
          )}
        </Card>

        {/* Confirmed rules */}
        <Card className="p-6">
          <h3 className="mb-3 font-display text-[14.5px] font-bold text-mist-100">Governing requirements ({confirmedRequirements.length})</h3>
          <div className="space-y-2">
            {confirmedRequirements.map((r) => (
              <div key={r.id} className="flex items-center justify-between rounded-lg border border-ink-700/70 bg-ink-900/40 px-3.5 py-2.5">
                <div>
                  <p className="text-[13px] font-medium text-mist-200">{r.label}</p>
                  <p className="text-[11px] uppercase tracking-wide text-mist-600">{r.category.replaceAll('_', ' ')}</p>
                </div>
                {r.mandatory && <span className="rounded-full border border-danger-500/25 bg-danger-500/10 px-2 py-0.5 text-[10.5px] font-medium text-danger-400">Mandatory</span>}
              </div>
            ))}
            {confirmedRequirements.length === 0 && <p className="py-8 text-center text-[13px] text-mist-600">No confirmed requirements yet.</p>}
          </div>
        </Card>
      </div>

      {/* Bidder submissions */}
      <Card className="p-6">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="font-display text-[14.5px] font-bold text-mist-100">Bidder submissions</h3>
          <div className="flex items-center gap-2">
            <select
              value={addingBidderId}
              onChange={(e) => setAddingBidderId(e.target.value)}
              className="rounded-lg border border-ink-600 bg-ink-900/70 px-2.5 py-1.5 text-[12.5px] text-mist-300 outline-none"
            >
              <option value="">Add existing bidder…</option>
              {bidders.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}
            </select>
            <button onClick={addBidderSubmission} className="flex items-center gap-1 rounded-lg border border-ink-600 px-2.5 py-1.5 text-[12.5px] text-mist-300 hover:border-verify-500/40">
              <Plus size={13} /> Add
            </button>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-[13px]">
            <thead>
              <tr className="border-b border-ink-700 text-[11px] uppercase tracking-wide text-mist-600">
                <th className="pb-2.5 font-medium">Bidder</th>
                <th className="pb-2.5 font-medium">Status</th>
                <th className="pb-2.5 font-medium">Score</th>
                <th className="pb-2.5 font-medium">Risk</th>
                <th className="pb-2.5 font-medium">Recommendation</th>
                <th />
              </tr>
            </thead>
            <tbody className="divide-y divide-ink-700/60">
              {tender.submissions.map((s) => (
                <tr key={s.id} className="group">
                  <td className="py-3 font-medium text-mist-200">{s.bidder_name}</td>
                  <td className="py-3"><StatusPill status={s.status} /></td>
                  <td className="py-3 font-mono text-mist-300">{s.compliance_score}%</td>
                  <td className="py-3"><RiskBadge level={s.risk_level} /></td>
                  <td className="py-3 text-mist-400">{s.ai_recommendation}</td>
                  <td className="py-3 text-right">
                    <Link to={`/submissions/${s.id}`} className="inline-flex items-center gap-1 text-[12.5px] font-medium text-verify-400 opacity-0 transition group-hover:opacity-100">
                      Open <ArrowUpRight size={13} />
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {tender.submissions.length === 0 && <p className="py-8 text-center text-[13px] text-mist-600">No bidders yet.</p>}
        </div>
      </Card>
    </div>
  );
}
