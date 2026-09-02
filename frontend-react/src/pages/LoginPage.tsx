import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const DEMO_ACCOUNTS = [
  { role: 'Fleet Manager', email: 'fleet.manager@caterpillar.com', pass: 'manager123456', tag: 'MANAGER' },
  { role: 'System Admin', email: 'admin@caterpillar.com', pass: 'admin123456', tag: 'ADMIN' },
  { role: 'Site Operator', email: 'operator1@caterpillar.com', pass: 'operator123456', tag: 'OPERATOR' },
  { role: 'Fleet Auditor', email: 'viewer@caterpillar.com', pass: 'viewer123456', tag: 'VIEWER' },
]

export function LoginPage() {
  const [email, setEmail] = useState('fleet.manager@caterpillar.com')
  const [password, setPassword] = useState('manager123456')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const { login } = useAuth()

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    setError('')
    setLoading(true)

    try {
      await login(email, password)
      navigate('/dashboard')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  const fillAccount = (accEmail: string, accPass: string) => {
    setEmail(accEmail)
    setPassword(accPass)
    setError('')
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#fff8f6] p-6">
      <div className="grid w-full max-w-5xl overflow-hidden rounded-[28px] border border-stone-200 bg-white shadow-[0_30px_80px_rgba(68,52,41,0.08)] lg:grid-cols-2">
        <div className="bg-[#1e2127] p-10 text-white flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2">
              <span className="h-3 w-3 rounded-full bg-[#f5c16c]"></span>
              <p className="text-xs uppercase tracking-[0.35em] text-stone-300 font-bold">Caterpillar Fleet</p>
            </div>
            <h1 className="mt-6 text-4xl font-black tracking-tight">Industrial fleet visibility</h1>
            <p className="mt-4 max-w-md text-sm text-stone-300">
              Monitor Caterpillar rental machinery, dispatch certified operators, track telematics, and optimize heavy asset utilization across every job site.
            </p>


          </div>

          <div className="mt-8 text-xs text-stone-400">
            Powered by Caterpillar Smart Rental Tracking System & IoT Telemetry
          </div>
        </div>

        <div className="p-8 sm:p-10">
          <div className="mb-6">
            <p className="text-xs uppercase tracking-[0.35em] text-stone-500 font-bold">System access</p>
            <h2 className="mt-2 text-3xl font-bold text-stone-900">Sign in</h2>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="mb-1.5 block text-xs font-semibold uppercase tracking-[0.2em] text-stone-600">Email</label>
              <input
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                className="w-full rounded-xl border border-stone-300 bg-stone-50 px-4 py-2.5 text-sm outline-none transition focus:border-[#ab6639] focus:bg-white"
                placeholder="name@caterpillar.com"
                required
              />
            </div>

            <div>
              <label className="mb-1.5 block text-xs font-semibold uppercase tracking-[0.2em] text-stone-600">Password</label>
              <input
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                className="w-full rounded-xl border border-stone-300 bg-stone-50 px-4 py-2.5 text-sm outline-none transition focus:border-[#ab6639] focus:bg-white"
                placeholder="••••••••"
                required
              />
            </div>

            {error && (
              <div className="rounded-xl border border-rose-200 bg-rose-50 p-3 text-xs font-medium text-rose-700">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-xl bg-[#ab6639] px-4 py-3 text-sm font-bold uppercase tracking-[0.2em] text-white transition hover:bg-[#8e512d] disabled:opacity-50 cursor-pointer"
            >
              {loading ? 'Authenticating...' : 'Sign In'}
            </button>
          </form>

          <div className="mt-6 flex items-center justify-between text-xs text-stone-600">
            <Link to="/signup" className="font-semibold text-[#ab6639] hover:text-[#8e512d]">Register account</Link>
            <span className="text-stone-400">Click below to auto-fill</span>
          </div>

          <div className="mt-6 border-t border-stone-200 pt-4">
            <p className="mb-2 text-[11px] font-bold uppercase tracking-[0.2em] text-stone-500">Quick Login (Click to fill)</p>
            <div className="grid grid-cols-2 gap-2">
              {DEMO_ACCOUNTS.map((acc) => (
                <button
                  key={acc.email}
                  type="button"
                  onClick={() => fillAccount(acc.email, acc.pass)}
                  className="rounded-xl border border-stone-200 bg-stone-50 p-2 text-left hover:border-[#ab6639] hover:bg-stone-100 transition cursor-pointer"
                >
                  <p className="text-xs font-bold text-stone-800">{acc.role}</p>
                  <p className="text-[10px] text-stone-500 truncate">{acc.email}</p>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
