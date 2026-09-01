import { MapContainer, Marker, Popup, TileLayer } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { Navbar } from '../components/Navbar'
import { Sidebar } from '../components/Sidebar'
import { useAuth } from '../context/AuthContext'
import { mockAssets } from '../data/mockData'

const icon = new L.Icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
})

export function LiveMapPage() {
  const { user } = useAuth()

  return (
    <div className="flex min-h-screen bg-[#fff8f6] text-stone-900">
      <Sidebar role={user?.role ?? 'VIEWER'} />

      <div className="flex-1">
        <Navbar />

        <main className="p-6">
          <div className="mb-6">
            <p className="text-xs uppercase tracking-[0.25em] text-stone-500">Field telemetry</p>
            <h2 className="mt-2 text-3xl font-bold">Live equipment map</h2>
          </div>

          <div className="overflow-hidden rounded-3xl border border-stone-200 bg-white shadow-sm">
            <div className="h-[620px] w-full">
              <MapContainer center={[40.75, -73.99]} zoom={11} scrollWheelZoom className="h-full w-full">
                <TileLayer
                  attribution='&copy; OpenStreetMap contributors'
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />

                {mockAssets.map((asset) => (
                  <Marker key={asset.id} position={[asset.latitude, asset.longitude]} icon={icon}>
                    <Popup>
                      <div className="space-y-1">
                        <p className="text-sm font-bold">{asset.name}</p>
                        <p className="text-xs uppercase tracking-[0.15em] text-stone-500">{asset.id}</p>
                        <p>Operator: {asset.operator}</p>
                        <p>Speed: {asset.speed} km/h</p>
                        <p>Fuel: {asset.fuel}%</p>
                        <p>Engine hours: {asset.engineHours}</p>
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
