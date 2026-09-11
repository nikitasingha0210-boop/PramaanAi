import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  TrendingUp, TrendingDown, FileStack, ShieldAlert, Clock, Users,
  ArrowUpRight, ArrowRight, Sparkles, AlertTriangle, CheckCircle2,
} from 'lucide-react';
import { api } from '../lib/api';
import { useAuth } from '../context/AuthContext';
import { Card, RiskBadge, StatusPill } from '../components/StatusPrimitives';

function greeting() {
  const h = new Date().getHours();
  if (h < 12) return 'Good morning';
  if (h < 17) return 'Good afternoon';
  return 'Good evening';
}

function KPI({ icon: Icon, label, value, hint, trend, accent = 'seal', big }) {
  const accentClasses = {
    seal: 'text-seal-400 bg-seal-500/10 border-seal-500/20',
    verify: 'text-verify-400 bg-verify-500/10 border-verify-500/20',
    danger: 'text-danger-400 bg-danger-500/10 border-danger-500/20',
    success: 'text-success-400 bg-success-500/10 border-success-500/20',
  }[accent];

  return (
    <Card className={`p-5 ${big ? 'sm:col-span-2' : ''}`}>
      <div className="flex items-start justify-between">
        <div className={`flex h-9 w-9 items-center justify-center rounded-lg border ${accentClasses}`}>
          <Icon size={16} />
        </div>
        {trend != null && (
          <span className={`flex items-center gap-0.5 text-[11.5px] font-medium ${trend >= 0 ? 'text-success-400' : 'text-danger-400'}`}>
            {trend >= 0 ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
            {Math.abs(trend)}%
          </span>
        )}
      </div>
      <p className="mt-3.5 font-display text-2xl font-bold text-mist-100">{value}</p>
      <p className="mt-0.5 text-[12.5px] text-mist-500">{label}</p>
      {hint && <p className="mt-1 text-[11px] text-mist-600">{hint}</p>}
    </Card>
  );
}

export default function Dashboard() {
  const { user } = useAuth();
  const [overview, setOverview] = useState(null);
  const [tenders, setTenders] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [auditEvents, setAuditEvents] = useState([]);

  useEffect(() => {
    api.analyticsOverview().then(setOverview).catch(() => {});
    api.listTenders().then(setTenders).catch(() => {});
    api.listAlerts().then((a) => setAlerts(a.slice(0, 6))).catch(() => {});
    api.listAudit({ limit: 6 }).then(setAuditEvents).catch(() => {});
  }, []);

  return (
    <div className="mx-auto max-w-7xl space-y-7">
      {/* Greeting */}
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p className="font-display text-xl font-bold text-mist-100">
            {greeting()}, {user?.full_name?.split(' ')[0]}
          </p>
          <p className="mt-1 text-[13.5px] text-mist-500">Your verification intelligence at a glance.</p>
        </div>
        <Link
          to="/tenders"
          className="flex items-center gap-1.5 rounded-lg border border-ink-600 bg-ink-850 px-3.5 py-2 text-[12.5px] font-medium text-mist-300 transition hover:border-seal-500/40 hover:text-seal-300"
        >
          View all tenders <ArrowRight size={13} />
        </Link>
      </div>

      {/* KPI grid */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
        <KPI icon={FileStack} label="Active tenders" value={overview?.active_tenders ?? '—'} accent="verify" />
        <KPI icon={Clock} label="Bids under review" value={overview?.bids_under_review ?? '—'} accent="seal" />
        <KPI icon={Users} label="Verified bidders" value={overview?.verified_bidders ?? '—'} accent="success" />
        <KPI icon={ShieldAlert} label="High-risk bidders" value={overview?.high_risk_bidders ?? '—'} accent="danger" />
        <KPI icon={AlertTriangle} label="Critical discrepancies" value={overview?.critical_discrepancies ?? '—'} accent="danger" />
        <KPI icon={Sparkles} label="Effort saved" value={`${overview?.estimated_effort_saved_hours ?? 0}h`} hint="vs. manual verification" accent="seal" />
      </div>

      {/* Main asymmetric area */}
      <div className="grid grid-cols-1 gap-5 lg:grid-cols-3">
        {/* Large: tenders under evaluation */}
        <Card className="p-6 lg:col-span-2">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="font-display text-[15px] font-bold text-mist-100">Tenders in evaluation</h3>
            <Link to="/tenders" className="text-[12px] text-mist-500 hover:text-mist-300">See all</Link>
          </div>
          <div className="space-y-2.5">
            {tenders.slice(0, 5).map((t) => (
              <Link
                key={t.id}
                to={`/tenders/${t.id}`}
                className="flex flex-col gap-2.5 rounded-lg border border-ink-700/70 bg-ink-900/40 px-4 py-3 transition hover:border-verify-500/30 hover:bg-ink-900/70 sm:flex-row sm:items-center sm:justify-between"
              >
                <div className="min-w-0">
                  <p className="truncate text-[13.5px] font-medium text-mist-200">{t.title}</p>
                  <p className="mt-0.5 truncate font-mono text-[11px] text-mist-600">{t.code} · {t.department}</p>
                </div>
                <div className="flex shrink-0 items-center gap-3">
                  <span className="text-[11.5px] text-mist-500">{t.submission_count} bidder{t.submission_count !== 1 ? 's' : ''}</span>
                  <StatusPill status={t.status} />
                  <ArrowUpRight size={14} className="hidden text-mist-600 sm:block" />
                </div>
              </Link>
            ))}
            {tenders.length === 0 && <p className="py-8 text-center text-[13px] text-mist-600">No tenders yet.</p>}
          </div>
        </Card>

        {/* Smaller: risk alerts */}
        <Card className="p-6">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="font-display text-[15px] font-bold text-mist-100">Risk alerts</h3>
            <Link to="/alerts" className="text-[12px] text-mist-500 hover:text-mist-300">See all</Link>
          </div>
          <div className="space-y-3">
            {alerts.map((a) => (
              <div key={a.id} className="flex items-start gap-2.5">
                <span
                  className={`mt-1 h-1.5 w-1.5 shrink-0 rounded-full ${
                    a.severity === 'critical' ? 'bg-danger-400' : a.severity === 'warning' ? 'bg-warning-400' : 'bg-verify-400'
                  }`}
                />
                <div className="min-w-0">
                  <p className="truncate text-[12.5px] font-medium text-mist-300">{a.title}</p>
                  <p className="truncate text-[11px] text-mist-600">{a.detail}</p>
                </div>
              </div>
            ))}
            {alerts.length === 0 && <p className="py-6 text-center text-[13px] text-mist-600">No active alerts.</p>}
          </div>
        </Card>
      </div>

      {/* Recent audit activity */}
      <Card className="p-6">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="font-display text-[15px] font-bold text-mist-100">Recent audit activity</h3>
          <Link to="/audit" className="text-[12px] text-mist-500 hover:text-mist-300">Open audit trail</Link>
        </div>
        <div className="divide-y divide-ink-700/60">
          {auditEvents.map((e) => (
            <div key={e.id} className="flex items-center gap-4 py-2.5 text-[12.5px]">
              <span className="w-20 shrink-0 font-mono text-[11px] text-mist-600">
                {new Date(e.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
              <CheckCircle2 size={13} className="shrink-0 text-mist-600" />
              <span className="min-w-0 flex-1 truncate text-mist-400">
                <span className="text-mist-200">{e.actor_name}</span> — {e.action.replaceAll('.', ' ').replaceAll('_', ' ')}
                {e.reason ? <span className="text-mist-600"> · {e.reason}</span> : null}
              </span>
            </div>
          ))}
          {auditEvents.length === 0 && <p className="py-6 text-center text-[13px] text-mist-600">No audit activity yet.</p>}
        </div>
      </Card>
    </div>
  );
}
