import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Menu, FileStack, Users, X } from 'lucide-react';
import { api } from '../lib/api';

export default function TopBar({ onOpenMobileNav }) {
  const [open, setOpen] = useState(false);
  const [q, setQ] = useState('');
  const [results, setResults] = useState([]);
  const inputRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    function onKey(e) {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setOpen(true);
      }
      if (e.key === 'Escape') setOpen(false);
    }
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  useEffect(() => {
    if (open) setTimeout(() => inputRef.current?.focus(), 50);
  }, [open]);

  const runSearch = useCallback((value) => {
    setQ(value);
    if (value.trim().length < 2) { setResults([]); return; }
    api.search(value).then(setResults).catch(() => setResults([]));
  }, []);

  function goTo(result) {
    setOpen(false);
    setQ('');
    if (result.type === 'tender') navigate(`/tenders/${result.id}`);
    else if (result.type === 'submission') navigate(`/submissions/${result.id}`);
    else if (result.type === 'bidder') navigate('/bidders');
  }

  return (
    <>
      <header className="sticky top-0 z-30 flex items-center justify-end gap-4 border-b border-ink-700/60 bg-ink-950/80 px-5 py-3.5 backdrop-blur-xl lg:px-8">
        <button onClick={onOpenMobileNav} className="mr-auto text-mist-400 lg:hidden">
          <Menu size={20} />
        </button>
        <button
          onClick={() => setOpen(true)}
          className="flex w-full max-w-[280px] items-center gap-2 rounded-lg border border-ink-700 bg-ink-850/60 px-3 py-2 text-[13px] text-mist-600 transition hover:border-ink-600 hover:text-mist-400"
        >
          <Search size={14} />
          <span className="flex-1 text-left">Search tenders, bidders, PAN...</span>
          <kbd className="rounded border border-ink-600 bg-ink-800 px-1.5 py-0.5 font-mono text-[10px] text-mist-600">⌘K</kbd>
        </button>
      </header>

      {open && (
        <div className="fixed inset-0 z-[100] flex items-start justify-center bg-black/70 pt-[14vh] backdrop-blur-sm" onClick={() => setOpen(false)}>
          <div
            onClick={(e) => e.stopPropagation()}
            className="w-full max-w-xl overflow-hidden rounded-xl border border-ink-600 bg-ink-850 shadow-2xl shadow-ink-500/25"
          >
            <div className="flex items-center gap-2.5 border-b border-ink-700 px-4 py-3.5">
              <Search size={16} className="text-mist-500" />
              <input
                ref={inputRef}
                value={q}
                onChange={(e) => runSearch(e.target.value)}
                placeholder="Search by tender ID, bidder name, PAN, GSTIN, CIN..."
                className="flex-1 bg-transparent text-[14px] text-mist-100 outline-none placeholder:text-mist-600"
              />
              <button onClick={() => setOpen(false)} className="text-mist-600 hover:text-mist-300"><X size={16} /></button>
            </div>
            <div className="max-h-80 overflow-y-auto p-2">
              {results.length === 0 && q.trim().length >= 2 && (
                <p className="px-3 py-6 text-center text-[13px] text-mist-600">No matches found.</p>
              )}
              {results.map((r) => (
                <button
                  key={`${r.type}-${r.id}`}
                  onClick={() => goTo(r)}
                  className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left transition hover:bg-ink-800"
                >
                  <div className="flex h-8 w-8 items-center justify-center rounded-md bg-ink-700 text-mist-400">
                    {r.type === 'tender' ? <FileStack size={14} /> : <Users size={14} />}
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-[13px] font-medium text-mist-200">{r.title}</p>
                    <p className="truncate text-[11.5px] text-mist-600">{r.subtitle}</p>
                  </div>
                  <span className="rounded-full border border-ink-600 px-2 py-0.5 text-[10px] uppercase text-mist-600">{r.type}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
