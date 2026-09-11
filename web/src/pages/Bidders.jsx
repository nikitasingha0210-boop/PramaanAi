import { useEffect, useState } from 'react';
import { Users } from 'lucide-react';
import { Card } from '../components/StatusPrimitives';

export default function Bidders() {
  const [bidders, setBidders] = useState([]);

  useEffect(() => {
    fetch('/api/tenders/bidders/all', { headers: { Authorization: `Bearer ${localStorage.getItem('pramaanai_token')}` } })
      .then((r) => r.json()).then(setBidders).catch(() => {});
  }, []);

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <div>
        <h2 className="font-display text-xl font-bold text-mist-100">Bidders</h2>
        <p className="mt-1 text-[13px] text-mist-500">Registered bidder organizations across all tenders.</p>
      </div>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {bidders.map((b) => (
          <Card key={b.id} className="p-5">
            <div className="mb-3 flex h-9 w-9 items-center justify-center rounded-lg border border-verify-500/20 bg-verify-500/10">
              <Users size={16} className="text-verify-400" />
            </div>
            <h3 className="font-display text-[14px] font-bold text-mist-100">{b.name}</h3>
            <p className="mt-0.5 text-[11.5px] text-mist-500">{b.category}</p>
            <div className="mt-3 space-y-1 font-mono text-[11.5px] text-mist-500">
              <p>PAN: {b.pan || '—'}</p>
              <p>GSTIN: {b.gstin || '—'}</p>
              <p>CIN: {b.cin || '—'}</p>
            </div>
          </Card>
        ))}
        {bidders.length === 0 && <p className="col-span-3 py-16 text-center text-[13px] text-mist-600">No bidders registered yet.</p>}
      </div>
    </div>
  );
}
