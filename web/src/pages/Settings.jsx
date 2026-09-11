import { useAuth } from '../context/AuthContext';
import { Card } from '../components/StatusPrimitives';

export default function Settings() {
  const { user } = useAuth();
  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <h2 className="font-display text-xl font-bold text-mist-100">Settings</h2>
      <Card className="p-6">
        <h3 className="mb-4 font-display text-[14.5px] font-bold text-mist-100">Account</h3>
        <div className="space-y-3 text-[13.5px]">
          <div className="flex justify-between border-b border-ink-700 pb-3"><span className="text-mist-500">Name</span><span className="text-mist-200">{user?.full_name}</span></div>
          <div className="flex justify-between border-b border-ink-700 pb-3"><span className="text-mist-500">Email</span><span className="text-mist-200">{user?.email}</span></div>
          <div className="flex justify-between border-b border-ink-700 pb-3"><span className="text-mist-500">Role</span><span className="capitalize text-mist-200">{user?.role?.replaceAll('_', ' ')}</span></div>
          <div className="flex justify-between"><span className="text-mist-500">Department</span><span className="text-mist-200">{user?.department || '—'}</span></div>
        </div>
      </Card>
      <p className="text-[12px] text-mist-600">Additional preferences and notification settings are not yet available in this prototype.</p>
    </div>
  );
}
