import { useEffect, useState } from 'react'
import {
  Brain,
  RefreshCw,
  Sparkles,
  TrendingUp,
  Zap,
} from 'lucide-react'
import { Navbar } from '../components/Navbar'
import { Sidebar } from '../components/Sidebar'
import { useAuth } from '../context/AuthContext'
import { api } from '../services/api'
import type { AnomalyItem, ForecastItem, RecommendationItem } from '../types'

export function AnalyticsPage() {
  const { user } = useAuth()
  const [forecasts, setForecasts] = useState<ForecastItem[]>([])
  const [anomalies, setAnomalies] = useState<AnomalyItem[]>([])
  const [recommendations, setRecommendations] = useState<RecommendationItem[]>([])

  const loadData = async () => {
    try {
      const [fcList, anList, recList] = await Promise.all([
        api.getForecasts().catch(() => [] as ForecastItem[]),
        api.getAnomalies().catch(() => [] as AnomalyItem[]),
        api.getRecommendations().catch(() => [] as RecommendationItem[]),
      ])
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

  const handleGenerateForecasts = async () => {
    const res = await api.generateForecasts()
    setForecasts(res)
  }

  const handleScanAnomalies = async () => {
    const res = await api.scanAnomalies()
    setAnomalies(res)
  }

  const handleGenerateRecommendations = async () => {
    const res = await api.generateRecommendations()
    setRecommendations(res)
  }

  const openAnomalies = anomalies.filter((a) => a.status === 'OPEN')
  const pendingRecommendations = recommendations.filter((r) => r.status === 'PENDING')

  return (
    <div className="flex min-h-screen bg-[#fff8f6] text-stone-900">
      <Sidebar role={user?.role ?? 'VIEWER'} />

      <div className="flex-1 flex flex-col min-w-0">
        <Navbar />

        <main className="flex-1 p-4 md:p-8 max-w-7xl mx-auto w-full space-y-6">
          <div className="mb-6">
            <span className="inline-flex items-center gap-1.5 rounded-full bg-purple-100 px-3 py-1 text-xs font-bold uppercase tracking-wider text-purple-900">
              <Sparkles size={13} className="text-purple-600" />
              Machine Learning Analytics & Risk Engine
            </span>
            <h2 className="mt-2 text-3xl font-extrabold text-stone-900 tracking-tight">
              Utilization, ML Forecasting & Anomaly Intelligence
            </h2>
            <p className="text-xs md:text-sm text-stone-500 mt-1">
              Real-time telemetry anomaly detection, hybrid demand forecasting, and automated machine reallocation.
            </p>
          </div>

          <div className="grid gap-6 md:grid-cols-3">
            <div className="rounded-3xl border border-stone-200 bg-white p-5 shadow-sm">
              <div className="flex items-center justify-between">
                <p className="text-xs uppercase tracking-[0.25em] text-stone-500 font-bold">Hybrid Demand Forecasts</p>
                <TrendingUp size={18} className="text-purple-600" />
              </div>
              <p className="mt-4 text-4xl font-extrabold text-purple-950">{forecasts.length}</p>
              <p className="mt-2 text-xs text-stone-600">Model v2.1 predictions active across job sites.</p>
              <button
                onClick={handleGenerateForecasts}
                className="mt-4 inline-flex items-center gap-1.5 rounded-xl bg-purple-100 hover:bg-purple-200 text-purple-900 px-3 py-1.5 text-xs font-bold transition cursor-pointer"
              >
                <RefreshCw size={12} /> Regenerate Forecasts
              </button>
            </div>

            <div className="rounded-3xl border border-stone-200 bg-white p-5 shadow-sm">
              <div className="flex items-center justify-between">
                <p className="text-xs uppercase tracking-[0.25em] text-stone-500 font-bold">Rules + Isolation Forest</p>
                <Zap size={18} className="text-rose-600" />
              </div>
              <p className="mt-4 text-4xl font-extrabold text-rose-950">{openAnomalies.length}</p>
              <p className="mt-2 text-xs text-stone-600">Open telemetry anomalies flagged for review.</p>
              <button
                onClick={handleScanAnomalies}
                className="mt-4 inline-flex items-center gap-1.5 rounded-xl bg-rose-100 hover:bg-rose-200 text-rose-900 px-3 py-1.5 text-xs font-bold transition cursor-pointer"
              >
                <Zap size={12} /> Scan Telemetry
              </button>
            </div>

            <div className="rounded-3xl border border-stone-200 bg-white p-5 shadow-sm">
              <div className="flex items-center justify-between">
                <p className="text-xs uppercase tracking-[0.25em] text-stone-500 font-bold">Smart Recommendations</p>
                <Brain size={18} className="text-indigo-600" />
              </div>
              <p className="mt-4 text-4xl font-extrabold text-indigo-950">{pendingRecommendations.length}</p>
              <p className="mt-2 text-xs text-stone-600">Suggested machine reallocations to meet demand.</p>
              <button
                onClick={handleGenerateRecommendations}
                className="mt-4 inline-flex items-center gap-1.5 rounded-xl bg-indigo-100 hover:bg-indigo-200 text-indigo-900 px-3 py-1.5 text-xs font-bold transition cursor-pointer"
              >
                <Brain size={12} /> Evaluate Reallocations
              </button>
            </div>
          </div>

          {/* Detailed Lists */}
          <div className="grid gap-6 lg:grid-cols-2">
            {/* Forecasts List */}
            <div className="rounded-3xl border border-stone-200 bg-white p-6 shadow-sm">
              <h3 className="text-lg font-bold text-stone-900 mb-3">Recent Hybrid Demand Forecasts</h3>
              <div className="space-y-2.5 max-h-80 overflow-y-auto">
                {forecasts.slice(0, 10).map((fc) => (
                  <div key={fc.id} className="rounded-2xl border border-purple-100 bg-purple-50/50 p-3 flex items-center justify-between text-xs">
                    <div>
                      <p className="font-extrabold text-stone-900">{fc.equipment_type}</p>
                      <p className="text-[11px] text-stone-500">Date: {fc.forecast_date} · Model {fc.model_version}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-extrabold text-purple-900">{fc.predicted_demand} units</p>
                      <p className="text-[10px] text-emerald-700 font-bold">{Math.round(fc.confidence * 100)}% confidence</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Anomaly Alerts List */}
            <div className="rounded-3xl border border-stone-200 bg-white p-6 shadow-sm">
              <h3 className="text-lg font-bold text-stone-900 mb-3">Detected Telemetry Anomalies</h3>
              <div className="space-y-2.5 max-h-80 overflow-y-auto">
                {anomalies.slice(0, 10).map((an) => (
                  <div key={an.id} className="rounded-2xl border border-rose-100 bg-rose-50/50 p-3 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-stone-900">{an.anomaly_type}</span>
                      <span className="text-[10px] font-extrabold bg-rose-200 text-rose-900 px-1.5 py-0.5 rounded">{an.severity} ({an.score.toFixed(2)})</span>
                    </div>
                    <p className="text-[11px] text-stone-600 mt-1">{an.reason}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
