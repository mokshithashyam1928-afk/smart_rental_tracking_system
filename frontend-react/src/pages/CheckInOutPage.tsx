import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  AlertCircle,
  ArrowDownLeft,
  ArrowUpRight,
  Camera,
  CheckCircle2,
  FlipHorizontal,
  History,
  Loader2,
  MapPin,
  PlusCircle,
  QrCode,
  Sparkles,
  Truck,
  Upload,
  User,
  Zap,
} from 'lucide-react'
import { Html5Qrcode, Html5QrcodeSupportedFormats, type Html5QrcodeCameraScanConfig } from 'html5-qrcode'
import { Navbar } from '../components/Navbar'
import { Sidebar } from '../components/Sidebar'
import { useAuth } from '../context/AuthContext'
import { api } from '../services/api'
import type { OperatorItem, Rental, ResolvedEquipment, SiteItem } from '../types'

interface TransactionRecord {
  id: string
  type: 'CHECK_OUT' | 'CHECK_IN'
  equipmentId: string
  equipmentName: string
  operatorName: string
  siteName: string
  timestamp: string
}

export function CheckInOutPage() {
  const { user } = useAuth()

  // Camera & Scanner States
  const [scannerActive, setScannerActive] = useState(false)
  const [facingMode, setFacingMode] = useState<'environment' | 'user'>('environment')
  const [cameraError, setCameraError] = useState<string | null>(null)
  const [lastScannedCode, setLastScannedCode] = useState<string>('')
  const [isProcessingScan, setIsProcessingScan] = useState(false)
  
  // Synchronous atomic lock ref to completely eliminate duplicate frames
  const isLockedRef = useRef<boolean>(false)
  const html5QrCodeRef = useRef<Html5Qrcode | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Current Active Vehicle info & Action status
  const [resolvedEquipment, setResolvedEquipment] = useState<ResolvedEquipment | null>(null)
  const [lastActionType, setLastActionType] = useState<'CHECK_OUT' | 'CHECK_IN' | null>(null)
  const [actionSuccess, setActionSuccess] = useState<string | null>(null)
  const [actionError, setActionError] = useState<string | null>(null)

  // Dispatch preset settings (used when automatically checking out available machines)
  const [operators, setOperators] = useState<OperatorItem[]>([])
  const [sites, setSites] = useState<SiteItem[]>([])
  const [defaultOperatorId, setDefaultOperatorId] = useState<number | ''>('')
  const [defaultSiteId, setDefaultSiteId] = useState<number | ''>('')
  const [defaultDurationHours, setDefaultDurationHours] = useState<number>(24)

  // Live Gate Transactions & Fleet List
  const [recentTransactions, setRecentTransactions] = useState<TransactionRecord[]>([])
  const [fleetList, setFleetList] = useState<ResolvedEquipment[]>([])

  // Refresh auxiliary data
  const refreshData = async () => {
    try {
      const [ops, stes, fleet, rentals] = await Promise.all([
        api.getOperators().catch(() => []),
        api.getSites().catch(() => []),
        api.getRawEquipment().catch(() => []),
        api.getRentals().catch(() => []),
      ])
      setOperators(ops)
      setSites(stes)
      setFleetList(fleet)
      if (ops.length > 0 && !defaultOperatorId) setDefaultOperatorId(ops[0].id)
      if (stes.length > 0 && !defaultSiteId) setDefaultSiteId(stes[0].id)

      if (rentals && rentals.length > 0) {
        const txList: TransactionRecord[] = rentals.map((r: Rental) => ({
          id: r.id,
          type: r.status === 'COMPLETED' ? 'CHECK_IN' : 'CHECK_OUT',
          equipmentId: r.equipmentId,
          equipmentName: r.equipmentName,
          operatorName: r.operator || 'Assigned Operator',
          siteName: r.site || 'Site',
          timestamp: r.startDate || new Date().toLocaleDateString(),
        }))
        setRecentTransactions(txList)
      } else {
        setRecentTransactions([])
      }
    } catch (err) {
      console.error('Failed to load initial data:', err)
    }
  }

  useEffect(() => {
    refreshData()
  }, [])

  // Start Scanner
  const startScanner = async () => {
    setCameraError(null)
    isLockedRef.current = false
    setScannerActive(true)

    try {
      if (html5QrCodeRef.current) {
        try {
          await html5QrCodeRef.current.stop()
        } catch {
          // ignore
        }
      }

      const qrScanner = new Html5Qrcode('qr-reader-viewport', {
        formatsToSupport: [Html5QrcodeSupportedFormats.QR_CODE, Html5QrcodeSupportedFormats.CODE_128],
        verbose: false,
      })
      html5QrCodeRef.current = qrScanner

      const config: Html5QrcodeCameraScanConfig = {
        fps: 10,
        qrbox: { width: 250, height: 250 },
        aspectRatio: 1.0,
      }

      await qrScanner.start(
        { facingMode: facingMode },
        config,
        (decodedText) => {
          // Synchronous atomic lock: process exactly ONE frame
          if (isLockedRef.current) return
          isLockedRef.current = true

          // Stop camera immediately to prevent any subsequent frames
          qrScanner.stop().catch(() => {})
          setScannerActive(false)

          handleSingleScanAction(decodedText)
        },
        () => {
          // scanning frame seeking QR
        }
      )
    } catch (err: unknown) {
      console.error('Camera start error:', err)
      setCameraError(
        err instanceof Error
          ? err.message
          : 'Unable to access mobile camera. Please check camera permissions or upload an image.'
      )
      setScannerActive(false)
      isLockedRef.current = false
    }
  }

  // Stop Scanner
  const stopScanner = async () => {
    if (html5QrCodeRef.current) {
      try {
        await html5QrCodeRef.current.stop()
        html5QrCodeRef.current.clear()
      } catch {
        // ignore
      }
      html5QrCodeRef.current = null
    }
    setScannerActive(false)
    isLockedRef.current = false
  }

  useEffect(() => {
    return () => {
      if (html5QrCodeRef.current) {
        html5QrCodeRef.current.stop().catch(() => {})
      }
    }
  }, [])

  // Switch rear/front camera
  const toggleCameraFacing = async () => {
    const nextMode = facingMode === 'environment' ? 'user' : 'environment'
    setFacingMode(nextMode)
    if (scannerActive) {
      await stopScanner()
      setTimeout(() => {
        setFacingMode(nextMode)
        startScanner()
      }, 300)
    }
  }

  // Authoritative Single-Scan Action:
  // Step 1: Query backend for latest live state of the vehicle
  // Step 2: If checked in (AVAILABLE) -> CHECK OUT
  //         If checked out (RENTED/ACTIVE) -> CHECK IN
  const handleSingleScanAction = async (code: string) => {
    const cleanCode = code.trim()
    if (!cleanCode) {
      isLockedRef.current = false
      return
    }

    setLastScannedCode(cleanCode)
    setIsProcessingScan(true)
    setActionError(null)
    setActionSuccess(null)

    try {
      const result = await api.scanQrGate({
        qr_code: cleanCode,
        operator_id: defaultOperatorId,
        site_id: defaultSiteId,
        due_hours: defaultDurationHours,
      })

      const eq = result.equipment
      const rental = (result.rental as Record<string, unknown>) || {}
      const opDetail = (rental.operator_detail as Record<string, unknown>) || (eq.operator_detail as Record<string, unknown>) || {}
      const siteDetail = (rental.site_detail as Record<string, unknown>) || (eq.site_detail as Record<string, unknown>) || {}

      const opName = (opDetail.name as string) || 'Assigned Operator'
      const siteName = (siteDetail.name as string) || (eq.site_detail?.name as string) || 'Site'

      const newRecord: TransactionRecord = {
        id: `TX-${Date.now().toString().slice(-6)}`,
        type: result.action,
        equipmentId: eq.equipment_id,
        equipmentName: eq.model || eq.equipment_type,
        operatorName: opName,
        siteName: siteName,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }

      setRecentTransactions((prev) => [newRecord, ...prev])
      setLastActionType(result.action)

      if (result.action === 'CHECK_OUT') {
        setActionSuccess(`Checked Out: ${eq.equipment_id} dispatched to ${siteName}!`)
      } else {
        setActionSuccess(`Checked In: ${eq.equipment_id} returned to yard and marked AVAILABLE!`)
      }

      setResolvedEquipment(eq)
      await refreshData()
    } catch (err: unknown) {
      console.error('Scan action error:', err)
      setActionError(
        err instanceof Error
          ? err.message
          : `Vehicle "${cleanCode}" could not be processed.`
      )
    } finally {
      setIsProcessingScan(false)
      isLockedRef.current = false
    }
  }

  // File Upload scan fallback
  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    setIsProcessingScan(true)
    setActionError(null)

    try {
      const html5QrCode = new Html5Qrcode('qr-reader-viewport')
      const decodedText = await html5QrCode.scanFile(file, true)
      handleSingleScanAction(decodedText)
    } catch {
      setActionError('Could not decode QR code from uploaded image. Please try a clearer picture.')
      setIsProcessingScan(false)
      isLockedRef.current = false
    }
  }

  return (
    <div className="flex min-h-screen bg-[#fcf9f7] text-stone-900">
      <Sidebar role={user?.role ?? 'VIEWER'} />

      <div className="flex-1 flex flex-col min-w-0">
        <Navbar />

        <main className="flex-1 p-4 md:p-8 max-w-7xl mx-auto w-full space-y-8">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2">
                <span className="inline-flex items-center gap-1.5 rounded-full bg-amber-100 px-3 py-1 text-xs font-bold uppercase tracking-wider text-amber-900">
                  <Sparkles size={13} className="text-amber-600" />
                  Instant QR Fleet Gate
                </span>
              </div>
              <h1 className="mt-2 text-2xl md:text-3xl font-extrabold text-stone-900 tracking-tight">
                Check-In & Check-Out Gate
              </h1>
              <p className="mt-1 text-sm text-stone-500">
                Single scan auto-toggle: Scan an available machine to Check Out; scan a deployed machine to Check In.
              </p>
            </div>

            <div className="flex items-center gap-2.5">
              <input
                type="file"
                ref={fileInputRef}
                accept="image/*"
                className="hidden"
                onChange={handleFileUpload}
              />
              <button
                onClick={() => fileInputRef.current?.click()}
                className="inline-flex items-center gap-2 rounded-xl border border-stone-300 bg-white px-3.5 py-2.5 text-xs font-semibold uppercase tracking-wider text-stone-700 hover:bg-stone-50 transition shadow-xs cursor-pointer"
              >
                <Upload size={15} />
                Upload QR Image
              </button>
            </div>
          </div>

          {/* Quick Dispatch Preset Controls */}
          <div className="rounded-2xl border border-stone-200 bg-white p-4 shadow-xs">
            <p className="text-xs font-bold uppercase tracking-wider text-stone-500 mb-2">
              Dispatch Preset (Applied when checking out available machines):
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
              <div className="flex items-center gap-2 rounded-xl bg-stone-50 p-2.5 border border-stone-200">
                <User size={15} className="text-stone-400 shrink-0" />
                <div className="w-full">
                  <p className="text-[10px] uppercase font-bold text-stone-400">Assigned Operator</p>
                  <select
                    value={defaultOperatorId}
                    onChange={(e) => setDefaultOperatorId(Number(e.target.value))}
                    className="w-full bg-transparent font-semibold text-stone-800 outline-none cursor-pointer"
                  >
                    {operators.map((op) => (
                      <option key={op.id} value={op.id}>
                        {op.name} ({op.employee_id})
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="flex items-center gap-2 rounded-xl bg-stone-50 p-2.5 border border-stone-200">
                <MapPin size={15} className="text-[#ab6639] shrink-0" />
                <div className="w-full">
                  <p className="text-[10px] uppercase font-bold text-stone-400">Destination Site</p>
                  <select
                    value={defaultSiteId}
                    onChange={(e) => setDefaultSiteId(Number(e.target.value))}
                    className="w-full bg-transparent font-semibold text-stone-800 outline-none cursor-pointer"
                  >
                    {sites.map((site) => (
                      <option key={site.id} value={site.id}>
                        {site.name} ({site.site_code})
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="flex items-center gap-2 rounded-xl bg-stone-50 p-2.5 border border-stone-200">
                <ArrowUpRight size={15} className="text-teal-600 shrink-0" />
                <div className="w-full">
                  <p className="text-[10px] uppercase font-bold text-stone-400">Rental Duration</p>
                  <select
                    value={defaultDurationHours}
                    onChange={(e) => setDefaultDurationHours(Number(e.target.value))}
                    className="w-full bg-transparent font-semibold text-stone-800 outline-none cursor-pointer"
                  >
                    <option value={24}>24 Hours (1 Day)</option>
                    <option value={72}>72 Hours (3 Days)</option>
                    <option value={168}>168 Hours (7 Days)</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          {/* Main Scanner Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            {/* Left Column: Live Mobile Scanner */}
            <div className="lg:col-span-6 space-y-6">
              <div className="rounded-3xl border border-stone-200 bg-white p-5 md:p-6 shadow-sm">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2.5">
                    <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-amber-500 text-white font-bold">
                      <Camera size={18} />
                    </div>
                    <div>
                      <h3 className="font-bold text-stone-900 text-base">Mobile QR Gate Scanner</h3>
                      <p className="text-xs text-stone-500">Scan QR to toggle Check-In / Check-Out</p>
                    </div>
                  </div>

                  {scannerActive && (
                    <button
                      onClick={toggleCameraFacing}
                      className="p-2 rounded-xl border border-stone-200 text-stone-600 hover:bg-stone-100 transition cursor-pointer"
                      title="Switch camera"
                    >
                      <FlipHorizontal size={17} />
                    </button>
                  )}
                </div>

                {/* Scanner Viewport */}
                <div className="relative overflow-hidden rounded-2xl bg-stone-900 aspect-square flex flex-col items-center justify-center border-2 border-stone-800">
                  <div id="qr-reader-viewport" className="w-full h-full" />

                  {!scannerActive && (
                    <div className="absolute inset-0 flex flex-col items-center justify-center p-6 text-center bg-stone-900/90 backdrop-blur-xs text-white">
                      <div className="h-16 w-16 rounded-2xl bg-amber-500/20 text-amber-400 flex items-center justify-center mb-3 border border-amber-500/30">
                        <QrCode size={32} />
                      </div>
                      <p className="font-bold text-base">Instant Scanner</p>
                      <p className="text-xs text-stone-400 mt-1 max-w-xs">
                        Point camera at a vehicle QR code to instantly check in or check out.
                      </p>
                      <button
                        onClick={startScanner}
                        className="mt-4 inline-flex items-center gap-2 rounded-xl bg-amber-500 px-5 py-2.5 text-xs font-bold uppercase tracking-wider text-white hover:bg-amber-600 transition shadow-lg shadow-amber-500/20 cursor-pointer"
                      >
                        <Zap size={15} />
                        {resolvedEquipment ? 'Scan Next Vehicle' : 'Start Camera Scanner'}
                      </button>
                    </div>
                  )}

                  {scannerActive && (
                    <div className="absolute bottom-3 left-3 right-3 flex justify-between items-center z-20">
                      <span className="inline-flex items-center gap-1.5 rounded-full bg-black/60 px-3 py-1 text-[11px] font-medium text-emerald-400 backdrop-blur-md">
                        <span className="h-2 w-2 rounded-full bg-emerald-400 animate-ping" />
                        Scanning live...
                      </span>
                      <button
                        onClick={stopScanner}
                        className="rounded-lg bg-rose-600 px-3 py-1 text-xs font-bold text-white hover:bg-rose-700 transition shadow cursor-pointer"
                      >
                        Stop
                      </button>
                    </div>
                  )}
                </div>

                {cameraError && (
                  <div className="mt-4 flex items-start gap-2.5 rounded-2xl border border-rose-200 bg-rose-50 p-3.5 text-xs text-rose-800">
                    <AlertCircle size={16} className="text-rose-600 shrink-0 mt-0.5" />
                    <div>
                      <p className="font-semibold">Camera Notice</p>
                      <p className="text-rose-700 mt-0.5">{cameraError}</p>
                    </div>
                  </div>
                )}

                {/* Instant Test Buttons */}
                <div className="mt-6 pt-5 border-t border-stone-100">
                  <div className="flex items-center justify-between mb-2.5">
                    <p className="text-xs font-bold uppercase tracking-wider text-stone-500">
                      Or tap a vehicle to simulate scan:
                    </p>
                    <Link
                      to="/equipment"
                      className="text-xs font-bold text-[#ab6639] hover:underline inline-flex items-center gap-1"
                    >
                      <PlusCircle size={13} />
                      Register Vehicle
                    </Link>
                  </div>

                  {fleetList.length === 0 ? (
                    <div className="rounded-xl border border-dashed border-stone-300 p-4 text-center">
                      <p className="text-xs text-stone-500">No vehicles registered yet.</p>
                      <Link
                        to="/equipment"
                        className="mt-1.5 inline-block text-xs font-bold text-[#ab6639] hover:underline"
                      >
                        Go to Equipment page to register a vehicle →
                      </Link>
                    </div>
                  ) : (
                    <div className="flex flex-wrap gap-2">
                      {fleetList.map((eq) => (
                        <button
                          key={eq.id}
                          onClick={() => handleSingleScanAction(eq.equipment_id)}
                          className={`rounded-xl border px-3 py-1.5 text-xs font-semibold transition cursor-pointer ${
                            lastScannedCode === eq.equipment_id
                              ? 'border-amber-500 bg-amber-50 text-amber-900 ring-2 ring-amber-400/30'
                              : 'border-stone-200 bg-stone-50 text-stone-700 hover:bg-stone-100'
                          }`}
                        >
                          <span className="font-mono font-bold">{eq.equipment_id}</span>
                          <span
                            className={`ml-1.5 text-[10px] uppercase px-1.5 py-0.5 rounded-md ${
                              eq.status === 'AVAILABLE'
                                ? 'bg-emerald-100 text-emerald-800'
                                : 'bg-amber-100 text-amber-800'
                            }`}
                          >
                            {eq.status}
                          </span>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Right Column: Live Status & Feedback */}
            <div className="lg:col-span-6 space-y-6">
              {/* Instant Success Banner */}
              {actionSuccess && (
                <div className="flex items-center gap-3 rounded-2xl border border-emerald-200 bg-emerald-50 p-4 text-emerald-900 shadow-xs animate-in fade-in duration-200">
                  <CheckCircle2 size={24} className="text-emerald-600 shrink-0" />
                  <div>
                    <p className="text-sm font-extrabold">{actionSuccess}</p>
                    <p className="text-xs text-emerald-700 mt-0.5">
                      {lastActionType === 'CHECK_OUT'
                        ? 'Vehicle is now deployed on-site. Next scan will check it back in.'
                        : 'Vehicle is now returned in yard. Next scan will check it out.'}
                    </p>
                  </div>
                </div>
              )}

              {/* Instant Error Banner */}
              {actionError && (
                <div className="flex items-center gap-3 rounded-2xl border border-rose-200 bg-rose-50 p-4 text-rose-900 shadow-xs animate-in fade-in duration-200">
                  <AlertCircle size={22} className="text-rose-600 shrink-0" />
                  <div>
                    <p className="text-sm font-semibold">{actionError}</p>
                  </div>
                </div>
              )}

              {/* Processing Loader */}
              {isProcessingScan && (
                <div className="rounded-3xl border border-stone-200 bg-white p-8 text-center shadow-sm">
                  <Loader2 size={32} className="animate-spin text-amber-500 mx-auto mb-2" />
                  <p className="text-sm font-bold text-stone-900">Executing Gate Transaction...</p>
                  <p className="text-xs text-stone-500 mt-0.5">Toggling vehicle state</p>
                </div>
              )}

              {/* Vehicle Current State Card */}
              {!isProcessingScan && resolvedEquipment && (
                <div className="rounded-3xl border border-stone-200 bg-white p-6 shadow-sm space-y-5">
                  <div className="flex items-center justify-between pb-4 border-b border-stone-100">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-mono font-bold text-stone-800 bg-stone-100 px-2 py-0.5 rounded-md">
                          {resolvedEquipment.equipment_id}
                        </span>
                        <span
                          className={`rounded-full px-2.5 py-0.5 text-xs font-bold uppercase tracking-wider ${
                            resolvedEquipment.status === 'AVAILABLE'
                              ? 'bg-emerald-100 text-emerald-900 border border-emerald-300'
                              : 'bg-amber-100 text-amber-900 border border-amber-300'
                          }`}
                        >
                          {resolvedEquipment.status === 'AVAILABLE'
                            ? 'Currently Checked In (In Yard)'
                            : 'Currently Checked Out (In Field)'}
                        </span>
                      </div>
                      <h2 className="text-xl font-extrabold text-stone-900 mt-1">
                        {resolvedEquipment.model || resolvedEquipment.equipment_type}
                      </h2>
                      <p className="text-xs text-stone-500">
                        {resolvedEquipment.manufacturer} · SN: {resolvedEquipment.serial_number || 'N/A'}
                      </p>
                    </div>

                    <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-stone-100 text-stone-700">
                      <Truck size={24} />
                    </div>
                  </div>

                  {/* Status Banner */}
                  <div className="rounded-2xl bg-stone-50 p-4 border border-stone-200 text-xs space-y-2">
                    <p className="font-bold text-stone-800">
                      {resolvedEquipment.status === 'AVAILABLE'
                        ? '🟢 In Depot Yard (Available)'
                        : '🟡 Deployed On Job Site'}
                    </p>
                    <p className="text-stone-500">
                      {resolvedEquipment.status === 'AVAILABLE'
                        ? 'Next QR scan will automatically dispatch this vehicle to the designated job site.'
                        : 'Next QR scan will automatically return and check in this vehicle.'}
                    </p>
                  </div>

                  {/* Button to Scan Next */}
                  {!scannerActive && (
                    <button
                      onClick={startScanner}
                      className="w-full inline-flex items-center justify-center gap-2 rounded-2xl bg-[#ab6639] hover:bg-[#8e512d] py-3.5 px-6 text-sm font-bold uppercase tracking-wider text-white transition shadow-md cursor-pointer"
                    >
                      <Camera size={18} />
                      Scan Next Vehicle QR
                    </button>
                  )}
                </div>
              )}

              {/* Instructions if none scanned yet */}
              {!isProcessingScan && !resolvedEquipment && (
                <div className="rounded-3xl border border-dashed border-stone-300 bg-stone-50/50 p-10 text-center">
                  <div className="mx-auto h-14 w-14 rounded-2xl bg-amber-50 text-[#ab6639] flex items-center justify-center mb-3">
                    <Zap size={28} />
                  </div>
                  <h3 className="text-base font-bold text-stone-800">Instant Scan-To-Toggle</h3>
                  <p className="text-xs text-stone-500 mt-1 max-w-sm mx-auto">
                    Point your camera at any vehicle QR code. If it is checked in, it checks out. If it is checked out, it checks in!
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Gate Transactions Log */}
          <div className="rounded-3xl border border-stone-200 bg-white p-6 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="font-bold text-stone-900 text-lg">Gate Check-In / Check-Out Log</h3>
                <p className="text-xs text-stone-500">Live transaction records from gate QR scans</p>
              </div>
              <History size={18} className="text-stone-400" />
            </div>

            {recentTransactions.length === 0 ? (
              <div className="py-10 text-center text-xs text-stone-500">
                No gate transactions recorded yet. Scan a vehicle QR code to see live activity.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr className="border-b border-stone-200 text-xs font-bold uppercase tracking-wider text-stone-500">
                      <th className="pb-3 pr-4">Action</th>
                      <th className="pb-3 pr-4">Equipment</th>
                      <th className="pb-3 pr-4">Operator</th>
                      <th className="pb-3 pr-4">Site</th>
                      <th className="pb-3 pr-4">Time</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-stone-100 text-xs font-medium text-stone-800">
                    {recentTransactions.map((tx) => (
                      <tr key={tx.id} className="hover:bg-stone-50/60 transition">
                        <td className="py-3 pr-4">
                          <span
                            className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-[10px] font-extrabold uppercase tracking-wider ${
                              tx.type === 'CHECK_OUT'
                                ? 'bg-amber-100 text-amber-900'
                                : 'bg-emerald-100 text-emerald-900'
                            }`}
                          >
                            {tx.type === 'CHECK_OUT' ? (
                              <ArrowUpRight size={12} className="text-amber-600" />
                            ) : (
                              <ArrowDownLeft size={12} className="text-emerald-600" />
                            )}
                            {tx.type === 'CHECK_OUT' ? 'Checked Out' : 'Checked In'}
                          </span>
                        </td>
                        <td className="py-3 pr-4">
                          <p className="font-bold text-stone-900">{tx.equipmentId}</p>
                          <p className="text-[11px] text-stone-500">{tx.equipmentName}</p>
                        </td>
                        <td className="py-3 pr-4">{tx.operatorName}</td>
                        <td className="py-3 pr-4">{tx.siteName}</td>
                        <td className="py-3 pr-4 text-stone-500 font-mono">{tx.timestamp}</td>
                      </tr>
                    ))}
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
