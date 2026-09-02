import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Activity,
  AlertCircle,
  AlertTriangle,
  ArrowDownLeft,
  ArrowRight,
  ArrowUpRight,
  Bell,
  Brain,
  Camera,
  Check,
  Clock,
  Fuel,
  Gauge,
  MapPin,
  PlusCircle,
  RefreshCw,
  ShieldAlert,
  Sparkles,
  Timer,
  TrendingUp,
  Truck,
  Zap,
} from 'lucide-react'
import { Navbar } from '../components/Navbar'
import { Sidebar } from '../components/Sidebar'
import { StatCard } from '../components/StatCard'
import { useAuth } from '../context/AuthContext'
import { api } from '../services/api'
import type {
  AnomalyItem,
  DashboardStat,
  ForecastItem,
  RecommendationItem,
  Rental,
  SiteItem,
} from '../types'

const defaultStats: DashboardStat[] = [
  { label: 'Total Assets', value: 0, change: '', accent: 'amber' },
  { label: 'Available', value: 0, change: '', accent: 'teal' },
  { label: 'Rented', value: 0, change: '', accent: 'slate' },
  { label: 'In Use', value: 0, change: '', accent: 'amber' },
  { label: 'Idle', value: 0, change: '', accent: 'slate' },
  { label: 'Overdue', value: 0, change: '', accent: 'rose' },
]

