import { useMemo, useState } from 'react'
import { Camera, ScanLine, Search, ShieldCheck } from 'lucide-react'
import { Navbar } from '../components/Navbar'
import { Sidebar } from '../components/Sidebar'
import { useAuth } from '../context/AuthContext'
import { mockAssets } from '../data/mockData'

export function EquipmentPage() {
  const { user } = useAuth()
  const [search, setSearch] = useState('')
  const [qrCode, setQrCode] = useState('EQ-1001')

  const filteredAssets = useMemo(() => {
    const value = search.trim().toLowerCase()

    if (!value) return mockAssets

    return mockAssets.filter(
      (asset) =>
        asset.id.toLowerCase().includes(value) ||
        asset.name.toLowerCase().includes(value) ||
        asset.site.toLowerCase().includes(value),
    )
  }, [search])

  return (
    <div className="flex min-h-screen bg-[#fff8f6] text-stone-900">
      <Sidebar role={user?.role ?? 'VIEWER'} />

      <div className="flex-1">
        <Navbar />

        <main className="space-y-6 p-6">
          <div className="mb-2 flex items-center justify-between gap-4">
            <div>
              <p className="text-xs uppercase tracking-[0.25em] text-stone-500">Equipment</p>
              <h2 className="mt-2 text-3xl font-bold">Asset control</h2>
            </div>
            <button className="inline-flex items-center gap-2 rounded-xl bg-[#ab6639] px-4 py-2 text-sm font-bold uppercase tracking-[0.2em] text-white hover:bg-[#8e512d]">
              <Camera size={16} />
              Scan QR
            </button>
          </div>

          <div className="grid gap-6 xl:grid-cols-[1fr_0.9fr]">
            <div className="rounded-3xl border border-stone-200 bg-white p-5 shadow-sm">
              <div className="mb-4 flex items-center gap-3 rounded-2xl border border-stone-200 bg-stone-50 px-3 py-2">
                <Search size={18} className="text-stone-400" />
                <input
                  value={search}
                  onChange={(event) => setSearch(event.target.value)}
                  placeholder="Search equipment or site"
                  className="w-full bg-transparent text-sm outline-none placeholder:text-stone-400"
                />
              </div>

              <div className="space-y-3">
                {filteredAssets.map((asset) => (
                  <div key={asset.id} className="flex items-center justify-between rounded-2xl border border-stone-200 bg-stone-50 p-3">
                    <div>
                      <p className="font-semibold text-stone-900">{asset.name}</p>
                      <p className="text-xs uppercase tracking-[0.2em] text-stone-500">{asset.id}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold text-stone-700">{asset.site}</p>
                      <p className="text-xs text-stone-500">Status: {asset.status}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-3xl border border-stone-200 bg-white p-5 shadow-sm">
              <div className="flex items-center gap-2">
                <ScanLine className="text-[#ab6639]" size={18} />
                <p className="text-xs uppercase tracking-[0.25em] text-stone-500">QR workflow</p>
              </div>

              <div className="mt-6 rounded-3xl border-2 border-dashed border-[#ab6639]/30 bg-[#fff3e8] p-6 text-center">
                <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-2xl bg-white shadow-sm">
                  <ScanLine className="text-[#ab6639]" size={30} />
                </div>
                <p className="mt-4 text-lg font-bold text-stone-900">Ready to scan</p>
                <p className="mt-2 text-sm text-stone-600">Point a QR code or enter the asset ID manually.</p>
              </div>

              <div className="mt-5 space-y-3">
                <label className="block text-xs font-semibold uppercase tracking-[0.2em] text-stone-600">Asset reference</label>
                <input
                  value={qrCode}
                  onChange={(event) => setQrCode(event.target.value)}
                  className="w-full rounded-xl border border-stone-300 bg-stone-50 px-4 py-3 text-sm outline-none focus:border-[#ab6639] focus:bg-white"
                />
                <button className="w-full rounded-xl border border-stone-200 bg-white px-4 py-3 text-sm font-semibold text-stone-700 hover:bg-stone-50">
                  Validate asset
                </button>
              </div>
            </div>
          </div>

          <div className="rounded-3xl border border-stone-200 bg-white p-5 shadow-sm">
            <div className="flex items-center gap-2">
              <ShieldCheck className="text-[#ab6639]" size={18} />
              <p className="text-xs uppercase tracking-[0.25em] text-stone-500">Operational check</p>
            </div>
            <p className="mt-2 text-sm text-stone-600">
              QR validation confirms equipment authenticity, site assignment, and operator credential status before checkout or return.
            </p>
          </div>
        </main>
      </div>
    </div>
  )
}
