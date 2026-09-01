import { useEffect, useState } from 'react'
import { MapContainer, Marker, Popup, TileLayer } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { Navbar } from '../components/Navbar'
import { Sidebar } from '../components/Sidebar'
import { useAuth } from '../context/AuthContext'
import { mockAssets } from '../data/mockData'
import { useWebSocket } from '../hooks/useWebSocket'
import { api } from '../services/api'
import type { Asset } from '../types'

const icon = new L.Icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
})

export function LiveMapPage() {
  const { user } = useAuth()
  const [initialAssets, setInitialAssets] = useState<Asset[]>(mockAssets)

  useEffect(() => {
    async function loadAssets() {
      try {
        const live = await api.getLiveAssets()
        if (live && live.length > 0) {
          setInitialAssets(live)
        }
      } catch {
        // fallback to mockAssets
      }
    }
    loadAssets()
  }, [])

  const { assets } = useWebSocket(initialAssets)

  // Default center based on first asset or default
  const centerLat = assets[0]?.latitude || 12.9716
  const centerLng = assets[0]?.longitude || 77.5946

  return (
    <div className="flex min-h-screen bg-[#fff8f6] text-stone-900">
      <Sidebar role={user?.role ?? 'VIEWER'} />

      <div className="flex-1">
        <Navbar />

        <main className="p-6">
          <div className="mb-6 flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.25em] text-stone-500">Field telemetry</p>
              <h2 className="mt-2 text-3xl font-bold">Live equipment map</h2>
            </div>
            <span className="inline-flex items-center gap-2 rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-800">
              <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
              Live Telemetry Active ({assets.length} machines)
            </span>
          </div>

          <div className="overflow-hidden rounded-3xl border border-stone-200 bg-white shadow-sm">
            <div className="h-[620px] w-full">
              <MapContainer center={[centerLat, centerLng]} zoom={10} scrollWheelZoom className="h-full w-full">
                <TileLayer
                  attribution='&copy; OpenStreetMap contributors'
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />

                {assets.map((asset) => (
                  <Marker key={asset.id} position={[asset.latitude, asset.longitude]} icon={icon}>
                    <Popup>
                      <div className="space-y-1 text-sm">
                        <p className="font-bold text-stone-900">{asset.name}</p>
                        <p className="text-xs uppercase tracking-[0.15em] text-stone-500 font-semibold">{asset.id}</p>
                        <p className="text-xs text-stone-600">Site: <span className="font-medium text-stone-800">{asset.site}</span></p>
                        <p className="text-xs text-stone-600">Operator: <span className="font-medium text-stone-800">{asset.operator}</span></p>
                        <div className="mt-2 grid grid-cols-2 gap-1 rounded bg-stone-100 p-1.5 text-[11px]">
                          <div>Speed: <span className="font-semibold">{asset.speed} km/h</span></div>
                          <div>Fuel: <span className="font-semibold">{asset.fuel}%</span></div>
                          <div className="col-span-2">Engine Hrs: <span className="font-semibold">{asset.engineHours} hrs</span></div>
                        </div>
                      </div>
                    </Popup>
                  </Marker>
                ))}
              </MapContainer>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
