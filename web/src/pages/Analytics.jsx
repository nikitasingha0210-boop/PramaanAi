import { useEffect, useState } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { api } from '../lib/api';
import { Card } from '../components/StatusPrimitives';

const STATUS_COLORS = {
  likely_compliant: '#58745B',
  requires_review: '#B18445',
  potentially_non_compliant: '#A65454',
  not_qualified: '#A65454',
  qualified: '#58745B',
  submitted: '#64758A',
  under_verification: '#64758A',
};
const RISK_COLORS = { low: '#58745B', medium: '#B18445', high: '#A65454', critical: '#7A3E48' };

function StatCard({ label, value, hint }) {
  return (
    <Card className="p-5">
      <p className="font-display text-2xl font-bold text-mist-100">{value}</p>
      <p className="mt-1 text-[12.5px] text-mist-500">{label}</p>
      {hint && <p className="mt-0.5 text-[11px] text-mist-600">{hint}</p>}
    </Card>
  );
}

export default function Analytics() {
  const [data, setData] = useState(null);

  useEffect(() => { api.analyticsOverview().then(setData); }, []);
  if (!data) return <p className="text-mist-500">Loading…</p>;

  const complianceData = Object.entries(data.compliance_distribution || {}).map(([k, v]) => ({ name: k.replaceAll('_', ' '), value: v, key: k }));
  const riskData = Object.entries(data.risk_distribution || {}).map(([k, v]) => ({ name: k, value: v, key: k }));

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <div>
        <h2 className="font-display text-xl font-bold text-mist-100">Analytics</h2>
        <p className="mt-1 text-[13px] text-mist-500">Verification performance across all tenders.</p>
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatCard label="Documents processed" value={data.documents_processed} />
        <StatCard label="Avg. verification time" value={`${data.avg_verification_minutes}m`} hint="vs. hours manually" />
        <StatCard label="Effort saved" value={`${data.estimated_effort_saved_hours}h`} />
        <StatCard label="Pending verification" value={data.pending_verification} />
      </div>

      <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
        <Card className="p-6">
          <h3 className="mb-4 font-display text-[14.5px] font-bold text-mist-100">Compliance distribution</h3>
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie data={complianceData} dataKey="value" nameKey="name" innerRadius={55} outerRadius={85} paddingAngle={3}>
                {complianceData.map((d) => <Cell key={d.key} fill={STATUS_COLORS[d.key] || '#64758A'} stroke="none" />)}
              </Pie>
              <Tooltip contentStyle={{ background: '#FFFFFF', border: '1px solid #E5DED2', borderRadius: 8, fontSize: 12, color: '#343331', boxShadow: '0 4px 16px rgba(52,51,49,0.12)' }} />
            </PieChart>
          </ResponsiveContainer>
          <div className="mt-2 flex flex-wrap justify-center gap-3">
            {complianceData.map((d) => (
              <span key={d.key} className="flex items-center gap-1.5 text-[11px] capitalize text-mist-500">
                <span className="h-2 w-2 rounded-full" style={{ background: STATUS_COLORS[d.key] || '#64758A' }} /> {d.name} ({d.value})
              </span>
            ))}
          </div>
        </Card>

        <Card className="p-6">
          <h3 className="mb-4 font-display text-[14.5px] font-bold text-mist-100">Risk distribution</h3>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={riskData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5DED2" vertical={false} />
              <XAxis dataKey="name" stroke="#8B8780" tick={{ fontSize: 11, textTransform: 'capitalize' }} axisLine={false} tickLine={false} />
              <YAxis stroke="#8B8780" tick={{ fontSize: 11 }} axisLine={false} tickLine={false} allowDecimals={false} />
              <Tooltip contentStyle={{ background: '#FFFFFF', border: '1px solid #E5DED2', borderRadius: 8, fontSize: 12, color: '#343331', boxShadow: '0 4px 16px rgba(52,51,49,0.12)' }} cursor={{ fill: 'rgba(122,62,72,0.05)' }} />
              <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                {riskData.map((d) => <Cell key={d.key} fill={RISK_COLORS[d.key] || '#64758A'} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>
    </div>
  );
}
