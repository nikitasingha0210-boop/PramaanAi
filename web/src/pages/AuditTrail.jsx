import { useEffect, useState } from 'react';
import { Lock, ShieldCheck } from 'lucide-react';
import { api } from '../lib/api';
import { Card } from '../components/StatusPrimitives';

export default function AuditTrail() {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    api.listAudit({ limit: 200 }).then(setEvents);
  }, []);

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-display text-xl font-bold text-mist-100">Audit trail</h2>
          <p className="mt-1 text-[13px] text-mist-500">An append-only ledger of every action taken across PramaanAI.</p>
        </div>
        <span className="flex items-center gap-1.5 rounded-lg border border-ink-600 bg-ink-850 px-3 py-1.5 text-[11.5px] text-mist-500">
          <Lock size={12} /> Immutable
        </span>
      </div>

      <Card className="p-0">
        <div className="relative">
          <div className="absolute bottom-6 left-[38px] top-6 w-px bg-ink-700" />
          <div className="space-y-0 p-6">
            {events.map((e) => (
              <div key={e.id} className="relative flex gap-4 py-3.5">
                <div className="flex w-16 shrink-0 flex-col items-end pt-0.5">
                  <span className="font-mono text-[11px] text-mist-500">
                    {new Date(e.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                  </span>
                  <span className="font-mono text-[9.5px] text-mist-700">
                    {new Date(e.created_at).toLocaleDateString()}
                  </span>
                </div>
                <div className="relative z-10 mt-1 flex h-3 w-3 shrink-0 items-center justify-center rounded-full border-2 border-ink-900 bg-verify-500" />
                <div className="min-w-0 flex-1 pb-1">
                  <p className="text-[13px] text-mist-200">
                    <span className="font-medium">{e.actor_name}</span>
                    <span className="text-mist-600"> ({e.actor_role.replaceAll('_', ' ')})</span>
                    {' — '}
                    <span className="font-mono text-[12px] text-verify-400">{e.action}</span>
                  </p>
                  {(e.old_value || e.new_value) && (
                    <p className="mt-0.5 text-[12px] text-mist-500">
                      {e.old_value && <span className="rounded bg-ink-800 px-1.5 py-0.5 font-mono text-[11px]">{e.old_value}</span>}
                      {e.old_value && e.new_value && <span className="mx-1.5">→</span>}
                      {e.new_value && <span className="rounded bg-ink-800 px-1.5 py-0.5 font-mono text-[11px] text-mist-300">{e.new_value}</span>}
                    </p>
                  )}
                  {e.reason && <p className="mt-1 text-[12px] italic text-mist-600">"{e.reason}"</p>}
                  {e.override && (
                    <span className="mt-1 inline-flex items-center gap-1 rounded-full border border-warning-500/25 bg-warning-500/10 px-2 py-0.5 text-[10.5px] text-warning-400">
                      <ShieldCheck size={10} /> Override
                    </span>
                  )}
                </div>
              </div>
            ))}
            {events.length === 0 && <p className="py-16 text-center text-[13px] text-mist-600">No audit events yet.</p>}
          </div>
        </div>
      </Card>
    </div>
  );
}
