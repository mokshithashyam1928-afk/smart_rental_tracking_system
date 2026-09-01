import { useEffect, useRef, useState } from 'react'
import type { Asset } from '../types'

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws/tracking/'

/**
 * Connects to the Django Channels WebSocket for live equipment telemetry.
 * Falls back to polling every 10 seconds if WebSocket is unavailable.
 */
export function useWebSocket(initialAssets: Asset[]) {
  const [assets, setAssets] = useState<Asset[]>(initialAssets)
  const socketRef = useRef<WebSocket | null>(null)
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

  // Keep assets list in sync when initialAssets changes from parent
  useEffect(() => {
    if (initialAssets.length > 0) {
      setAssets(initialAssets)
    }
  }, [initialAssets])

  useEffect(() => {
    function connect() {
      try {
        const token = sessionStorage.getItem('access_token')
        const url = token ? `${WS_URL}?token=${token}` : WS_URL
        const socket = new WebSocket(url)
        socketRef.current = socket

        socket.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data) as {
              equipment_id?: string
              latitude?: number
              longitude?: number
              speed?: number
              fuel_level?: number
              status?: string
            }
            if (!data.equipment_id) return

            setAssets((current) =>
              current.map((asset) => {
                if (asset.id === data.equipment_id) {
                  return {
                    ...asset,
                    latitude: data.latitude ?? asset.latitude,
                    longitude: data.longitude ?? asset.longitude,
                    speed: data.speed ?? asset.speed,
                    fuel: data.fuel_level ?? asset.fuel,
                    status: (data.status as Asset['status']) ?? asset.status,
                    lastUpdated: 'just now',
                  }
                }
                return asset
              }),
            )
          } catch {
            // ignore parse errors
          }
        }

        socket.onclose = () => {
          // Auto-reconnect after 5 seconds
          reconnectTimer.current = setTimeout(connect, 5000)
        }

        socket.onerror = () => {
          socket.close()
        }
      } catch {
        // WebSocket not available, silently ignore — data comes from REST poll
      }
    }

    connect()

    return () => {
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current)
      if (socketRef.current) {
        socketRef.current.onclose = null // prevent reconnect on intentional close
        socketRef.current.close()
      }
    }
  }, [])

  return { assets }
}
