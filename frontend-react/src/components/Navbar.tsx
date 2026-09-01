import { Bell, HelpCircle, LogOut, Settings } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

export function Navbar() {
  const { user, logout } = useAuth()

  return (
    <header className="flex items-center justify-between border-b border-stone-200 bg-[#fff8f6] px-6 py-4">
      <div>
        <p className="text-xs uppercase tracking-[0.25em] text-stone-500">Fleet command</p>
        <h2 className="text-xl font-bold text-stone-900">Rental Operations</h2>
      </div>

      <div className="flex items-center gap-3">
        <button className="rounded-full border border-stone-200 p-2 text-stone-700 hover:bg-stone-100" aria-label="Notifications">
          <Bell size={18} />
        </button>
        <button className="rounded-full border border-stone-200 p-2 text-stone-700 hover:bg-stone-100" aria-label="Settings" title="Settings">
          <Settings size={18} />
        </button>
        <button className="rounded-full border border-stone-200 p-2 text-stone-700 hover:bg-stone-100" aria-label="Support" title="Support">
          <HelpCircle size={18} />
        </button>

        <div className="ml-2 flex items-center gap-3 rounded-full border border-stone-200 bg-white px-3 py-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[#ab6639] text-xs font-bold text-white">
            {user?.name?.slice(0, 1) || 'U'}
          </div>
          <div>
            <p className="text-sm font-semibold text-stone-900">{user?.name || 'User'}</p>
            <p className="text-[10px] uppercase tracking-[0.2em] text-stone-500">{user?.role || 'VIEWER'}</p>
          </div>
          <button onClick={logout} className="ml-2 rounded-full bg-stone-900 p-2 text-white hover:bg-stone-700" aria-label="Logout">
            <LogOut size={16} />
          </button>
        </div>
      </div>
    </header>
  )
}
