import { useEffect, useMemo, useState } from 'react'
import {
  Building2,
  ChevronDown,
  ChevronUp,
  Fuel,
  MapPin,
  MapPinned,
  Search,
  Truck,
  User,
} from 'lucide-react'
import { Navbar } from '../components/Navbar'
import { Sidebar } from '../components/Sidebar'
import { useAuth } from '../context/AuthContext'
import { api } from '../services/api'
import type { Asset, SiteItem } from '../types'

export function SitesPage() {
  const { user } = useAuth()
  const [sites, setSites] = useState<SiteItem[]>([])
  const [assets, setAssets] = useState<Asset[]>([])
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [expandedSiteId, setExpandedSiteId] = useState<number | null>(null)

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      try {
        const [liveSites, liveAssets] = await Promise.all([
          api.getSites().catch(() => []),
          api.getAssets().catch(() => []),
        ])
        setSites(liveSites)
        setAssets(liveAssets)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  // Group equipment assets by site name / ID
  const equipmentBySite = useMemo(() => {
    const map = new Map<string, Asset[]>()
    assets.forEach((asset) => {
      const keys = [asset.site, asset.siteCode].filter(Boolean).map((key) => key!.toLowerCase().trim())
      keys.forEach((siteKey) => {
        const existing = map.get(siteKey) || []
        existing.push(asset)
        map.set(siteKey, existing)
      })
    })
    return map
  }, [assets])

  const filteredSites = useMemo(() => {
    const query = search.trim().toLowerCase()
    if (!query) return sites

    return sites.filter((s) => {
      const nameMatch = s.name.toLowerCase().includes(query)
      const codeMatch = (s.site_code || '').toLowerCase().includes(query)
      const idMatch = String(s.id).includes(query)
      const addrMatch = (s.address || '').toLowerCase().includes(query)
      return nameMatch || codeMatch || idMatch || addrMatch
    })
  }, [search, sites])

  return (
    <div className="flex min-h-screen bg-[#fcf9f7] text-stone-900">
      <Sidebar role={user?.role ?? 'VIEWER'} />

      <div className="flex-1 flex flex-col min-w-0">
        <Navbar />

        <main className="flex-1 p-4 md:p-8 max-w-7xl mx-auto w-full space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <span className="inline-flex items-center gap-1.5 rounded-full bg-amber-100 px-3 py-1 text-xs font-bold uppercase tracking-wider text-amber-900">
                <MapPinned size={13} className="text-[#ab6639]" />
                Job Sites & Deployment Yards
              </span>
              <h1 className="mt-2 text-2xl md:text-3xl font-extrabold text-stone-900 tracking-tight">
                Site Directory & Equipment Allocation
              </h1>
              <p className="text-xs md:text-sm text-stone-500 mt-1">
                View site IDs, geographic locations, and detailed machinery allocation per construction site.
              </p>
            </div>

            {/* Search Bar */}
            <div className="flex items-center gap-2 rounded-2xl border border-stone-200 bg-white px-3.5 py-2.5 shadow-xs w-full sm:w-72">
              <Search size={16} className="text-stone-400" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search by Site ID or Name..."
                className="w-full bg-transparent text-xs font-medium outline-none placeholder:text-stone-400"
              />
            </div>
          </div>

          {/* Sites List */}
          {loading ? (
            <div className="rounded-3xl border border-stone-200 bg-white p-12 text-center text-xs font-semibold text-stone-500">
              Loading deployment sites and machinery allocation...
            </div>
          ) : filteredSites.length === 0 ? (
            <div className="rounded-3xl border border-dashed border-stone-300 bg-white p-12 text-center text-xs font-semibold text-stone-500">
              No construction sites found matching &quot;{search}&quot;.
            </div>
          ) : (
            <div className="space-y-4">
              {filteredSites.map((site) => {
                const siteCode = site.site_code || `SITE-${site.id.toString().padStart(3, '0')}`
                const assignedEquipment =
                  equipmentBySite.get(site.name.toLowerCase().trim()) ||
                  equipmentBySite.get(siteCode.toLowerCase().trim()) ||
                  []

                const activeCount = assignedEquipment.filter(
                  (e) => e.status === 'RENTED' || e.status === 'IN_USE',
                ).length
                const isExpanded = expandedSiteId === site.id

                return (
                  <div
                    key={site.id}
                    className="rounded-3xl border border-stone-200 bg-white p-5 md:p-6 shadow-xs hover:shadow-md transition duration-200"
                  >
                    {/* Site Header Info Row */}
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-stone-100">
                      <div className="flex items-start gap-3.5">
                        <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-amber-50 text-[#ab6639] shrink-0 border border-amber-200/60">
                          <Building2 size={22} />
                        </div>
                        <div>
                          <div className="flex items-center gap-2.5 flex-wrap">
                            <span className="font-mono text-xs font-extrabold text-[#ab6639] bg-amber-50 px-2.5 py-1 rounded-lg border border-amber-200">
                              Site ID: {siteCode}
                            </span>
                            <span className="text-[10px] font-mono text-stone-400">
                              (DB ID: #{site.id})
                            </span>
                            <span
                              className={`rounded-full px-2.5 py-0.5 text-[10px] font-extrabold uppercase tracking-wider ${
                                site.status === 'ACTIVE'
                                  ? 'bg-emerald-100 text-emerald-800'
                                  : 'bg-stone-200 text-stone-700'
                              }`}
                            >
                              {site.status || 'ACTIVE'}
                            </span>
                          </div>

                          <h3 className="text-xl font-extrabold text-stone-900 mt-1">{site.name}</h3>
                          <p className="text-xs text-stone-500 mt-0.5 flex items-center gap-1.5">
                            <MapPin size={13} className="text-stone-400 shrink-0" />
                            {site.address || 'Primary Job Site Location'}
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center gap-4">
                        <div className="text-left md:text-right">
                          <p className="text-2xl font-extrabold text-stone-900">
                            {assignedEquipment.length}{' '}
                            <span className="text-xs font-semibold text-stone-500">machines</span>
                          </p>
                          <p className="text-[11px] text-emerald-700 font-bold">
                            {activeCount} active in field
                          </p>
                        </div>

                        <button
                          onClick={() => setExpandedSiteId(isExpanded ? null : site.id)}
                          className="inline-flex items-center gap-1.5 rounded-xl border border-stone-200 bg-stone-50 px-3.5 py-2 text-xs font-bold text-stone-700 hover:bg-stone-100 transition cursor-pointer"
                        >
                          {isExpanded ? (
                            <>
                              Hide Equipment Details <ChevronUp size={14} />
                            </>
                          ) : (
                            <>
                              View Equipment Details <ChevronDown size={14} />
                            </>
                          )}
                        </button>
                      </div>
                    </div>

                    {/* Equipment Details Expansion Section */}
                    {isExpanded && (
                      <div className="mt-4 pt-2 animate-in fade-in duration-200">
                        <div className="mb-3 flex items-center justify-between">
                          <p className="text-xs font-bold uppercase tracking-wider text-stone-500 flex items-center gap-1.5">
                            <Truck size={14} className="text-[#ab6639]" />
                            Deployed Equipment List for {site.name} ({siteCode})
                          </p>
                          <span className="text-[11px] font-semibold text-stone-400">
                            Showing {assignedEquipment.length} items
                          </span>
                        </div>

                        {assignedEquipment.length === 0 ? (
                          <div className="rounded-2xl border border-dashed border-stone-200 bg-stone-50 p-6 text-center text-xs text-stone-500">
                            No equipment currently assigned to this site.
                          </div>
                        ) : (
                          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                            {assignedEquipment.map((eq) => (
                              <div
                                key={eq.id}
                                className="rounded-2xl border border-stone-200 bg-stone-50/70 p-4 space-y-2 hover:bg-white transition"
                              >
                                <div className="flex items-center justify-between">
                                  <span className="font-mono text-xs font-bold text-stone-900 bg-white px-2 py-0.5 rounded border border-stone-200">
                                    {eq.id}
                                  </span>
                                  <span
                                    className={`rounded-full px-2 py-0.5 text-[9px] font-extrabold uppercase tracking-wider ${
                                      eq.status === 'AVAILABLE'
                                        ? 'bg-emerald-100 text-emerald-800'
                                        : eq.status === 'IN_USE' || eq.status === 'RENTED'
                                          ? 'bg-amber-100 text-amber-800'
                                          : eq.status === 'OVERDUE'
                                            ? 'bg-rose-100 text-rose-800'
                                            : 'bg-stone-200 text-stone-700'
                                    }`}
                                  >
                                    {eq.status}
                                  </span>
                                </div>

                                <div>
                                  <h4 className="font-extrabold text-stone-900 text-sm">{eq.name}</h4>
                                  <p className="text-[11px] text-stone-500">{eq.type}</p>
                                </div>

                                <div className="pt-2 border-t border-stone-200/60 grid grid-cols-2 gap-2 text-[11px]">
                                  <div className="flex items-center gap-1 text-stone-700">
                                    <User size={12} className="text-stone-400" />
                                    <span className="truncate">{eq.operator || 'Unassigned'}</span>
                                  </div>
                                  <div className="flex items-center gap-1 text-stone-700 justify-end font-mono">
                                    <Fuel size={12} className="text-amber-600" />
                                    <span>{eq.fuel}% fuel</span>
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          )}
        </main>
      </div>
    </div>
  )
}
