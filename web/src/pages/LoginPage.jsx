import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Eye, EyeOff, ShieldCheck, ArrowRight, Loader2, ScanLine, ChevronDown } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const DEMO_ACCOUNTS = [
  { role: 'Procurement Officer', email: 'procurement.officer@pramaanai.gov.in' },
  { role: 'Procurement Administrator', email: 'procurement.admin@pramaanai.gov.in' },
  { role: 'Compliance Reviewer', email: 'compliance.reviewer@pramaanai.gov.in' },
  { role: 'Department Administrator', email: 'department.admin@pramaanai.gov.in' },
  { role: 'Senior Approving Authority', email: 'approving.authority@pramaanai.gov.in' },
];
const DEMO_PASSWORD = 'Pramaan@2026';

const FLOATING_CHIPS = [
  { label: 'GSTIN Verified' },
  { label: '99.2% Confidence' },
  { label: 'Audit Ready' },
  { label: 'PAN Matched' },
  { label: 'Evidence Linked' },
];

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showDemo, setShowDemo] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
      navigate('/');
    } catch (err) {
      setError(err.status === 401 ? 'Incorrect email or password.' : 'Unable to sign in. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  function useDemo(account) {
    setEmail(account.email);
    setPassword(DEMO_PASSWORD);
    setShowDemo(false);
  }

  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-ink-950 bg-grid">
      {/* Ambient lighting */}
      <div className="pointer-events-none absolute -top-40 -left-40 h-[560px] w-[560px] rounded-full bg-seal-500/10 blur-[140px]" />
      <div className="pointer-events-none absolute -bottom-52 -right-32 h-[620px] w-[620px] rounded-full bg-verify-500/10 blur-[150px]" />
      <div className="pointer-events-none absolute top-1/3 left-1/2 h-[300px] w-[300px] -translate-x-1/2 rounded-full bg-ink-500/10 blur-[120px]" />

      <div className="relative z-10 mx-auto flex min-h-screen max-w-7xl flex-col px-6 py-8 lg:px-12">
        {/* Wordmark */}
        <div className="flex items-center gap-2.5 animate-rise-in" style={{ animationDelay: '0.05s' }}>
          <div className="flex h-8 w-8 items-center justify-center rounded-md border border-seal-500/30 bg-seal-500/10">
            <ShieldCheck size={17} className="text-seal-400" strokeWidth={2} />
          </div>
          <span className="font-display text-[15px] font-bold tracking-tight text-mist-100">PramaanAI</span>
        </div>

        <div className="flex flex-1 flex-col items-center justify-center gap-16 py-10 lg:flex-row lg:items-center lg:gap-10">
          {/* LEFT — brand composition */}
          <div className="relative w-full max-w-xl lg:flex-[1.15]">
            <div className="relative">
              <h1
                className="font-display text-[2.65rem] font-bold leading-[1.08] tracking-tight text-mist-100 animate-rise-in sm:text-6xl"
                style={{ animationDelay: '0.15s' }}
              >
                Proof,
                <br />
                not just a score.
              </h1>
              <p
                className="mt-5 max-w-md font-body text-[15px] leading-relaxed text-mist-500 animate-rise-in"
                style={{ animationDelay: '0.28s' }}
              >
                Every compliance result traces back to the document it came from, the government
                record it was checked against, and the rule that fired — so your officers decide
                with evidence, not a black box.
              </p>

              {/* Evidence chain visual */}
              <div
                className="mt-10 hidden animate-rise-in sm:block"
                style={{ animationDelay: '0.42s' }}
              >
                <div className="flex flex-wrap items-center gap-0 font-mono text-[11px] uppercase tracking-wider text-mist-600">
                  {['Requirement', 'Evidence', 'Verification', 'Rule', 'Result'].map((step, i) => (
                    <div key={step} className="flex items-center">
                      <div className="rounded-full border border-ink-600 bg-ink-900/60 px-3 py-1.5 text-mist-400">
                        {step}
                      </div>
                      {i < 4 && <div className="mx-1.5 h-px w-6 bg-gradient-to-r from-ink-600 to-ink-600/20" />}
                    </div>
                  ))}
                </div>
              </div>

              {/* Floating verification chips — arranged as a loose cluster, never over text */}
              <div className="mt-10 hidden flex-wrap gap-3 lg:flex">
                {FLOATING_CHIPS.map((chip, i) => (
                  <div
                    key={chip.label}
                    className="animate-rise-in animate-drift rounded-lg border border-ink-600/80 bg-ink-850/80 px-3 py-1.5 shadow-lg shadow-ink-500/15 backdrop-blur-sm"
                    style={{
                      animationDelay: `${0.55 + i * 0.12}s, ${1.4 + i * 0.6}s`,
                      transform: `translateY(${i % 2 === 0 ? '0px' : '10px'})`,
                    }}
                  >
                    <span className="flex items-center gap-1.5 whitespace-nowrap font-mono text-[11px] text-success-400">
                      <span className="h-1.5 w-1.5 rounded-full bg-success-400" />
                      {chip.label}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* RIGHT — login panel */}
          <div
            className="w-full max-w-[400px] shrink-0 animate-rise-in lg:flex-1"
            style={{ animationDelay: '0.35s' }}
          >
            <div className="relative rounded-2xl border border-ink-600/70 bg-ink-850/90 p-8 shadow-2xl shadow-ink-500/25 backdrop-blur-xl">
              <div className="mb-7">
                <h2 className="font-display text-xl font-bold text-mist-100">Sign in to PramaanAI</h2>
                <p className="mt-1.5 text-[13px] text-mist-500">Verification intelligence for public procurement.</p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="mb-1.5 block text-[12px] font-medium text-mist-400">Work email</label>
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@department.gov.in"
                    className="w-full rounded-lg border border-ink-600 bg-ink-900/70 px-3.5 py-2.5 text-[14px] text-mist-100 placeholder:text-mist-600 outline-none transition focus:border-verify-500/60 focus:ring-2 focus:ring-verify-500/20"
                  />
                </div>

                <div>
                  <label className="mb-1.5 block text-[12px] font-medium text-mist-400">Password</label>
                  <div className="relative">
                    <input
                      type={showPassword ? 'text' : 'password'}
                      required
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="••••••••••••"
                      className="w-full rounded-lg border border-ink-600 bg-ink-900/70 px-3.5 py-2.5 pr-10 text-[14px] text-mist-100 placeholder:text-mist-600 outline-none transition focus:border-verify-500/60 focus:ring-2 focus:ring-verify-500/20"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword((s) => !s)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-mist-600 transition hover:text-mist-400"
                      aria-label={showPassword ? 'Hide password' : 'Show password'}
                    >
                      {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                </div>

                {error && (
                  <div className="rounded-lg border border-danger-500/30 bg-danger-500/10 px-3 py-2 text-[13px] text-danger-400">
                    {error}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={loading}
                  className="group flex w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-b from-seal-400 to-seal-600 py-2.5 text-[14px] font-semibold text-ink-950 shadow-lg shadow-seal-600/20 transition hover:shadow-seal-600/30 active:scale-[0.99] disabled:opacity-60"
                >
                  {loading ? (
                    <Loader2 size={16} className="animate-spin" />
                  ) : (
                    <>
                      Sign in
                      <ArrowRight size={15} className="transition group-hover:translate-x-0.5" />
                    </>
                  )}
                </button>
              </form>

              <div className="mt-5 flex items-center gap-1.5 text-[11.5px] text-mist-600">
                <ScanLine size={12} />
                Access is scoped by role — every action is recorded to the audit trail.
              </div>

              {/* Demo credentials */}
              <div className="mt-6 border-t border-ink-700 pt-4">
                <button
                  type="button"
                  onClick={() => setShowDemo((s) => !s)}
                  className="flex w-full items-center justify-between text-[12.5px] font-medium text-mist-400 transition hover:text-mist-200"
                >
                  Demo access — 5 role accounts
                  <ChevronDown size={14} className={`transition-transform ${showDemo ? 'rotate-180' : ''}`} />
                </button>
                {showDemo && (
                  <div className="mt-3 space-y-1.5">
                    {DEMO_ACCOUNTS.map((acc) => (
                      <button
                        key={acc.email}
                        type="button"
                        onClick={() => useDemo(acc)}
                        className="flex w-full items-center justify-between rounded-md border border-ink-700 bg-ink-900/50 px-3 py-2 text-left text-[12px] transition hover:border-verify-500/40 hover:bg-ink-900"
                      >
                        <span className="text-mist-300">{acc.role}</span>
                        <span className="font-mono text-[10.5px] text-mist-600">use →</span>
                      </button>
                    ))}
                    <p className="pt-1 text-[11px] text-mist-600">Password for every demo account: <span className="font-mono text-mist-400">{DEMO_PASSWORD}</span></p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
