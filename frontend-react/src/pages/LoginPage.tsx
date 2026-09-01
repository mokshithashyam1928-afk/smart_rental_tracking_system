import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export function LoginPage() {
  const [email, setEmail] = useState('admin@smart-rental.io')
  const [password, setPassword] = useState('admin123')
  const [error, setError] = useState('')
  const navigate = useNavigate()
  const { login } = useAuth()

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    setError('')

    try {
      await login(email, password)
      navigate('/dashboard')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed')
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#fff8f6] p-6">
      <div className="grid w-full max-w-5xl overflow-hidden rounded-[28px] border border-stone-200 bg-white shadow-[0_30px_80px_rgba(68,52,41,0.08)] lg:grid-cols-2">
        <div className="bg-[#1e2127] p-10 text-white">
          <p className="text-xs uppercase tracking-[0.35em] text-stone-300">SmartRental</p>
          <h1 className="mt-6 text-4xl font-black tracking-tight">Industrial fleet visibility</h1>
          <p className="mt-4 max-w-md text-sm text-stone-300">
            Monitor rental assets, dispatch crews, and keep equipment utilization optimized across every site.
          </p>

          <div className="mt-10 space-y-4">
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <p className="text-xs uppercase tracking-[0.25em] text-stone-300">Depot status</p>
              <p className="mt-2 text-3xl font-bold text-[#f5c16c]">96%</p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <p className="text-xs uppercase tracking-[0.25em] text-stone-300">Active rentals</p>
              <p className="mt-2 text-3xl font-bold text-[#7dd3c0]">248</p>
            </div>
          </div>
        </div>

        <div className="p-8 sm:p-10">
          <div className="mb-8">
            <p className="text-xs uppercase tracking-[0.35em] text-stone-500">System access</p>
            <h2 className="mt-3 text-3xl font-bold text-stone-900">Welcome back</h2>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-stone-600">Email</label>
              <input
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                className="w-full rounded-xl border border-stone-300 bg-stone-50 px-4 py-3 text-sm outline-none ring-0 transition focus:border-[#ab6639] focus:bg-white"
                placeholder="name@company.com"
              />
            </div>

            <div>
              <label className="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-stone-600">Password</label>
              <input
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                className="w-full rounded-xl border border-stone-300 bg-stone-50 px-4 py-3 text-sm outline-none transition focus:border-[#ab6639] focus:bg-white"
                placeholder="••••••••"
              />
            </div>

            {error && <p className="text-sm font-medium text-red-600">{error}</p>}

            <button type="submit" className="w-full rounded-xl bg-[#ab6639] px-4 py-3 text-sm font-bold uppercase tracking-[0.2em] text-white transition hover:bg-[#8e512d]">
              Sign In
            </button>
          </form>

          <div className="mt-8 flex items-center justify-between text-sm text-stone-600">
            <Link to="/signup" className="font-semibold text-[#ab6639] hover:text-[#8e512d]">Create account</Link>
            <button type="button" className="font-medium text-stone-600 hover:text-stone-900">Forgot credentials?</button>
          </div>

          <div className="mt-8 border-t border-stone-200 pt-5 text-sm text-stone-600">
            <p className="mb-2 font-semibold uppercase tracking-[0.2em] text-stone-500">Demo accounts</p>
            <ul className="space-y-1">
              <li>admin@smart-rental.io / admin123</li>
              <li>manager@smart-rental.io / manager123</li>
              <li>operator@smart-rental.io / operator123</li>
              <li>viewer@smart-rental.io / viewer123</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
