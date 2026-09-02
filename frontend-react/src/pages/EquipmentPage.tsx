import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  AlertCircle,
  Camera,
  CheckCircle2,
  Fuel,
  Gauge,
  Loader2,
  PlusCircle,
  Printer,
  QrCode,
  Search,
  Truck,
  X,
} from 'lucide-react'
import { QRCodeSVG } from 'qrcode.react'
import { Navbar } from '../components/Navbar'
import { Sidebar } from '../components/Sidebar'
import { useAuth } from '../context/AuthContext'
import { api } from '../services/api'
import type { Asset, SiteItem } from '../types'

const EQUIPMENT_TYPES = [
  { value: 'EXCAVATOR', label: 'Hydraulic Excavator' },
  { value: 'BULLDOZER', label: 'Track-Type Bulldozer' },
  { value: 'WHEEL_LOADER', label: 'Wheel Loader' },
  { value: 'DUMP_TRUCK', label: 'Articulated / Off-Highway Dump Truck' },
  { value: 'MOTOR_GRADER', label: 'Motor Grader' },
  { value: 'COMPACTOR', label: 'Vibratory Soil Compactor' },
  { value: 'CRANE', label: 'Telehandler / Rough Terrain Crane' },
  { value: 'GENERATOR', label: 'Diesel Generator Set' },
  { value: 'SKID_STEER', label: 'Skid Steer Loader' },
  { value: 'BACKHOE', label: 'Backhoe Loader' },
]

