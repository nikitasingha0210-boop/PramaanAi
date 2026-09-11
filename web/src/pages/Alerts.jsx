import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { AlertOctagon, AlertTriangle, Info, CheckCircle2 } from 'lucide-react';
import { api } from '../lib/api';
import { Card } from '../components/StatusPrimitives';

const SEVERITY_META = {
  critical: { icon: AlertOctagon, color: 'text-danger-400', bg: 'bg-danger-500/10', border: 'border-danger-500/25', label: 'Critical' },
  warning: { icon: AlertTriangle, color: 'text-warning-400', bg: 'bg-warning-500/10', border: 'border-warning-500/25', label: 'Warning' },
  information: { icon: Info, color: 'text-verify-400', bg: 'bg-verify-500/10', border: 'border-verify-500/25', label: 'Information' },
  resolved: { icon: CheckCircle2, color: 'text-success-400', bg: 'bg-success-500/10', border: 'border-success-500/25', label: 'Resolved' },
};

export default function Alerts() {
  const [alerts, setAlerts] = useState([]);
  useEffect(() => { api.listAlerts().then(setAlerts); }, []);

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <h2 className="font-display text-xl font-bold text-mist-100">Alerts</h2>
        <p className="mt-1 text-[13px] text-mist-500">Discrepancies, expirations, and reviews across all active tenders.</p>
      </div>

      <div className="space-y-2.5">
        {alerts.map((a) => {
          const meta = SEVERITY_META[a.severity] || SEVERITY_META.information;
          return (
            <Link to={`/tenders/${a.tender_id}`} key={a.id} className="block">
              <Card className={`flex items-start gap-3.5 border p-4 transition hover:bg-ink-800/50 ${meta.border}`}>
                <div className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg ${meta.bg}`}>
                  <meta.icon size={15} className={meta.color} />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <p className="truncate text-[13.5px] font-medium text-mist-200">{a.title}</p>
                    <span className={`shrink-0 rounded-full ${meta.bg} px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide ${meta.color}`}>{meta.label}</span>
                  </div>
                  {a.detail && <p className="mt-0.5 truncate text-[12px] text-mist-500">{a.detail}</p>}
                </div>
              </Card>
            </Link>
          );
        })}
        {alerts.length === 0 && <p className="py-16 text-center text-[13px] text-mist-600">No alerts — everything is clear.</p>}
      </div>
    </div>
  );
}
