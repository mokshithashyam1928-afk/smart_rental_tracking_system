import { useEffect, useState } from 'react'
import { Filter, Search, ShieldCheck } from 'lucide-react'
import { Navbar } from '../components/Navbar'
import { Sidebar } from '../components/Sidebar'
import { useAuth } from '../context/AuthContext'
import { api } from '../services/api'
import type { Asset } from '../types'

export function InventoryPage() {
  const { user } = useAuth()
  const [assets, setAssets] = useState<Asset[]>([])

  useEffect(() => {
    const load = async () => {
      const nextAssets = await api.getAssets()
      setAssets(nextAssets)
    }
    load()
  }, [])

  return (
    <div className="flex min-h-screen bg-[#fff8f6] text-stone-900">
      <Sidebar role={user?.role ?? 'VIEWER'} />

      <div className="flex-1">
        <Navbar />

        <main className="p-6">
          <div className="mb-6 flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.25em] text-stone-500">Inventory</p>
              <h2 className="mt-2 text-3xl font-bold">Equipment fleet</h2>
            </div>
            <div className="flex items-center gap-3">
              <button className="flex items-center gap-2 rounded-xl border border-stone-200 bg-white px-3 py-2 text-sm font-medium text-stone-700">
                <Filter size={16} /> Filter
              </button>
              <button className="rounded-xl bg-[#ab6639] px-4 py-2 text-sm font-bold uppercase tracking-[0.2em] text-white hover:bg-[#8e512d]">
                Export
              </button>
            </div>
          </div>

          <div className="rounded-3xl border border-stone-200 bg-white p-5 shadow-sm">
            <div className="mb-4 flex items-center gap-3 rounded-2xl border border-stone-200 bg-stone-50 px-3 py-2">
              <Search size={18} className="text-stone-400" />
              <input placeholder="Search equipment, site or operator" className="w-full bg-transparent text-sm outline-none" />
            </div>

            <div className="overflow-x-auto">
              <table className="min-w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-stone-200 text-stone-500">
                    <th className="pb-3 pr-4 font-medium">Equipment</th>
                    <th className="pb-3 pr-4 font-medium">Status</th>
                    <th className="pb-3 pr-4 font-medium">Site</th>
                    <th className="pb-3 pr-4 font-medium">Operator</th>
                    <th className="pb-3 pr-4 font-medium">Fuel</th>
                  </tr>
                </thead>
                <tbody>
                  {assets.map((asset) => (
                    <tr key={asset.id} className="border-b border-stone-100">
                      <td className="py-3 pr-4">
                        <div>
                          <p className="font-semibold text-stone-900">{asset.name}</p>
                          <p className="text-xs uppercase tracking-[0.2em] text-stone-500">{asset.id}</p>
                        </div>
                      </td>
                      <td className="py-3 pr-4">
                        <span className={`rounded-full px-2 py-1 text-[10px] font-bold ${asset.status === 'IN_USE' ? 'bg-[#fef3c7] text-[#7c4a12]' : asset.status === 'OVERDUE' ? 'bg-rose-100 text-rose-700' : asset.status === 'AVAILABLE' ? 'bg-[#ccfbf1] text-[#115e59]' : 'bg-stone-200 text-stone-700'}`}>
                          {asset.status}
                        </span>
                      </td>
                      <td className="py-3 pr-4 text-stone-600">{asset.site}</td>
                      <td className="py-3 pr-4 text-stone-600">{asset.operator}</td>
                      <td className="py-3 pr-4">
                        <div className="flex items-center gap-3">
                          <div className="h-2 w-24 overflow-hidden rounded-full bg-stone-200">
                            <div className="h-full rounded-full bg-[#ab6639]" style={{ width: `${asset.fuel}%` }} />
                          </div>
                          <span className="text-xs font-semibold text-stone-700">{asset.fuel}%</span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="mt-6 rounded-3xl border border-stone-200 bg-white p-5 shadow-sm">
            <div className="flex items-center gap-2">
              <ShieldCheck className="text-[#ab6639]" size={18} />
              <p className="text-xs uppercase tracking-[0.25em] text-stone-500">Validation</p>
            </div>
            <p className="mt-2 text-sm text-stone-600">Asset records are automatically synchronized through the telemetry service. Manual inspection flags are ready for operational review.</p>
          </div>
        </main>
      </div>
    </div>
  )
}