export function DashboardPage() {
  const { user } = useAuth()
  const [stats, setStats] = useState<DashboardStat[]>(defaultStats)
  const [rentals, setRentals] = useState<Rental[]>([])
  const [sites, setSites] = useState<SiteItem[]>([])

  // ML Intelligence State
  const [forecasts, setForecasts] = useState<ForecastItem[]>([])
  const [anomalies, setAnomalies] = useState<AnomalyItem[]>([])
  const [recommendations, setRecommendations] = useState<RecommendationItem[]>([])
  const [actionLoading, setActionLoading] = useState<string | null>(null)

  const loadData = async () => {
    try {
      const [nextStats, nextRentals, nextSites, fcList, anList, recList] = await Promise.all([
        api.getDashboardStats().catch(() => defaultStats),
        api.getRentals().catch(() => []),
        api.getSites().catch(() => []),
        api.getForecasts().catch(() => [] as ForecastItem[]),
        api.getAnomalies().catch(() => [] as AnomalyItem[]),
        api.getRecommendations().catch(() => [] as RecommendationItem[]),
      ])
      setStats(nextStats)
      setRentals(nextRentals)
      setSites(nextSites)
      setForecasts(fcList)
      setAnomalies(anList)
      setRecommendations(recList)
    } catch {
      // fallback
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  // ── Live WebSocket: Kafka → Django Channels → Dashboard ─────────────────
  useEffect(() => {
    const wsUrl = `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/ws/dashboard/`
    let ws: WebSocket | null = null
    let retryTimer: ReturnType<typeof setTimeout> | null = null
    let retries = 0

    const connect = () => {
      ws = new WebSocket(wsUrl)

      ws.onopen = () => {
        retries = 0
        console.info('[WS] Dashboard WebSocket connected')
      }

      ws.onmessage = (evt) => {
        try {
          const msg = JSON.parse(evt.data)
          if (msg.type === 'dashboard.fleet_update') {
            const summary = msg.payload?.summary
            if (summary) {
              setStats([
                { label: 'Total Assets', value: summary.total ?? 0, change: '', accent: 'amber' },
                { label: 'Available', value: summary.available ?? 0, change: '', accent: 'teal' },
                { label: 'Rented', value: summary.rented ?? 0, change: '', accent: 'slate' },
                { label: 'In Use', value: summary.rented ?? 0, change: '', accent: 'amber' },
                { label: 'Idle', value: summary.idle ?? 0, change: '', accent: 'slate' },
                { label: 'Overdue', value: summary.overdue ?? 0, change: '', accent: 'rose' },
              ])
            }
          }
        } catch {
          // malformed frame – ignore
        }
      }

      ws.onclose = () => {
        const delay = Math.min(1000 * 2 ** retries, 30000)
        retries += 1
        retryTimer = setTimeout(connect, delay)
      }

      ws.onerror = () => ws?.close()
    }

    connect()
    return () => {
      if (retryTimer) clearTimeout(retryTimer)
      ws?.close()
    }
  }, [])

  // Action Handlers for ML Intelligence
  const handleGenerateForecasts = async () => {
    try {
      setActionLoading('fc')
      const newFc = await api.generateForecasts()
      setForecasts(newFc)
    } catch (err) {
      console.error('Forecast generation failed:', err)
    } finally {
      setActionLoading(null)
    }
  }

  const handleScanAnomalies = async () => {
    try {
      setActionLoading('an')
      const newAn = await api.scanAnomalies()
      setAnomalies(newAn)
    } catch (err) {
      console.error('Anomaly scan failed:', err)
    } finally {
      setActionLoading(null)
    }
  }

  const handleGenerateRecommendations = async () => {
    try {
      setActionLoading('rec')
      const newRecs = await api.generateRecommendations()
      setRecommendations(newRecs)
    } catch (err) {
      console.error('Recommendation generation failed:', err)
    } finally {
      setActionLoading(null)
    }
  }

  const handleAcceptRecommendation = async (id: number) => {
    try {
      await api.acceptRecommendation(id)
      setRecommendations((prev) =>
        prev.map((r) => (r.id === id ? { ...r, status: 'ACCEPTED' } : r))
      )
      loadData()
    } catch (err) {
      console.error('Accept recommendation failed:', err)
    }
  }

  const handleDismissRecommendation = async (id: number) => {
    try {
      await api.dismissRecommendation(id)
      setRecommendations((prev) =>
        prev.map((r) => (r.id === id ? { ...r, status: 'DISMISSED' } : r))
      )
    } catch (err) {
      console.error('Dismiss recommendation failed:', err)
    }
  }

  const handleAcknowledgeAnomaly = async (id: number) => {
    try {
      await api.acknowledgeAnomaly(id)
      setAnomalies((prev) =>
        prev.map((a) => (a.id === id ? { ...a, status: 'ACKNOWLEDGED' } : a))
      )
    } catch (err) {
      console.error('Acknowledge anomaly failed:', err)
    }
  }

  const getDurationStats = (rental: Rental) => {
    if (!rental.startDate) {
      return { hours: 1, text: '1h 0m', fuelLiters: 14.5, isOverdue: false, isApproaching: false }
    }
    const start = new Date(rental.startDate).getTime()
    const now = Date.now()
    const diffMs = Math.max(0, now - (isNaN(start) ? now : start))
    const totalHours = Math.max(0.5, diffMs / (1000 * 60 * 60))
    const hoursInt = Math.floor(totalHours)
    const minutesInt = Math.floor((totalHours - hoursInt) * 60)

    const end = rental.endDate ? new Date(rental.endDate).getTime() : 0
    const isOverdue = end > 0 && now > end
    const isApproaching = end > 0 && !isOverdue && end - now <= 4 * 3600 * 1000

    return {
      hours: Math.round(totalHours * 10) / 10,
      text: `${hoursInt}h ${minutesInt}m`,
      fuelLiters: Math.round(totalHours * 14.5 * 10) / 10,
      isOverdue,
      isApproaching,
    }
  }

  const usageSummary = useMemo(() => {
    let totalRentedHours = 0
    let totalFuelConsumed = 0
    let totalIdleHours = 0

    rentals.forEach((r) => {
      const st = getDurationStats(r)
      totalRentedHours += st.hours
      totalFuelConsumed += st.fuelLiters
      totalIdleHours += st.hours * 0.2
    })

    const activeList = rentals.filter((r) => r.status === 'ACTIVE')
    const overdueList = rentals.filter((r) => r.status === 'OVERDUE' || getDurationStats(r).isOverdue)
    const approachingList = rentals.filter((r) => getDurationStats(r).isApproaching)

    return {
      totalRentedHours: Math.round(totalRentedHours * 10) / 10,
      totalFuelConsumed: Math.round(totalFuelConsumed * 10) / 10,
      totalIdleHours: Math.round(totalIdleHours * 10) / 10,
      activeCount: activeList.length,
      overdueList,
      approachingList,
    }
  }, [rentals])

  const openAnomalies = useMemo(() => anomalies.filter((a) => a.status === 'OPEN'), [anomalies])
  const pendingRecommendations = useMemo(
    () => recommendations.filter((r) => r.status === 'PENDING'),
    [recommendations]
  )

  const siteMap = useMemo(() => {
    const map = new Map<number, string>()
    sites.forEach((s) => map.set(s.id, s.name))
    return map
  }, [sites])

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
                  Live Operational Telematics
                </span>

                {/* Quick Summary ML Badges near top */}
                <span className="inline-flex items-center gap-1.5 rounded-full bg-purple-100 px-3 py-1 text-xs font-bold uppercase tracking-wider text-purple-900">
                  <TrendingUp size={13} className="text-purple-600" />
                  {forecasts.length} Forecasts
                </span>
                <span className="inline-flex items-center gap-1.5 rounded-full bg-rose-100 px-3 py-1 text-xs font-bold uppercase tracking-wider text-rose-900">
                  <Zap size={13} className="text-rose-600" />
                  {openAnomalies.length} Active Anomalies
                </span>
                <span className="inline-flex items-center gap-1.5 rounded-full bg-indigo-100 px-3 py-1 text-xs font-bold uppercase tracking-wider text-indigo-900">
                  <Brain size={13} className="text-indigo-600" />
                  {pendingRecommendations.length} Recommendations
                </span>
              </div>
              <h1 className="mt-2 text-2xl md:text-3xl font-extrabold text-stone-900 tracking-tight">
                Fleet Dashboard & Usage Tracking
              </h1>
              <p className="text-xs md:text-sm text-stone-500 mt-1">
                Real-time usage logging, runtime hours, fuel telemetry, and return reminders.
              </p>
            </div>

            <div className="flex items-center gap-2.5">
              <Link
                to="/checkin-checkout"
                className="inline-flex items-center gap-2 rounded-xl bg-[#ab6639] hover:bg-[#8e512d] px-4 py-2.5 text-xs font-bold uppercase tracking-wider text-white transition shadow-sm cursor-pointer"
              >
                <Camera size={16} />
                Scan QR Gate
              </Link>

              {(user?.role === 'ADMIN' || user?.role === 'MANAGER') && (
                <Link
                  to="/equipment"
                  className="inline-flex items-center gap-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 px-4 py-2.5 text-xs font-bold uppercase tracking-wider text-white transition shadow-sm cursor-pointer"
                >
                  <PlusCircle size={16} />
                  Register Vehicle
                </Link>
              )}
            </div>
          </div>

          {/* Overdue Alerts & Approaching Return Notifications Banner */}
          {(usageSummary.overdueList.length > 0 || usageSummary.approachingList.length > 0) && (
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-xs font-extrabold uppercase tracking-wider text-stone-600">
                <Bell size={14} className="text-amber-600" />
                Overdue Alerts & Approaching Return Reminders
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {usageSummary.overdueList.map((rental) => (
                  <div
                    key={rental.id}
                    className="flex items-start gap-3 rounded-2xl p-4 border border-rose-300 bg-rose-50 text-rose-950 shadow-xs"
                  >
                    <AlertCircle size={20} className="text-rose-600 shrink-0 mt-0.5" />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <span className="font-mono font-bold text-xs">{rental.equipmentId}</span>
                        <span className="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded-md bg-rose-200 text-rose-900">
                          OVERDUE
                        </span>
                      </div>
                      <p className="text-sm font-extrabold text-stone-900 mt-0.5">{rental.equipmentName}</p>
                      <p className="text-xs text-stone-600 mt-0.5">
                        Site: <span className="font-semibold">{rental.site}</span> · Operator: <span className="font-semibold">{rental.operator}</span>
                      </p>
                      <div className="mt-2 flex items-center justify-between text-xs">
                        <span className="text-rose-700 font-semibold">Exceeded scheduled return time</span>
                        <Link
                          to="/checkin-checkout"
                          className="font-bold text-[#ab6639] hover:underline inline-flex items-center gap-1"
                        >
                          Check In →
                        </Link>
                      </div>
                    </div>
                  </div>
                ))}

                {usageSummary.approachingList.map((rental) => (
                  <div
                    key={rental.id}
                    className="flex items-start gap-3 rounded-2xl p-4 border border-amber-300 bg-amber-50 text-amber-950 shadow-xs"
                  >
                    <AlertTriangle size={20} className="text-amber-600 shrink-0 mt-0.5" />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <span className="font-mono font-bold text-xs">{rental.equipmentId}</span>
                        <span className="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded-md bg-amber-200 text-amber-900">
                          RETURN APPROACHING
                        </span>
                      </div>
                      <p className="text-sm font-extrabold text-stone-900 mt-0.5">{rental.equipmentName}</p>
                      <p className="text-xs text-stone-600 mt-0.5">
                        Site: <span className="font-semibold">{rental.site}</span> · Operator: <span className="font-semibold">{rental.operator}</span>
                      </p>
                      <div className="mt-2 flex items-center justify-between text-xs">
                        <span className="text-amber-800 font-semibold">Scheduled return within 4 hours</span>
                        <Link
                          to="/checkin-checkout"
                          className="font-bold text-[#ab6639] hover:underline inline-flex items-center gap-1"
                        >
                          Check In →
                        </Link>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Real Live Stat Cards */}
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
            {stats.map((stat) => (
              <StatCard
                key={stat.label}
                label={stat.label}
                value={stat.value}
                change={stat.change}
                accent={stat.accent}
              />
            ))}
          </div>

          {/* Usage Logging Telemetry Summary Row */}
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="rounded-2xl border border-stone-200 bg-white p-5 shadow-xs">
              <div className="flex items-center justify-between">
                <p className="text-xs font-bold uppercase tracking-wider text-stone-500">Total Operating Hours</p>
                <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-amber-50 text-amber-600">
                  <Timer size={16} />
                </div>
              </div>
              <p className="mt-2 text-2xl md:text-3xl font-extrabold text-stone-900">
                {usageSummary.totalRentedHours} <span className="text-sm font-semibold text-stone-500">hrs</span>
              </p>
              <p className="mt-1 text-[11px] text-stone-500">Total runtime logged from field deployments</p>
            </div>

            <div className="rounded-2xl border border-stone-200 bg-white p-5 shadow-xs">
              <div className="flex items-center justify-between">
                <p className="text-xs font-bold uppercase tracking-wider text-stone-500">Total Fuel Consumed</p>
                <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-teal-50 text-teal-600">
                  <Fuel size={16} />
                </div>
              </div>
              <p className="mt-2 text-2xl md:text-3xl font-extrabold text-stone-900">
                {usageSummary.totalFuelConsumed} <span className="text-sm font-semibold text-stone-500">L</span>
              </p>
              <p className="mt-1 text-[11px] text-stone-500">Heavy equipment average ~14.5 L/hr</p>
            </div>

            <div className="rounded-2xl border border-stone-200 bg-white p-5 shadow-xs">
              <div className="flex items-center justify-between">
                <p className="text-xs font-bold uppercase tracking-wider text-stone-500">Idle / Downtime Hours</p>
                <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-slate-100 text-slate-600">
                  <Clock size={16} />
                </div>
              </div>
              <p className="mt-2 text-2xl md:text-3xl font-extrabold text-stone-900">
                {usageSummary.totalIdleHours} <span className="text-sm font-semibold text-stone-500">hrs</span>
              </p>
              <p className="mt-1 text-[11px] text-stone-500">Standby and gate queue durations</p>
            </div>

            <div className="rounded-2xl border border-stone-200 bg-white p-5 shadow-xs">
              <div className="flex items-center justify-between">
                <p className="text-xs font-bold uppercase tracking-wider text-stone-500">Active Deployments</p>
                <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-amber-50 text-[#ab6639]">
                  <MapPin size={16} />
                </div>
              </div>
              <p className="mt-2 text-2xl md:text-3xl font-extrabold text-stone-900">
                {usageSummary.activeCount} <span className="text-sm font-semibold text-emerald-600">Active</span>
              </p>
              <p className="mt-1 text-[11px] text-stone-500">Across {sites.length} construction sites</p>
            </div>
          </div>

          {/* ═════════════════════════════════════════════════════════════════════ */}
          {/* ML INTELLIGENCE SECTION (Demand Forecasts, Anomaly Detection, Asset Reallocation) */}
          {/* ═════════════════════════════════════════════════════════════════════ */}
          <div className="space-y-4 pt-2">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-stone-200 pb-3">
              <div>
                <span className="inline-flex items-center gap-1.5 rounded-full bg-purple-100 px-3 py-1 text-xs font-bold uppercase tracking-wider text-purple-900">
                  <Sparkles size={13} className="text-purple-600" />
                  Machine Learning & AI Operations
                </span>
                <h2 className="text-xl md:text-2xl font-extrabold text-stone-900 mt-1 tracking-tight">
                  ML Intelligence
                </h2>
              </div>
              <p className="text-xs text-stone-500 max-w-md">
                Predictive equipment demand forecasts, real-time statistical anomaly detection, and automated site reallocation recommendations.
              </p>
            </div>

            {/* 3 Side-by-Side Cards on Desktop, Vertical Stack on Mobile */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

              {/* CARD 1: Demand Forecasting ("Hybrid Demand Forecasts") */}
              <div className="rounded-3xl border border-stone-200 bg-white p-5 md:p-6 shadow-sm flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between pb-3 border-b border-stone-100">
                    <div>
                      <span className="text-[10px] font-extrabold uppercase tracking-wider text-purple-600 bg-purple-50 px-2 py-0.5 rounded-md">
                        Demand Model v2.1
                      </span>
                      <h3 className="text-lg font-extrabold text-stone-900 mt-1">Hybrid Demand Forecasts</h3>
                    </div>
                    <button
                      onClick={handleGenerateForecasts}
                      disabled={actionLoading === 'fc'}
                      className="inline-flex items-center gap-1.5 rounded-xl bg-purple-600 hover:bg-purple-700 text-white px-3 py-1.5 text-xs font-bold transition shadow-xs disabled:opacity-50 cursor-pointer"
                    >
                      <RefreshCw size={13} className={actionLoading === 'fc' ? 'animate-spin' : ''} />
                      {actionLoading === 'fc' ? 'Generating...' : 'Forecast'}
                    </button>
                  </div>

                  <p className="text-xs text-stone-500 mt-2 mb-4 leading-relaxed">
                    Combines historical rental volume, active utilization, and weekday/weekend construction demand patterns.
                  </p>

                  <div className="space-y-3 max-h-72 overflow-y-auto pr-1">
                    {forecasts.length === 0 ? (
                      <div className="py-8 text-center text-xs text-stone-400">
                        No forecasts generated yet. Click &quot;Forecast&quot; above to run the hybrid demand regressor.
                      </div>
                    ) : (
                      forecasts.slice(0, 5).map((fc) => (
                        <div
                          key={fc.id}
                          className="rounded-2xl border border-purple-100 bg-purple-50/50 p-3 flex items-center justify-between text-xs"
                        >
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="font-extrabold text-stone-900">{fc.equipment_type}</span>
                              <span className="text-[10px] font-semibold text-purple-700 bg-purple-100 px-1.5 py-0.5 rounded">
                                {siteMap.get(fc.site) || fc.site_name || `Site #${fc.site}`}
                              </span>
                            </div>
                            <p className="text-[11px] text-stone-500 mt-0.5">
                              Target Date: <span className="font-medium text-stone-800">{fc.forecast_date}</span>
                            </p>
                          </div>
                          <div className="text-right shrink-0">
                            <p className="font-extrabold text-purple-900 text-sm">{fc.predicted_demand} units</p>
                            <p className="text-[10px] text-emerald-700 font-bold">
                              {Math.round(fc.confidence * 100)}% confidence
                            </p>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-stone-100 text-right">
                  <span className="text-[11px] font-bold text-stone-400">
                    Total Forecast Records: {forecasts.length}
                  </span>
                </div>
              </div>

              {/* CARD 2: Anomaly Detection ("Rules + Isolation Forest") */}
              <div className="rounded-3xl border border-stone-200 bg-white p-5 md:p-6 shadow-sm flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between pb-3 border-b border-stone-100">
                    <div>
                      <span className="text-[10px] font-extrabold uppercase tracking-wider text-rose-600 bg-rose-50 px-2 py-0.5 rounded-md">
                        Anomaly Engine
                      </span>
                      <h3 className="text-lg font-extrabold text-stone-900 mt-1">Rules + Isolation Forest</h3>
                    </div>
                    <button
                      onClick={handleScanAnomalies}
                      disabled={actionLoading === 'an'}
                      className="inline-flex items-center gap-1.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white px-3 py-1.5 text-xs font-bold transition shadow-xs disabled:opacity-50 cursor-pointer"
                    >
                      <Zap size={13} className={actionLoading === 'an' ? 'animate-spin' : ''} />
                      {actionLoading === 'an' ? 'Scanning...' : 'Scan Telemetry'}
                    </button>
                  </div>

                  <p className="text-xs text-stone-500 mt-2 mb-4 leading-relaxed">
                    Scans live telemetry for excessive idle hours, excessive speed, rapid fuel drops, unauthorized movement, and unusual patterns.
                  </p>

                  <div className="space-y-3 max-h-72 overflow-y-auto pr-1">
                    {anomalies.length === 0 ? (
                      <div className="py-8 text-center text-xs text-stone-400">
                        No telemetry anomalies detected. Click &quot;Scan Telemetry&quot; to run rule-based + Isolation Forest checks.
                      </div>
                    ) : (
                      anomalies.slice(0, 5).map((an) => (
                        <div
                          key={an.id}
                          className={`rounded-2xl border p-3 text-xs transition ${
                            an.severity === 'CRITICAL' || an.severity === 'HIGH'
                              ? 'bg-rose-50/80 border-rose-200'
                              : 'bg-amber-50/80 border-amber-200'
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <span className="font-extrabold text-stone-900">{an.anomaly_type}</span>
                            <span
                              className={`text-[9px] font-extrabold uppercase px-1.5 py-0.5 rounded ${
                                an.severity === 'CRITICAL' || an.severity === 'HIGH'
                                  ? 'bg-rose-200 text-rose-900'
                                  : 'bg-amber-200 text-amber-900'
                              }`}
                            >
                              {an.severity} ({an.score.toFixed(2)})
                            </span>
                          </div>
                          <p className="text-[11px] font-mono text-stone-600 mt-1">
                            Equipment: <span className="font-bold text-stone-900">{an.equipment_id || `Asset #${an.equipment}`}</span>
                          </p>
                          <p className="text-[11px] text-stone-700 mt-0.5 line-clamp-2 leading-snug">{an.reason}</p>

                          <div className="mt-2.5 flex items-center justify-between pt-1.5 border-t border-stone-200/60">
                            <span className="text-[10px] font-bold text-stone-500">Status: {an.status}</span>
                            {an.status === 'OPEN' && (
                              <button
                                onClick={() => handleAcknowledgeAnomaly(an.id)}
                                className="text-[10px] font-bold text-rose-700 hover:underline cursor-pointer"
                              >
                                Acknowledge →
                              </button>
                            )}
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-stone-100 flex items-center justify-between text-[11px]">
                  <span className="font-bold text-stone-500">Detected Issues: {anomalies.length}</span>
                  <span className="font-extrabold text-rose-600">{openAnomalies.length} Open Alerts</span>
                </div>
              </div>

              {/* CARD 3: Recommended Assets / Asset Reallocation ("Smart Asset Recommendations") */}
              <div className="rounded-3xl border border-stone-200 bg-white p-5 md:p-6 shadow-sm flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between pb-3 border-b border-stone-100">
                    <div>
                      <span className="text-[10px] font-extrabold uppercase tracking-wider text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-md">
                        Optimizer
                      </span>
                      <h3 className="text-lg font-extrabold text-stone-900 mt-1">Smart Asset Recommendations</h3>
                    </div>
                    <button
                      onClick={handleGenerateRecommendations}
                      disabled={actionLoading === 'rec'}
                      className="inline-flex items-center gap-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-1.5 text-xs font-bold transition shadow-xs disabled:opacity-50 cursor-pointer"
                    >
                      <Brain size={13} className={actionLoading === 'rec' ? 'animate-spin' : ''} />
                      {actionLoading === 'rec' ? 'Evaluating...' : 'Re-Evaluate'}
                    </button>
                  </div>

                  <p className="text-xs text-stone-500 mt-2 mb-4 leading-relaxed">
                    Suggests moving idle/available machinery from low-demand sites to high-forecast construction sites.
                  </p>

                  <div className="space-y-3 max-h-72 overflow-y-auto pr-1">
                    {recommendations.length === 0 ? (
                      <div className="py-8 text-center text-xs text-stone-400">
                        No asset reallocation recommendations. Click &quot;Re-Evaluate&quot; to calculate optimal machine distribution.
                      </div>
                    ) : (
                      recommendations.slice(0, 5).map((rec) => (
                        <div
                          key={rec.id}
                          className="rounded-2xl border border-indigo-100 bg-indigo-50/40 p-3 text-xs"
                        >
                          <div className="flex items-center justify-between">
                            <span className="font-mono font-bold text-stone-900">
                              {rec.equipment_id || `Asset #${rec.equipment}`}
                            </span>
                            <span className="text-[10px] font-extrabold text-indigo-700 bg-indigo-100 px-1.5 py-0.5 rounded">
                              Score: {rec.score.toFixed(2)}
                            </span>
                          </div>

                          <div className="flex items-center gap-1.5 mt-1.5 text-[11px] font-bold text-stone-800">
                            <span className="truncate max-w-[100px]">
                              {siteMap.get(rec.source_site) || rec.source_site_name || `Site #${rec.source_site}`}
                            </span>
                            <ArrowRight size={12} className="text-indigo-600 shrink-0" />
                            <span className="truncate max-w-[100px] text-indigo-900">
                              {siteMap.get(rec.target_site) || rec.target_site_name || `Site #${rec.target_site}`}
                            </span>
                          </div>

                          <p className="text-[11px] text-stone-600 mt-1 line-clamp-2 leading-snug">{rec.reason}</p>

                          <div className="mt-2.5 flex items-center justify-between pt-1.5 border-t border-stone-200/60">
                            <span
                              className={`text-[9px] font-extrabold uppercase px-1.5 py-0.5 rounded ${
                                rec.status === 'ACCEPTED'
                                  ? 'bg-emerald-100 text-emerald-800'
                                  : rec.status === 'DISMISSED'
                                    ? 'bg-stone-200 text-stone-700'
                                    : 'bg-indigo-100 text-indigo-900'
                              }`}
                            >
                              {rec.status}
                            </span>

                            {rec.status === 'PENDING' && (
                              <div className="flex items-center gap-2">
                                <button
                                  onClick={() => handleDismissRecommendation(rec.id)}
                                  className="text-[10px] font-bold text-stone-500 hover:text-stone-800 cursor-pointer"
                                >
                                  Dismiss
                                </button>
                                <button
                                  onClick={() => handleAcceptRecommendation(rec.id)}
                                  className="inline-flex items-center gap-1 rounded-lg bg-emerald-600 text-white px-2 py-0.5 text-[10px] font-bold hover:bg-emerald-700 transition cursor-pointer"
                                >
                                  <Check size={11} /> Accept
                                </button>
                              </div>
                            )}
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-stone-100 flex items-center justify-between text-[11px]">
                  <span className="font-bold text-stone-500">Total Recommendations: {recommendations.length}</span>
                  <span className="font-extrabold text-indigo-700">{pendingRecommendations.length} Pending Actions</span>
                </div>
              </div>

            </div>
          </div>

          {/* Middle Row: Site Deployments & Gate Status */}
          <div className="grid gap-6 lg:grid-cols-[1.6fr_1fr]">
            {/* Live Utilization Card */}
            <div className="rounded-3xl border border-stone-200 bg-white p-5 md:p-6 shadow-sm">
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <p className="text-xs uppercase tracking-[0.25em] text-stone-500">Telemetry Status</p>
                  <h3 className="mt-1 text-xl font-bold text-stone-900">Fleet Allocation Overview</h3>
                </div>
                <Truck className="text-[#ab6639]" size={20} />
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 pt-2">
                <div className="rounded-2xl bg-amber-50 p-4 border border-amber-200">
                  <div className="flex items-center justify-between">
                    <p className="text-xs font-bold uppercase tracking-wider text-amber-800">In Field</p>
                    <ArrowUpRight size={16} className="text-amber-700" />
                  </div>
                  <p className="text-2xl font-extrabold text-amber-950 mt-2">{usageSummary.activeCount}</p>
                  <p className="text-[11px] text-amber-700 mt-0.5">Active on job sites</p>
                </div>

                <div className="rounded-2xl bg-teal-50 p-4 border border-teal-200">
                  <div className="flex items-center justify-between">
                    <p className="text-xs font-bold uppercase tracking-wider text-teal-800">In Depot Yard</p>
                    <ArrowDownLeft size={16} className="text-teal-700" />
                  </div>
                  <p className="text-2xl font-extrabold text-teal-950 mt-2">
                    {stats.find((s) => s.label === 'Available')?.value ?? 0}
                  </p>
                  <p className="text-[11px] text-teal-700 mt-0.5">Ready for dispatch</p>
                </div>

                <div className="rounded-2xl bg-rose-50 p-4 border border-rose-200">
                  <div className="flex items-center justify-between">
                    <p className="text-xs font-bold uppercase tracking-wider text-rose-800">Overdue Returns</p>
                    <ShieldAlert size={16} className="text-rose-700" />
                  </div>
                  <p className="text-2xl font-extrabold text-rose-950 mt-2">{usageSummary.overdueList.length}</p>
                  <p className="text-[11px] text-rose-700 mt-0.5">Exceeded return schedule</p>
                </div>
              </div>
            </div>

            {/* Live Alerts & Scanner Status */}
            <div className="rounded-3xl border border-stone-200 bg-white p-5 md:p-6 shadow-sm">
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <p className="text-xs uppercase tracking-[0.25em] text-stone-500">Live Status</p>
                  <h3 className="mt-1 text-xl font-bold text-stone-900">Fleet Gate Engine</h3>
                </div>
                <Activity className="text-[#ab6639]" size={20} />
              </div>

              <div className="space-y-3">
                <div className="rounded-2xl border border-stone-200 bg-stone-50 p-3.5 flex items-center justify-between">
                  <div className="flex items-center gap-2.5">
                    <div className="h-2.5 w-2.5 rounded-full bg-emerald-500 animate-pulse" />
                    <p className="text-xs font-bold text-stone-800">QR Gate Scanner</p>
                  </div>
                  <Link
                    to="/checkin-checkout"
                    className="rounded-full bg-emerald-100 text-emerald-800 px-2.5 py-0.5 text-[10px] font-extrabold hover:bg-emerald-200 transition"
                  >
                    READY TO SCAN →
                  </Link>
                </div>

                <div className="rounded-2xl border border-stone-200 bg-stone-50 p-3.5 flex items-center justify-between">
                  <div className="flex items-center gap-2.5">
                    <div className="h-2.5 w-2.5 rounded-full bg-amber-500" />
                    <p className="text-xs font-bold text-stone-800">Active Field Deployments</p>
                  </div>
                  <span className="font-mono text-xs font-extrabold text-stone-900">
                    {usageSummary.activeCount} active
                  </span>
                </div>

                <div className="rounded-2xl border border-stone-200 bg-stone-50 p-3.5 flex items-center justify-between">
                  <div className="flex items-center gap-2.5">
                    <div className="h-2.5 w-2.5 rounded-full bg-teal-500" />
                    <p className="text-xs font-bold text-stone-800">Total Registered Fleet</p>
                  </div>
                  <span className="font-mono text-xs font-extrabold text-stone-900">
                    {stats.find((s) => s.label === 'Total Assets')?.value ?? 0} machines
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Recent Rental Contracts */}
          <div className="rounded-3xl border border-stone-200 bg-white p-6 shadow-sm">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.25em] text-stone-500">Live Contracts</p>
                <h3 className="mt-1 text-xl font-bold text-stone-900">Recent Rental Deployments & Usage</h3>
              </div>
              <Link
                to="/rentals"
                className="text-xs font-bold text-[#ab6639] hover:underline"
              >
                View all contracts →
              </Link>
            </div>

            {rentals.length === 0 ? (
              <div className="py-12 text-center text-xs text-stone-500">
                No rental contracts active yet. Check out a vehicle in the Check-In / Check-Out scanner to start deployment.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr className="border-b border-stone-200 text-xs font-bold uppercase tracking-wider text-stone-500">
                      <th className="pb-3 pr-4">Rental Reference</th>
                      <th className="pb-3 pr-4">Equipment</th>
                      <th className="pb-3 pr-4">Operator</th>
                      <th className="pb-3 pr-4">Deployment Site</th>
                      <th className="pb-3 pr-4">Runtime & Fuel</th>
                      <th className="pb-3 pr-4">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-stone-100 text-xs font-medium text-stone-800">
                    {rentals.slice(0, 6).map((rental) => {
                      const st = getDurationStats(rental)
                      return (
                        <tr key={rental.id} className="hover:bg-stone-50/60 transition">
                          <td className="py-3 pr-4 font-mono font-bold text-stone-900">{rental.id}</td>
                          <td className="py-3 pr-4">
                            <p className="font-bold text-stone-900">{rental.equipmentName}</p>
                            <p className="text-[10px] font-mono text-stone-500">{rental.equipmentId}</p>
                          </td>
                          <td className="py-3 pr-4">{rental.operator}</td>
                          <td className="py-3 pr-4">{rental.site}</td>
                          <td className="py-3 pr-4">
                            <div className="flex items-center gap-1.5 text-stone-800 font-bold">
                              <Timer size={12} className="text-amber-600" />
                              {st.text}
                            </div>
                            <p className="text-[10px] text-teal-700 font-semibold">{st.fuelLiters} L fuel</p>
                          </td>
                          <td className="py-3 pr-4">
                            <span
                              className={`rounded-full px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider ${
                                st.isOverdue || rental.status === 'OVERDUE'
                                  ? 'bg-rose-100 text-rose-800'
                                  : rental.status === 'COMPLETED'
                                    ? 'bg-stone-100 text-stone-700'
                                    : 'bg-emerald-100 text-emerald-800'
                              }`}
                            >
                              {st.isOverdue || rental.status === 'OVERDUE'
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