export function EquipmentPage() {
  const { user } = useAuth()
  const [search, setSearch] = useState('')
  const [assets, setAssets] = useState<Asset[]>([])
  const [sites, setSites] = useState<SiteItem[]>([])
  const [loading, setLoading] = useState(true)

  // QR Modal
  const [selectedAssetForQr, setSelectedAssetForQr] = useState<Asset | null>(null)

  // Registration Modal (for Managers and Admins)
  const [showRegisterModal, setShowRegisterModal] = useState(false)
  const [regVehicleId, setRegVehicleId] = useState('')
  const [regModel, setRegModel] = useState('')
  const [regType, setRegType] = useState('EXCAVATOR')
  const [regSiteId, setRegSiteId] = useState<number | ''>('')
  const [regSerial, setRegSerial] = useState('')
  const [registerLoading, setRegisterLoading] = useState(false)
  const [registerError, setRegisterError] = useState<string | null>(null)
  const [registerSuccess, setRegisterSuccess] = useState<string | null>(null)

  const isManagerOrAdmin = user?.role === 'ADMIN' || user?.role === 'MANAGER'

  const loadData = async () => {
    setLoading(true)
    try {
      const [liveAssets, liveSites] = await Promise.all([
        api.getAssets().catch(() => []),
        api.getSites().catch(() => []),
      ])
      setAssets(liveAssets)
      setSites(liveSites)
      if (liveSites.length > 0 && !regSiteId) {
        setRegSiteId(liveSites[0].id)
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const filteredAssets = useMemo(() => {
    const value = search.trim().toLowerCase()

    if (!value) return assets

    return assets.filter(
      (asset) =>
        asset.id.toLowerCase().includes(value) ||
        asset.name.toLowerCase().includes(value) ||
        asset.site.toLowerCase().includes(value) ||
        asset.type.toLowerCase().includes(value),
    )
  }, [search, assets])

  // Handle Register Vehicle Submission
  const handleRegisterVehicle = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!regVehicleId.trim()) {
      setRegisterError('Please enter a vehicle registration number / asset ID.')
      return
    }

    setRegisterLoading(true)
    setRegisterError(null)
    setRegisterSuccess(null)

    try {
      const newEq = await api.registerEquipment({
        equipment_id: regVehicleId.trim().toUpperCase(),
        model: regModel.trim() || `Cat ${regType}`,
        equipment_type: regType,
        site: regSiteId ? Number(regSiteId) : null,
        serial_number: regSerial.trim() || undefined,
      })

      setRegisterSuccess(`Vehicle ${newEq.equipment_id} registered successfully!`)

      // Construct adapted asset
      const createdAsset: Asset = {
        id: newEq.equipment_id,
        name: newEq.model || newEq.equipment_type,
        type: newEq.equipment_type,
        site: newEq.site_detail?.name || 'Assigned Site',
        status: 'AVAILABLE',
        operator: 'Unassigned',
        fuel: 100,
        speed: 0,
        engineHours: 0,
        latitude: 12.9716,
        longitude: 77.5946,
        lastUpdated: 'Just now',
        checkoutDate: '',
        checkinDate: '',
      }

      setAssets((prev) => [createdAsset, ...prev])
      setShowRegisterModal(false)

      // Open QR code modal immediately for the newly registered vehicle!
      setSelectedAssetForQr(createdAsset)

      // Reset form fields
      setRegVehicleId('')
      setRegModel('')
      setRegSerial('')
    } catch (err: unknown) {
      setRegisterError(err instanceof Error ? err.message : 'Failed to register vehicle.')
    } finally {
      setRegisterLoading(false)
    }
  }

  const handlePrintQr = () => {
    window.print()
  }

  return (
    <div className="flex min-h-screen bg-[#fcf9f7] text-stone-900">
      <Sidebar role={user?.role ?? 'VIEWER'} />

      <div className="flex-1 flex flex-col min-w-0">
        <Navbar />

        <main className="flex-1 p-4 md:p-8 max-w-7xl mx-auto w-full space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.25em] text-stone-500">Fleet Operations</p>
              <h1 className="mt-1 text-2xl md:text-3xl font-extrabold text-stone-900 tracking-tight">
                Vehicle Fleet & QR Directory
              </h1>
              <p className="text-xs md:text-sm text-stone-500 mt-1">
                Register vehicles and generate single permanent QR badges for field check-in / check-out.
              </p>
            </div>

            <div className="flex items-center gap-2.5">
              {isManagerOrAdmin && (
                <button
                  onClick={() => {
                    setRegisterError(null)
                    setRegisterSuccess(null)
                    setShowRegisterModal(true)
                  }}
                  className="inline-flex items-center justify-center gap-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 px-4 py-2.5 text-xs font-bold uppercase tracking-wider text-white transition shadow-sm cursor-pointer"
                >
                  <PlusCircle size={16} />
                  Register Vehicle
                </button>
              )}

              <Link
                to="/checkin-checkout"
                className="inline-flex items-center justify-center gap-2 rounded-xl bg-[#ab6639] hover:bg-[#8e512d] px-4 py-2.5 text-xs font-bold uppercase tracking-wider text-white transition shadow-sm cursor-pointer"
              >
                <Camera size={16} />
                Open QR Scanner
              </Link>
            </div>
          </div>

          {/* Success Banner */}
          {registerSuccess && (
            <div className="flex items-center gap-2.5 rounded-2xl border border-emerald-200 bg-emerald-50 p-4 text-xs font-semibold text-emerald-900 shadow-xs">
              <CheckCircle2 size={18} className="text-emerald-600 shrink-0" />
              <span>{registerSuccess}</span>
            </div>
          )}

          {/* Search bar & Filter */}
          <div className="flex items-center gap-3 rounded-2xl border border-stone-200 bg-white px-4 py-3 shadow-xs">
            <Search size={18} className="text-stone-400 shrink-0" />
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search by Registration Number (e.g. CAT-336-1001), Model, Site, or Category..."
              className="w-full bg-transparent text-sm outline-none placeholder:text-stone-400"
            />
          </div>

          {/* Loading or Empty State */}
          {loading ? (
            <div className="py-20 text-center text-sm font-semibold text-stone-500">
              Loading registered fleet...
            </div>
          ) : filteredAssets.length === 0 ? (
            <div className="rounded-3xl border border-dashed border-stone-300 bg-white p-12 text-center">
              <div className="mx-auto h-16 w-16 rounded-2xl bg-amber-50 text-[#ab6639] flex items-center justify-center mb-4">
                <Truck size={32} />
              </div>
              <h3 className="text-lg font-bold text-stone-800">No Vehicles in Directory</h3>
              <p className="text-xs text-stone-500 mt-1.5 max-w-md mx-auto">
                {search
                  ? 'No vehicles matched your search query.'
                  : isManagerOrAdmin
                    ? 'Register your first fleet vehicle using its registration number to automatically generate its QR badge.'
                    : 'No vehicles have been registered yet by fleet managers.'}
              </p>
              {isManagerOrAdmin && (
                <button
                  onClick={() => setShowRegisterModal(true)}
                  className="mt-5 inline-flex items-center gap-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 px-5 py-2.5 text-xs font-bold uppercase tracking-wider text-white transition shadow-sm cursor-pointer"
                >
                  <PlusCircle size={15} />
                  Register First Vehicle
                </button>
              )}
            </div>
          ) : (
            /* Equipment Grid */
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {filteredAssets.map((asset) => (
                <div
                  key={asset.id}
                  className="group relative flex flex-col justify-between rounded-3xl border border-stone-200 bg-white p-5 shadow-sm hover:border-amber-400/60 hover:shadow-md transition duration-200"
                >
                  <div>
                    {/* Top Bar */}
                    <div className="flex items-center justify-between gap-2 pb-3 border-b border-stone-100">
                      <span className="font-mono text-xs font-extrabold text-stone-800 bg-stone-100 px-2.5 py-1 rounded-lg">
                        {asset.id}
                      </span>
                      <span
                        className={`rounded-full px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider ${
                          asset.status === 'AVAILABLE'
                            ? 'bg-emerald-100 text-emerald-800'
                            : asset.status === 'IN_USE' || asset.status === 'RENTED'
                              ? 'bg-amber-100 text-amber-800'
                              : asset.status === 'OVERDUE'
                                ? 'bg-rose-100 text-rose-800'
                                : 'bg-stone-200 text-stone-700'
                        }`}
                      >
                        {asset.status}
                      </span>
                    </div>

                    {/* Asset Info */}
                    <div className="mt-3.5">
                      <h3 className="font-bold text-stone-900 text-lg leading-tight group-hover:text-amber-800 transition">
                        {asset.name}
                      </h3>
                      <p className="text-xs text-stone-500 mt-1 flex items-center gap-1.5">
                        <Truck size={14} className="text-stone-400" />
                        {asset.type} · {asset.site}
                      </p>
                    </div>

                    {/* Telematics stats */}
                    <div className="mt-4 grid grid-cols-2 gap-2 rounded-2xl bg-stone-50 p-3 text-xs">
                      <div className="flex items-center gap-2">
                        <Fuel size={14} className="text-amber-600" />
                        <div>
                          <p className="text-[10px] uppercase font-semibold text-stone-400">Fuel Level</p>
                          <p className="font-bold text-stone-800">{asset.fuel}%</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Gauge size={14} className="text-teal-600" />
                        <div>
                          <p className="text-[10px] uppercase font-semibold text-stone-400">Engine Hours</p>
                          <p className="font-bold text-stone-800">{asset.engineHours} hrs</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Card Actions */}
                  <div className="mt-5 pt-3 border-t border-stone-100 flex items-center justify-between gap-2">
                    <button
                      onClick={() => setSelectedAssetForQr(asset)}
                      className="inline-flex items-center gap-1.5 rounded-xl border border-stone-200 bg-stone-50 px-3 py-1.5 text-xs font-bold text-stone-700 hover:bg-amber-50 hover:text-amber-900 hover:border-amber-300 transition cursor-pointer"
                    >
                      <QrCode size={14} />
                      View Vehicle QR
                    </button>

                    <Link
                      to="/checkin-checkout"
                      className="inline-flex items-center gap-1 text-xs font-bold text-[#ab6639] hover:underline"
                    >
                      Check In / Out →
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* MODAL 1: REGISTER VEHICLE MODAL (For Managers / Admins) */}
          {showRegisterModal && (
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-stone-900/60 backdrop-blur-xs animate-in fade-in duration-150">
              <div className="relative w-full max-w-lg rounded-3xl bg-white p-6 sm:p-8 shadow-2xl border border-stone-200">
                <button
                  onClick={() => setShowRegisterModal(false)}
                  className="absolute right-4 top-4 rounded-full p-2 text-stone-400 hover:bg-stone-100 hover:text-stone-700 transition cursor-pointer"
                >
                  <X size={18} />
                </button>

                <div className="flex items-center gap-2 mb-1">
                  <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-100 px-3 py-1 text-xs font-bold uppercase tracking-wider text-emerald-900">
                    <PlusCircle size={13} className="text-emerald-700" />
                    Manager Fleet Registration
                  </span>
                </div>

                <h3 className="text-xl font-extrabold text-stone-900 mt-1">Register New Vehicle</h3>
                <p className="text-xs text-stone-500 mt-0.5">
                  The vehicle registration number will be permanently encoded into its unique QR code badge.
                </p>

                {registerError && (
                  <div className="mt-4 flex items-center gap-2 rounded-xl bg-rose-50 border border-rose-200 p-3 text-xs text-rose-800 font-semibold">
                    <AlertCircle size={16} className="text-rose-600 shrink-0" />
                    <span>{registerError}</span>
                  </div>
                )}

                <form onSubmit={handleRegisterVehicle} className="mt-5 space-y-4">
                  <div>
                    <label className="block text-xs font-bold uppercase tracking-wider text-stone-700 mb-1">
                      Vehicle / Registration Number *
                    </label>
                    <input
                      required
                      value={regVehicleId}
                      onChange={(e) => setRegVehicleId(e.target.value)}
                      placeholder="e.g. CAT-336-1001 or KA-01-EQ-9988"
                      className="w-full rounded-xl border border-stone-300 bg-stone-50 px-3.5 py-2.5 text-sm font-mono font-bold text-stone-900 outline-none focus:border-amber-500 focus:bg-white"
                    />
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-bold uppercase tracking-wider text-stone-700 mb-1">
                        Equipment Category
                      </label>
                      <select
                        value={regType}
                        onChange={(e) => setRegType(e.target.value)}
                        className="w-full rounded-xl border border-stone-300 bg-stone-50 px-3 py-2.5 text-sm font-semibold text-stone-800 outline-none focus:border-amber-500 focus:bg-white"
                      >
                        {EQUIPMENT_TYPES.map((t) => (
                          <option key={t.value} value={t.value}>
                            {t.label}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-xs font-bold uppercase tracking-wider text-stone-700 mb-1">
                        Designated Site / Area
                      </label>
                      <select
                        value={regSiteId}
                        onChange={(e) => setRegSiteId(e.target.value ? Number(e.target.value) : '')}
                        className="w-full rounded-xl border border-stone-300 bg-stone-50 px-3 py-2.5 text-sm font-semibold text-stone-800 outline-none focus:border-amber-500 focus:bg-white"
                      >
                        {sites.map((s) => (
                          <option key={s.id} value={s.id}>
                            {s.name}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-bold uppercase tracking-wider text-stone-700 mb-1">
                      Full Model Name (Optional)
                    </label>
                    <input
                      value={regModel}
                      onChange={(e) => setRegModel(e.target.value)}
                      placeholder="e.g. Cat 336 Heavy Hydraulic Excavator"
                      className="w-full rounded-xl border border-stone-300 bg-stone-50 px-3.5 py-2.5 text-sm font-medium text-stone-900 outline-none focus:border-amber-500 focus:bg-white"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold uppercase tracking-wider text-stone-700 mb-1">
                      Chassis PIN / Serial Number (Optional)
                    </label>
                    <input
                      value={regSerial}
                      onChange={(e) => setRegSerial(e.target.value)}
                      placeholder="e.g. PIN-CAT-336-US-883"
                      className="w-full rounded-xl border border-stone-300 bg-stone-50 px-3.5 py-2.5 text-sm font-mono text-stone-900 outline-none focus:border-amber-500 focus:bg-white"
                    />
                  </div>

                  <div className="pt-3 flex items-center justify-end gap-3">
                    <button
                      type="button"
                      onClick={() => setShowRegisterModal(false)}
                      className="rounded-xl border border-stone-300 px-4 py-2.5 text-xs font-bold uppercase tracking-wider text-stone-600 hover:bg-stone-50 transition cursor-pointer"
                    >
                      Cancel
                    </button>

                    <button
                      type="submit"
                      disabled={registerLoading}
                      className="inline-flex items-center gap-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 px-5 py-2.5 text-xs font-bold uppercase tracking-wider text-white transition shadow-md disabled:opacity-50 cursor-pointer"
                    >
                      {registerLoading ? (
                        <>
                          <Loader2 size={16} className="animate-spin" />
                          Registering...
                        </>
                      ) : (
                        <>
                          <CheckCircle2 size={16} />
                          Register & Generate QR
                        </>
                      )}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}

          {/* MODAL 2: QR CODE BADGE MODAL FOR ANY VEHICLE */}
          {selectedAssetForQr && (
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-stone-900/60 backdrop-blur-xs animate-in fade-in duration-150">
              <div className="relative w-full max-w-md rounded-3xl bg-white p-6 sm:p-8 shadow-2xl border border-stone-200 text-center">
                <button
                  onClick={() => setSelectedAssetForQr(null)}
                  className="absolute right-4 top-4 rounded-full p-2 text-stone-400 hover:bg-stone-100 hover:text-stone-700 transition cursor-pointer"
                >
                  <X size={18} />
                </button>

                <div className="inline-flex items-center gap-1.5 rounded-full bg-amber-100 px-3 py-1 text-xs font-bold uppercase tracking-wider text-amber-900 mb-3">
                  Vehicle Identification Badge
                </div>

                <h3 className="text-xl font-extrabold text-stone-900">{selectedAssetForQr.name}</h3>
                <p className="text-xs font-mono font-bold text-stone-600 mt-0.5">
                  Registration Number: {selectedAssetForQr.id}
                </p>

                {/* QR Display with exact Registration ID */}
                <div className="my-6 inline-flex flex-col items-center justify-center rounded-2xl border-2 border-dashed border-amber-400 bg-amber-50/50 p-6 shadow-xs">
                  <div className="bg-white p-3.5 rounded-xl shadow-xs border border-stone-200">
                    <QRCodeSVG
                      value={selectedAssetForQr.id}
                      size={200}
                      level="H"
                      includeMargin={false}
                    />
                  </div>
                  <p className="text-xs font-mono font-extrabold text-stone-900 mt-3 tracking-wider">
                    {selectedAssetForQr.id}
                  </p>
                  <p className="text-[10px] text-stone-500 mt-0.5">
                    Scan with mobile camera to Check In or Check Out
                  </p>
                </div>

                {/* Modal Buttons */}
                <div className="flex items-center justify-center gap-3">
                  <button
                    onClick={handlePrintQr}
                    className="inline-flex items-center gap-2 rounded-xl border border-stone-300 bg-white px-4 py-2 text-xs font-bold text-stone-700 hover:bg-stone-50 transition shadow-xs cursor-pointer"
                  >
                    <Printer size={14} />
                    Print Badge
                  </button>

                  <Link
                    to="/checkin-checkout"
                    onClick={() => setSelectedAssetForQr(null)}
                    className="inline-flex items-center gap-2 rounded-xl bg-[#ab6639] hover:bg-[#8e512d] px-4 py-2 text-xs font-bold text-white transition shadow-xs cursor-pointer"
                  >
                    <Camera size={14} />
                    Test In Scanner
                  </Link>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}
