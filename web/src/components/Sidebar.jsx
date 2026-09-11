import { NavLink } from 'react-router-dom';
import {
  LayoutGrid, FileStack, Users, ScanSearch, FileCheck2, ClipboardList,
  Layers, BarChart3, Bell, History, Settings, LogOut, ShieldCheck,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const NAV_ITEMS = [
  { to: '/', icon: LayoutGrid, label: 'Dashboard', end: true },
  { to: '/tenders', icon: FileStack, label: 'Tenders' },
  { to: '/bidders', icon: Users, label: 'Bidders' },
  { to: '/analytics', icon: BarChart3, label: 'Analytics' },
  { to: '/alerts', icon: Bell, label: 'Alerts' },
  { to: '/audit', icon: History, label: 'Audit Trail' },
];

export default function Sidebar({ mobileOpen, onCloseMobile }) {
  const { user, logout } = useAuth();

  return (
    <>
      {mobileOpen && (
        <div className="fixed inset-0 z-40 bg-black/60 lg:hidden" onClick={onCloseMobile} />
      )}
      <aside
        className={`fixed left-0 top-0 z-50 flex h-screen w-[220px] flex-col border-r border-ink-700/70 bg-ink-900/95 backdrop-blur-xl transition-transform lg:translate-x-0
        ${mobileOpen ? 'translate-x-0' : '-translate-x-full'}`}
      >
        <div className="flex items-center gap-2.5 px-5 py-5">
          <div className="flex h-8 w-8 items-center justify-center rounded-md border border-seal-500/30 bg-seal-500/10">
            <ShieldCheck size={17} className="text-seal-400" strokeWidth={2} />
          </div>
          <span className="font-display text-[14.5px] font-bold tracking-tight text-mist-100">PramaanAI</span>
        </div>

        <nav className="flex-1 space-y-0.5 px-3 py-2">
          {NAV_ITEMS.map(({ to, icon: Icon, label, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              onClick={onCloseMobile}
              className={({ isActive }) =>
                `group relative flex items-center gap-2.5 rounded-lg px-3 py-2 text-[13px] font-medium transition-colors ${
                  isActive
                    ? 'bg-seal-500/10 text-seal-300'
                    : 'text-mist-500 hover:bg-ink-800/80 hover:text-mist-200'
                }`
              }
            >
              {({ isActive }) => (
                <>
                  {isActive && <span className="absolute left-0 top-1/2 h-4 w-[3px] -translate-y-1/2 rounded-r-full bg-seal-400" />}
                  <Icon size={16} strokeWidth={2} />
                  {label}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-ink-700/70 px-3 py-3">
          <NavLink
            to="/settings"
            className="flex items-center gap-2.5 rounded-lg px-3 py-2 text-[13px] font-medium text-mist-500 transition-colors hover:bg-ink-800/80 hover:text-mist-200"
          >
            <Settings size={16} /> Settings
          </NavLink>
          <div className="mt-2 flex items-center gap-2.5 rounded-lg px-3 py-2">
            <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-verify-500/15 font-display text-[11px] font-bold text-verify-300">
              {user?.full_name?.split(' ').map((n) => n[0]).join('').slice(0, 2)}
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-[12px] font-medium text-mist-200">{user?.full_name}</p>
              <p className="truncate text-[10.5px] capitalize text-mist-600">{user?.role?.replaceAll('_', ' ')}</p>
            </div>
            <button onClick={logout} aria-label="Log out" className="text-mist-600 transition hover:text-danger-400">
              <LogOut size={15} />
            </button>
          </div>
        </div>
      </aside>
    </>
  );
}
