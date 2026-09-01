import { Activity, BarChart3, MapPinned, ShieldCheck, Truck, UserCircle2 } from 'lucide-react'
import { NavLink } from 'react-router-dom'
import type { Role } from '../types'

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: BarChart3, roles: ['ADMIN', 'MANAGER', 'OPERATOR', 'VIEWER'] },
  { to: '/equipment', label: 'Equipment', icon: Truck, roles: ['ADMIN', 'MANAGER', 'OPERATOR', 'VIEWER'] },
  { to: '/inventory', label: 'Inventory', icon: Truck, roles: ['ADMIN', 'MANAGER', 'OPERATOR', 'VIEWER'] },
  { to: '/sites', label: 'Sites', icon: MapPinned, roles: ['ADMIN', 'MANAGER', 'OPERATOR', 'VIEWER'] },
  { to: '/operators', label: 'Operators', icon: UserCircle2, roles: ['ADMIN', 'MANAGER', 'OPERATOR'] },
  { to: '/map', label: 'Live Map', icon: MapPinned, roles: ['ADMIN', 'MANAGER', 'OPERATOR', 'VIEWER'] },
  { to: '/rentals', label: 'Rentals', icon: Activity, roles: ['ADMIN', 'MANAGER', 'OPERATOR'] },
  { to: '/analytics', label: 'Analytics', icon: ShieldCheck, roles: ['ADMIN', 'MANAGER'] },
]

export function Sidebar({ role }: { role: Role }) {
  return (
    <aside className="w-72 border-r border-stone-200 bg-[#fff8f6] p-5">
      <div className="mb-8 flex items-center gap-3">
        <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-[#ab6639] text-lg font-bold text-white">S</div>
        <div>
          <p className="text-xs uppercase tracking-[0.25em] text-stone-500">SmartRental</p>
          <h1 className="text-xl font-bold text-stone-900">Operations</h1>
        </div>
      </div>

      <nav className="space-y-2">
        {navItems.map(({ to, label, icon: Icon, roles }) => {
          const allowed = roles.includes(role)

          if (!allowed) return null

          return (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-semibold transition ${
                  isActive ? 'bg-[#ab6639] text-white shadow-sm' : 'text-stone-700 hover:bg-stone-100'
                }`
              }
            >
              <Icon size={18} />
              {label}
            </NavLink>
          )
        })}
      </nav>

      <div className="mt-8 rounded-2xl border border-stone-200 bg-stone-50 p-4">
        <div className="flex items-center gap-3">
          <div className="rounded-full bg-stone-200 p-2 text-stone-700">
            <UserCircle2 size={20} />
          </div>
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-stone-500">Role</p>
            <p className="font-semibold text-stone-900">{role}</p>
          </div>
        </div>
      </div>
    </aside>
  )
}
