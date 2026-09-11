import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Plus, ArrowUpRight, X } from 'lucide-react';
import { api } from '../lib/api';
import { useAuth } from '../context/AuthContext';
import { getPermissions } from '../lib/permissions';
import { Card, StatusPill } from '../components/StatusPrimitives';

export default function Tenders() {
  const { user } = useAuth();
  const permissions = getPermissions(user?.role);
  const [tenders, setTenders] = useState([]);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ code: '', title: '', department: '', description: '' });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  function refresh() {
    api.listTenders().then(setTenders).catch(() => {});
  }
  useEffect(refresh, []);

  async function handleCreate(e) {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      await api.createTender(form);
      setShowCreate(false);
      setForm({ code: '', title: '', department: '', description: '' });
      refresh();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-display text-xl font-bold text-mist-100">Tenders</h2>
          <p className="mt-1 text-[13px] text-mist-500">Manage tender-specific requirements and bidder verification.</p>
        </div>
        {permissions.create_tender && (
          <button
            onClick={() => setShowCreate(true)}
            className="flex items-center gap-1.5 rounded-lg bg-gradient-to-b from-seal-400 to-seal-600 px-3.5 py-2 text-[13px] font-semibold text-ink-950 shadow-md shadow-seal-600/20 transition hover:shadow-seal-600/30"
          >
            <Plus size={15} /> New tender
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {tenders.map((t) => (
          <Link
            key={t.id}
            to={`/tenders/${t.id}`}
            className="group block"
          >
            <Card className="p-5 transition group-hover:border-verify-500/35 group-hover:bg-ink-800/70">
              <div className="flex items-start justify-between">
                <div className="min-w-0">
                  <p className="font-mono text-[11px] text-mist-600">{t.code}</p>
                  <h3 className="mt-1 truncate font-display text-[15px] font-bold text-mist-100">{t.title}</h3>
                  <p className="mt-1 text-[12px] text-mist-500">{t.department}</p>
                </div>
                <ArrowUpRight size={16} className="shrink-0 text-mist-600 transition group-hover:text-seal-400" />
              </div>
              <div className="mt-4 flex items-center justify-between">
                <StatusPill status={t.status} />
                <div className="flex gap-4 text-[11.5px] text-mist-500">
                  <span>{t.confirmed_requirement_count}/{t.requirement_count} rules confirmed</span>
                  <span>{t.submission_count} bidders</span>
                </div>
              </div>
            </Card>
          </Link>
        ))}
        {tenders.length === 0 && (
          <p className="col-span-2 py-16 text-center text-[13px] text-mist-600">No tenders yet — create one to get started.</p>
        )}
      </div>

      {showCreate && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm" onClick={() => setShowCreate(false)}>
          <div onClick={(e) => e.stopPropagation()} className="w-full max-w-md rounded-xl border border-ink-600 bg-ink-850 p-6 shadow-2xl">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="font-display text-[15px] font-bold text-mist-100">Create tender</h3>
              <button onClick={() => setShowCreate(false)} className="text-mist-600 hover:text-mist-300"><X size={16} /></button>
            </div>
            <form onSubmit={handleCreate} className="space-y-3">
              {['code', 'title', 'department'].map((field) => (
                <div key={field}>
                  <label className="mb-1 block text-[11.5px] font-medium capitalize text-mist-400">{field}</label>
                  <input
                    required
                    value={form[field]}
                    onChange={(e) => setForm((f) => ({ ...f, [field]: e.target.value }))}
                    className="w-full rounded-lg border border-ink-600 bg-ink-900/70 px-3 py-2 text-[13.5px] text-mist-100 outline-none focus:border-verify-500/60"
                  />
                </div>
              ))}
              <div>
                <label className="mb-1 block text-[11.5px] font-medium text-mist-400">Description</label>
                <textarea
                  rows={3}
                  value={form.description}
                  onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
                  className="w-full rounded-lg border border-ink-600 bg-ink-900/70 px-3 py-2 text-[13.5px] text-mist-100 outline-none focus:border-verify-500/60"
                />
              </div>
              {error && <p className="text-[12px] text-danger-400">{error}</p>}
              <button
                disabled={saving}
                className="w-full rounded-lg bg-gradient-to-b from-seal-400 to-seal-600 py-2.5 text-[13.5px] font-semibold text-ink-950 disabled:opacity-60"
              >
                {saving ? 'Creating…' : 'Create tender'}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
