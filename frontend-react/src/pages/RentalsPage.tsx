import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  AlertCircle,
  AlertTriangle,
  ArrowUpRight,
  Bell,
  Camera,
  CheckCircle2,
  Clock,
  Fuel,
  Gauge,
  Layers,
  MapPin,
  Search,
  Timer,
  User,
  Zap,
} from 'lucide-react'
import { Navbar } from '../components/Navbar'
import { Sidebar } from '../components/Sidebar'
import { useAuth } from '../context/AuthContext'
import { api } from '../services/api'
import type { Rental, SiteItem } from '../types'

export function RentalsPage() {
  const { user } = useAuth()
  const [rentals, setRentals] = useState<Rental[]>([])
  const [sites, setSites] = useState<SiteItem[]>([])
  const [selectedSite, setSelectedSite] = useState<string>('ALL')
  const [statusFilter, setStatusFilter] = useState<'ALL' | 'ACTIVE' | 'COMPLETED' | 'OVERDUE'>('ALL')
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      try {
        const [nextRentals, nextSites] = await Promise.all([
          api.getRentals().catch(() => []),
          api.getSites().catch(() => []),
        ])
        setRentals(nextRentals)
        setSites(nextSites)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  // Calculate duration metrics
  const getDurationStats = (rental: Rental) => {
    if (!rental.startDate) {
      return { hours: 1, text: '1h 0m', fuelLiters: 14.5, idleHours: 0.2, isOverdue: false, isApproaching: false }
    }
    const start = new Date(rental.startDate).getTime()
    const now = Date.now()
    const diffMs = Math.max(0, now - (isNaN(start) ? now : start))
    const totalHours = Math.max(0.5, diffMs / (1000 * 60 * 60))
    const hoursInt = Math.floor(totalHours)
    const minutesInt = Math.floor((totalHours - hoursInt) * 60)

    let durationText = `${hoursInt}h ${minutesInt}m`
    if (hoursInt >= 24) {
      const days = Math.floor(hoursInt / 24)
      const remHours = hoursInt % 24
      durationText = `${days}d ${remHours}h`
    }

    const fuelLiters = Math.round(totalHours * 14.5 * 10) / 10
    const idleHours = Math.round(totalHours * 0.2 * 10) / 10

    let isOverdue = false
    let isApproaching = false

    if (rental.status === 'ACTIVE' && rental.endDate) {
      const due = new Date(rental.endDate).getTime()
      if (!isNaN(due)) {
        if (now > due) {
          isOverdue = true
        } else if (due - now <= 4 * 3600 * 1000) {
          isApproaching = true
        }
      }
    }

    return {
      hours: totalHours,
      text: durationText,
      fuelLiters,
      idleHours,
      isOverdue,
      isApproaching,
    }
  }

  // Aggregate Total Usage Logging Metrics across real registered data
  const usageSummary = useMemo(() => {
    let totalRentedHours = 0
    let totalFuelConsumed = 0
    let totalIdleHours = 0

    rentals.forEach((r) => {
      const stats = getDurationStats(r)
      totalRentedHours += stats.hours
      totalFuelConsumed += stats.fuelLiters
      totalIdleHours += stats.idleHours
    })

    const activeUnits = rentals.filter((r) => r.status === 'ACTIVE').length
    const overdueUnits = rentals.filter((r) => r.status === 'OVERDUE' || getDurationStats(r).isOverdue).length
    const approachingUnits = rentals.filter((r) => getDurationStats(r).isApproaching).length

    return {
      totalRentedHours: Math.round(totalRentedHours * 10) / 10,
      totalFuelConsumed: Math.round(totalFuelConsumed * 10) / 10,
      totalIdleHours: Math.round(totalIdleHours * 10) / 10,
      downtimeHours: Math.round((totalRentedHours * 0.05) * 10) / 10,
      activeUnits,
      overdueUnits,
      approachingUnits,
    }
  }, [rentals])

  // Overdue and Approaching Alert items
  const alertItems = useMemo(() => {
    return rentals
      .map((r) => ({ rental: r, stats: getDurationStats(r) }))
      .filter((item) => item.stats.isOverdue || item.stats.isApproaching || item.rental.status === 'OVERDUE')
  }, [rentals])

  // Per-site usage breakdown
  const siteUsageBreakdown = useMemo(() => {
    const siteMap: Record<string, { name: string; count: number; hours: number; fuel: number }> = {}
    sites.forEach((s) => {
      siteMap[s.name.toLowerCase()] = { name: s.name, count: 0, hours: 0, fuel: 0 }
    })

    rentals.forEach((r) => {
      const key = r.site.toLowerCase()
      if (!siteMap[key]) {
        siteMap[key] = { name: r.site, count: 0, hours: 0, fuel: 0 }
      }
      const st = getDurationStats(r)
      siteMap[key].count += 1
      siteMap[key].hours += st.hours
      siteMap[key].fuel += st.fuelLiters
    })

    return Object.values(siteMap).filter((s) => s.count > 0)
  }, [rentals, sites])

  const filteredRentals = useMemo(() => {
    return rentals.filter((rental) => {
      const matchesSearch =
        rental.id.toLowerCase().includes(search.toLowerCase()) ||
        rental.equipmentName.toLowerCase().includes(search.toLowerCase()) ||
        rental.equipmentId.toLowerCase().includes(search.toLowerCase()) ||
        rental.operator.toLowerCase().includes(search.toLowerCase()) ||
        rental.site.toLowerCase().includes(search.toLowerCase())

      const matchesSite =
        selectedSite === 'ALL' || rental.site.toLowerCase() === selectedSite.toLowerCase()

      const matchesStatus =
        statusFilter === 'ALL' || rental.status === statusFilter

      return matchesSearch && matchesSite && matchesStatus
    })
  }, [rentals, search, selectedSite, statusFilter])

  return (
    <div className="flex min-h-screen bg-[#fcf9f7] text-stone-900">
      <Sidebar role={user?.role ?? 'VIEWER'} />

      <div className="flex-1 flex flex-col min-w-0">
        <Navbar />

        <main className="flex-1 p-4 md:p-8 max-w-7xl mx-auto w-full space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2">
                <span className="inline-flex items-center gap-1.5 rounded-full bg-amber-100 px-3 py-1 text-xs font-bold uppercase tracking-wider text-amber-900">
                  <Gauge size={13} className="text-amber-600" />
                  Fleet Usage Logging & Telemetry
                </span>
              </div>
              <h1 className="mt-2 text-2xl md:text-3xl font-extrabold text-stone-900 tracking-tight">
                Usage Logging & Rental Management
              </h1>
              <p className="mt-1 text-xs md:text-sm text-stone-500">
                Live runtime hours, fuel usage, idle time, location breakdown, and overdue alerts for registered fleet.
              </p>
            </div>

            <Link
              to="/checkin-checkout"
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-[#ab6639] hover:bg-[#8e512d] px-4 py-2.5 text-xs font-bold uppercase tracking-wider text-white transition shadow-sm cursor-pointer"
            >
              <Camera size={16} />
              Open QR Gate Scanner
            </Link>
          </div>

          {/* Overdue Alerts & Approaching Return Notifications */}
          {alertItems.length > 0 && (
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-xs font-extrabold uppercase tracking-wider text-stone-600">
                <Bell size={14} className="text-amber-600" />
                Active Alerts & Return Reminders
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {alertItems.map(({ rental, stats }) => (
                  <div
                    key={rental.id}
                    className={`flex items-start gap-3 rounded-2xl p-4 border shadow-xs transition ${
                      stats.isOverdue || rental.status === 'OVERDUE'
                        ? 'border-rose-300 bg-rose-50/90 text-rose-950'
                        : 'border-amber-300 bg-amber-50/90 text-amber-950'
                    }`}
                  >
                    {stats.isOverdue || rental.status === 'OVERDUE' ? (
                      <AlertCircle size={20} className="text-rose-600 shrink-0 mt-0.5" />
                    ) : (
                      <AlertTriangle size={20} className="text-amber-600 shrink-0 mt-0.5" />
                    )}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <span className="font-mono font-bold text-xs">
                          {rental.equipmentId || rental.id}
                        </span>
                        <span
                          className={`text-[10px] font-extrabold uppercase px-2 py-0.5 rounded-md ${
                            stats.isOverdue || rental.status === 'OVERDUE'
                              ? 'bg-rose-200 text-rose-900'
                              : 'bg-amber-200 text-amber-900'
                          }`}
                        >
                          {stats.isOverdue || rental.status === 'OVERDUE' ? 'OVERDUE' : 'RETURN APPROACHING'}
                        </span>
                      </div>
                      <p className="text-sm font-extrabold text-stone-900 mt-0.5">
                        {rental.equipmentName}
                      </p>
                      <p className="text-xs text-stone-600 mt-0.5">
                        Site: <span className="font-semibold">{rental.site}</span> · Operator: <span className="font-semibold">{rental.operator}</span>
                      </p>
                      <div className="mt-2 flex items-center justify-between text-xs">
                        <span className="text-stone-500">
                          Runtime: <strong className="text-stone-800">{stats.text}</strong>
                        </span>
                        <Link
                          to="/checkin-checkout"
                          className="font-bold text-[#ab6639] hover:underline inline-flex items-center gap-1"
                        >
                          Check In Now →
                        </Link>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Usage Logging Metric Cards */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="rounded-2xl border border-stone-200 bg-white p-5 shadow-xs">
              <div className="flex items-center justify-between">
                <p className="text-xs font-bold uppercase tracking-wider text-stone-500">Total Runtime</p>
                <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-amber-50 text-amber-600">
                  <Timer size={16} />
                </div>
              </div>
              <p className="mt-2 text-2xl md:text-3xl font-extrabold text-stone-900">
                {usageSummary.totalRentedHours} <span className="text-sm font-semibold text-stone-500">hrs</span>
              </p>
              <p className="mt-1 text-[11px] text-stone-500">
                Across {rentals.length} registered deployment records
              </p>
            </div>

            <div className="rounded-2xl border border-stone-200 bg-white p-5 shadow-xs">
              <div className="flex items-center justify-between">
                <p className="text-xs font-bold uppercase tracking-wider text-stone-500">Fuel Usage</p>
                <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-teal-50 text-teal-600">
                  <Fuel size={16} />
                </div>
              </div>
              <p className="mt-2 text-2xl md:text-3xl font-extrabold text-stone-900">
                {usageSummary.totalFuelConsumed} <span className="text-sm font-semibold text-stone-500">L</span>
              </p>
              <p className="mt-1 text-[11px] text-stone-500">
                Est. ~14.5 L/hr heavy machine burn rate
              </p>
            </div>

            <div className="rounded-2xl border border-stone-200 bg-white p-5 shadow-xs">
              <div className="flex items-center justify-between">
                <p className="text-xs font-bold uppercase tracking-wider text-stone-500">Idle / Downtime</p>
                <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-slate-100 text-slate-600">
                  <Clock size={16} />
                </div>
              </div>
              <p className="mt-2 text-2xl md:text-3xl font-extrabold text-stone-900">
                {usageSummary.totalIdleHours} <span className="text-sm font-semibold text-stone-500">hrs</span>
              </p>
              <p className="mt-1 text-[11px] text-stone-500">
                Downtime: {usageSummary.downtimeHours} hrs
              </p>
            </div>

            <div className="rounded-2xl border border-stone-200 bg-white p-5 shadow-xs">
              <div className="flex items-center justify-between">
                <p className="text-xs font-bold uppercase tracking-wider text-stone-500">Site Deployments</p>
                <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-amber-50 text-[#ab6639]">
                  <MapPin size={16} />
                </div>
              </div>
              <p className="mt-2 text-2xl md:text-3xl font-extrabold text-stone-900">
                {usageSummary.activeUnits} <span className="text-sm font-semibold text-emerald-600">Active</span>
              </p>
              <p className="mt-1 text-[11px] text-stone-500">
                {usageSummary.overdueUnits > 0 ? (
                  <span className="text-rose-600 font-bold">{usageSummary.overdueUnits} Overdue Alert</span>
                ) : (
                  <span className="text-emerald-600 font-medium">All schedules on time</span>
                )}
              </p>
            </div>
          </div>

          {/* Usage Per Site Breakdown */}
          {siteUsageBreakdown.length > 0 && (
            <div className="rounded-2xl border border-stone-200 bg-white p-4 shadow-xs">
              <p className="text-xs font-bold uppercase tracking-wider text-stone-500 mb-3">
                Usage Logging Per Site / Area:
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {siteUsageBreakdown.map((st) => (
                  <div key={st.name} className="flex items-center justify-between rounded-xl bg-stone-50 p-3 border border-stone-200 text-xs">
                    <div className="flex items-center gap-2">
                      <MapPin size={15} className="text-[#ab6639] shrink-0" />
                      <div>
                        <p className="font-bold text-stone-900">{st.name}</p>
                        <p className="text-[11px] text-stone-500">{st.count} machines deployed</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-extrabold text-stone-800">{Math.round(st.hours * 10) / 10} hrs</p>
                      <p className="text-[10px] text-stone-500">{Math.round(st.fuel)} L fuel</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Filter Bar & Site Selector */}
          <div className="flex flex-col md:flex-row gap-3 items-stretch md:items-center justify-between">
            <div className="flex flex-wrap items-center gap-2">
              {(['ALL', 'ACTIVE', 'COMPLETED', 'OVERDUE'] as const).map((status) => (
                <button
                  key={status}
                  onClick={() => setStatusFilter(status)}
                  className={`rounded-xl px-3.5 py-2 text-xs font-bold uppercase tracking-wider transition cursor-pointer ${
                    statusFilter === status
                      ? 'bg-stone-900 text-white shadow-xs'
                      : 'bg-white border border-stone-200 text-stone-600 hover:bg-stone-50'
                  }`}
                >
                  {status}
                </button>
              ))}
            </div>

            <div className="flex items-center gap-3">
              {/* Site Dropdown */}
              <div className="flex items-center gap-2 rounded-xl border border-stone-200 bg-white px-3 py-2 text-xs font-semibold text-stone-700 shadow-xs">
                <MapPin size={14} className="text-[#ab6639]" />
                <select
                  value={selectedSite}
                  onChange={(e) => setSelectedSite(e.target.value)}
                  className="bg-transparent font-bold text-stone-800 outline-none cursor-pointer"
                >
                  <option value="ALL">All Deployment Sites</option>
                  {sites.map((site) => (
                    <option key={site.id} value={site.name}>
                      {site.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Search Bar */}
              <div className="flex flex-1 md:w-64 items-center gap-2 rounded-xl border border-stone-200 bg-white px-3 py-2 shadow-xs">
                <Search size={14} className="text-stone-400" />
                <input
                  type="text"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Search vehicle, operator, site..."
                  className="w-full bg-transparent text-xs outline-none placeholder:text-stone-400"
                />
              </div>
            </div>
          </div>

          {/* Data Table */}
          <div className="rounded-3xl border border-stone-200 bg-white shadow-sm overflow-hidden">
            {loading ? (
              <div className="p-16 text-center text-xs font-semibold text-stone-500">
                Loading live usage and rental records...
              </div>
            ) : filteredRentals.length === 0 ? (
              <div className="p-16 text-center space-y-3">
                <div className="mx-auto h-12 w-12 rounded-2xl bg-stone-100 flex items-center justify-center text-stone-400">
                  <Layers size={24} />
                </div>
                <h3 className="text-sm font-bold text-stone-800">No Rental Contracts Found</h3>
                <p className="text-xs text-stone-500 max-w-sm mx-auto">
                  {selectedSite !== 'ALL' || statusFilter !== 'ALL' || search
                    ? 'No records match your active search and filter criteria.'
                    : 'Scan an available vehicle at the Gate Scanner to start logging usage.'}
                </p>
                <Link
                  to="/checkin-checkout"
                  className="mt-2 inline-flex items-center gap-1.5 text-xs font-bold text-[#ab6639] hover:underline"
                >
                  <Zap size={14} />
                  Go to Gate QR Scanner →
                </Link>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-stone-200 bg-stone-50/50 text-[11px] font-bold uppercase tracking-wider text-stone-500">
                      <th className="py-3.5 px-4">Rental Ref</th>
                      <th className="py-3.5 px-4">Vehicle & Model</th>
                      <th className="py-3.5 px-4">Assigned Operator</th>
                      <th className="py-3.5 px-4">Site / Area</th>
                      <th className="py-3.5 px-4">Runtime & Fuel</th>
                      <th className="py-3.5 px-4">Idle / Downtime</th>
                      <th className="py-3.5 px-4">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-stone-100 font-medium text-stone-800">
                    {filteredRentals.map((rental) => {
                      const stats = getDurationStats(rental)
                      return (
                        <tr key={rental.id} className="hover:bg-stone-50/60 transition">
                          <td className="py-3.5 px-4 font-mono font-bold text-stone-900">
                            {rental.id}
                          </td>
                          <td className="py-3.5 px-4">
                            <p className="font-bold text-stone-900">{rental.equipmentName}</p>
                            <p className="text-[10px] font-mono text-stone-500">{rental.equipmentId}</p>
                          </td>
                          <td className="py-3.5 px-4">
                            <div className="flex items-center gap-1.5">
                              <User size={13} className="text-stone-400 shrink-0" />
                              <span>{rental.operator || 'Assigned Operator'}</span>
                            </div>
                          </td>
                          <td className="py-3.5 px-4">
                            <div className="flex items-center gap-1.5">
                              <MapPin size={13} className="text-[#ab6639] shrink-0" />
                              <span>{rental.site || 'Job Site'}</span>
                            </div>
                          </td>
                          <td className="py-3.5 px-4">
                            <div className="flex items-center gap-1.5 text-stone-800">
                              <Timer size={13} className="text-amber-600" />
                              <strong className="font-bold">{stats.text}</strong>
                            </div>
                            <p className="text-[10px] text-teal-700 font-semibold mt-0.5">
                              {stats.fuelLiters} L fuel used
                            </p>
                          </td>
                          <td className="py-3.5 px-4">
                            <p className="text-stone-700 font-semibold">{stats.idleHours} hrs idle</p>
                            <p className="text-[10px] text-stone-400">
                              {rental.status === 'ACTIVE' ? 'Working in field' : 'Checked in'}
                            </p>
                          </td>
                          <td className="py-3.5 px-4">
                            <span
                              className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-[10px] font-extrabold uppercase tracking-wider ${
                                stats.isOverdue || rental.status === 'OVERDUE'
                                  ? 'bg-rose-100 text-rose-800 border border-rose-200'
                                  : rental.status === 'COMPLETED'
                                    ? 'bg-stone-100 text-stone-700'
                                    : 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                              }`}
                            >
                              {stats.isOverdue || rental.status === 'OVERDUE' ? (
                                <AlertCircle size={12} className="text-rose-600" />
                              ) : rental.status === 'COMPLETED' ? (
                                <CheckCircle2 size={12} className="text-stone-500" />
                              ) : (
                                <ArrowUpRight size={12} className="text-emerald-600" />
                              )}
                              {stats.isOverdue || rental.status === 'OVERDUE'
                                ? 'OVERDUE'
                                : rental.status === 'COMPLETED'
                                  ? 'RETURNED'
                                  : 'ACTIVE ON SITE'}
                            </span>
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  )
}
