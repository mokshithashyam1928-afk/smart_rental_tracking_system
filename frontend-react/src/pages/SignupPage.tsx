import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import type { Role } from '../types'

const roles: Role[] = ['ADMIN', 'MANAGER', 'OPERATOR', 'VIEWER']

export function SignupPage() {
  const [name, setName] = useState('Alicia Morgan')
  const [email, setEmail] = useState('admin@smart-rental.io')
  const [password, setPassword] = useState('admin123')
  const [role, setRole] = useState<Role>('ADMIN')
  const [error, setError] = useState('')
  const navigate = useNavigate()
  const { signup } = useAuth()

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    setError('')

    try {
      await signup(name, email, password, role)
      navigate('/dashboard')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Signup failed')
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#fff8f6] p-6">
      <div className="w-full max-w-xl rounded-[28px] border border-stone-200 bg-white p-8 shadow-[0_30px_80px_rgba(68,52,41,0.08)]">
        <p className="text-xs uppercase tracking-[0.35em] text-stone-500">Create account</p>
        <h2 className="mt-3 text-3xl font-bold text-stone-900">Join SmartRental</h2>

        <form onSubmit={handleSubmit} className="mt-8 space-y-5">
          <div>
            <label className="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-stone-600">Full name</label>
            <input value={name} onChange={(e) => setName(e.target.value)} className="w-full rounded-xl border border-stone-300 bg-stone-50 px-4 py-3 text-sm focus:border-[#ab6639] focus:bg-white" />
          </div>

          <div>
            <label className="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-stone-600">Email</label>
            <input value={email} onChange={(e) => setEmail(e.target.value)} className="w-full rounded-xl border border-stone-300 bg-stone-50 px-4 py-3 text-sm focus:border-[#ab6639] focus:bg-white" />
          </div>

          <div>
            <label className="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-stone-600">Password</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="w-full rounded-xl border border-stone-300 bg-stone-50 px-4 py-3 text-sm focus:border-[#ab6639] focus:bg-white" />
          </div>

          <div>
            <label className="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-stone-600">Role</label>
            <select value={role} onChange={(e) => setRole(e.target.value as Role)} className="w-full rounded-xl border border-stone-300 bg-stone-50 px-4 py-3 text-sm focus:border-[#ab6639] focus:bg-white">
              {roles.map((option) => (
                <option key={option} value={option}>{option}</option>
              ))}
            </select>
          </div>

          {error && <p className="text-sm font-medium text-red-600">{error}</p>}

          <button type="submit" className="w-full rounded-xl bg-[#ab6639] px-4 py-3 text-sm font-bold uppercase tracking-[0.2em] text-white hover:bg-[#8e512d]">
            Create Account
          </button>
        </form>

        <p className="mt-6 text-sm text-stone-600">
          Already have an account?{' '}
          <Link to="/" className="font-semibold text-[#ab6639] hover:text-[#8e512d]">Sign in</Link>
        </p>
      </div>
    </div>
  )
}
