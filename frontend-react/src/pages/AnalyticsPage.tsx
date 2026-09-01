import { Navbar } from '../components/Navbar'
import { Sidebar } from '../components/Sidebar'
import { useAuth } from '../context/AuthContext'

export function AnalyticsPage() {
  const { user } = useAuth()

  return (
    <div className="flex min-h-screen bg-[#fff8f6] text-stone-900">
      <Sidebar role={user?.role ?? 'VIEWER'} />

      <div className="flex-1">
        <Navbar />

        <main className="p-6">
          <div className="mb-6">
            <p className="text-xs uppercase tracking-[0.25em] text-stone-500">Analytics</p>
            <h2 className="mt-2 text-3xl font-bold">Utilization and risk</h2>
          </div>

          <div className="grid gap-6 lg:grid-cols-3">
            <div className="rounded-3xl border border-stone-200 bg-white p-5 shadow-sm">
              <p className="text-xs uppercase tracking-[0.25em] text-stone-500">Fuel efficiency</p>
              <p className="mt-4 text-4xl font-bold text-stone-900">82%</p>
              <p className="mt-2 text-sm text-stone-600">Improved 4.2% over the previous week.</p>
            </div>
            <div className="rounded-3xl border border-stone-200 bg-white p-5 shadow-sm">
              <p className="text-xs uppercase tracking-[0.25em] text-stone-500">Idle cost</p>
              <p className="mt-4 text-4xl font-bold text-stone-900">$12.4k</p>
              <p className="mt-2 text-sm text-stone-600">Down from $15.1k in the prior cycle.</p>
            </div>
            <div className="rounded-3xl border border-stone-200 bg-white p-5 shadow-sm">
              <p className="text-xs uppercase tracking-[0.25em] text-stone-500">Demand forecast</p>
              <p className="mt-4 text-4xl font-bold text-stone-900">+18%</p>
              <p className="mt-2 text-sm text-stone-600">Projected demand for heavy earth movers.</p>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
