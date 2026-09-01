import { BarChart3, CalendarClock, ShieldAlert, Truck } from 'lucide-react'
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { Navbar } from '../components/Navbar'
import { Sidebar } from '../components/Sidebar'
import { StatCard } from '../components/StatCard'
import { useAuth } from '../context/AuthContext'
import { chartData, dashboardStats } from '../data/mockData'
import { useWebSocket } from '../hooks/useWebSocket'
import { api } from '../services/api'
import { useEffect, useState } from 'react'
import type { DashboardStat } from '../types'

export function DashboardPage() {
  const { user } = useAuth()
  const [stats, setStats] = useState<DashboardStat[]>(dashboardStats)

  useEffect(() => {
    const load = async () => {
      const nextStats = await api.getDashboardStats()
      setStats(nextStats)
    }
    load()
  }, [])

  const { assets } = useWebSocket([])

  return (
    <div className="flex min-h-screen bg-[#fff8f6] text-stone-900">
      <Sidebar role={user?.role ?? 'VIEWER'} />

      <div className="flex-1">
        <Navbar />

        <main className="space-y-6 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.25em] text-stone-500">Overview</p>
              <h2 className="mt-2 text-3xl font-bold">Asset performance</h2>
            </div>
            <div className="flex items-center gap-2 rounded-full bg-[#fff3e8] px-3 py-2 text-sm font-semibold text-[#ab6639]">
              <CalendarClock size={16} />
              Updated 2 mins ago
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            {stats.map((stat) => (
              <StatCard key={stat.label} label={stat.label} value={stat.value} change={stat.change} accent={stat.accent} />
            ))}
          </div>

          <div className="grid gap-6 xl:grid-cols-[1.7fr_1fr]">
            <div className="rounded-3xl border border-stone-200 bg-white p-5 shadow-sm">
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <p className="text-xs uppercase tracking-[0.25em] text-stone-500">Equipment Status</p>
                  <h3 className="mt-2 text-2xl font-bold">Fleet utilization</h3>
                </div>
                <BarChart3 className="text-[#ab6639]" size={20} />
              </div>

              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e7e5e4" />
                    <XAxis dataKey="name" stroke="#78716c" />
                    <YAxis stroke="#78716c" />
                    <Tooltip />
                    <Bar dataKey="active" fill="#ab6639" radius={[6, 6, 0, 0]} />
                    <Bar dataKey="idle" fill="#7dd3c0" radius={[6, 6, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="rounded-3xl border border-stone-200 bg-white p-5 shadow-sm">
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <p className="text-xs uppercase tracking-[0.25em] text-stone-500">Alerts</p>
                  <h3 className="mt-2 text-2xl font-bold">Priority queue</h3>
                </div>
                <ShieldAlert className="text-[#a16207]" size={20} />
              </div>

              <div className="space-y-4">
                {[{ label: 'Overdue return', value: '7 assets', tone: 'rose' }, { label: 'Fuel variance', value: '12 records', tone: 'amber' }, { label: 'Idle risk', value: '4 alerts', tone: 'teal' }].map((item) => (
                  <div key={item.label} className="rounded-2xl border border-stone-200 bg-stone-50 p-3">
                    <div className="flex items-center justify-between">
                      <p className="font-semibold text-stone-900">{item.label}</p>
                      <span className={`rounded-full px-2 py-1 text-[10px] font-bold ${item.tone === 'rose' ? 'bg-rose-100 text-rose-700' : item.tone === 'amber' ? 'bg-amber-100 text-amber-700' : 'bg-teal-100 text-teal-700'}`}>
                        {item.value}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="rounded-3xl border border-stone-200 bg-white p-5 shadow-sm">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.25em] text-stone-500">Rental activity</p>
                <h3 className="mt-2 text-2xl font-bold">Recent Rentals</h3>
              </div>
              <Truck className="text-[#ab6639]" size={20} />
            </div>

            <div className="overflow-x-auto">
              <table className="min-w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-stone-200 text-stone-500">
                    <th className="pb-3 pr-4 font-medium">Rental ID</th>
                    <th className="pb-3 pr-4 font-medium">Equipment</th>
                    <th className="pb-3 pr-4 font-medium">Operator</th>
                    <th className="pb-3 pr-4 font-medium">Site</th>
                    <th className="pb-3 pr-4 font-medium">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {assets.length > 0 ? assets.map((asset) => (
                    <tr key={asset.id} className="border-b border-stone-100">
                      <td className="py-3 pr-4 font-semibold">{asset.id}</td>
                      <td className="py-3 pr-4">{asset.name}</td>
                      <td className="py-3 pr-4">{asset.operator}</td>
                      <td className="py-3 pr-4">{asset.site}</td>
                      <td className="py-3 pr-4">
                        <span className={`rounded-full px-2 py-1 text-[10px] font-bold ${asset.status === 'IN_USE' ? 'bg-[#fef3c7] text-[#7c4a12]' : asset.status === 'OVERDUE' ? 'bg-rose-100 text-rose-700' : asset.status === 'AVAILABLE' ? 'bg-[#ccfbf1] text-[#115e59]' : 'bg-stone-200 text-stone-700'}`}>
                          {asset.status}
                        </span>
                      </td>
                    </tr>
                  )) : null}
                </tbody>
              </table>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
