import { useEffect, useState } from 'react'
import type { Asset } from '../types'

export function useWebSocket(initialAssets: Asset[]) {
  const [assets, setAssets] = useState<Asset[]>(initialAssets)

  useEffect(() => {
    const interval = window.setInterval(() => {
      setAssets((current) =>
        current.map((asset, index) => {
          const drift = (index % 3) * 1.5
          const nextFuel = Math.max(15, Math.min(98, asset.fuel + (index % 2 === 0 ? 2 : -2)))
          const nextSpeed = Math.max(0, Math.min(68, asset.speed + drift / 6 - 0.6))

          return {
            ...asset,
            fuel: Number(nextFuel.toFixed(0)),
            speed: Number(nextSpeed.toFixed(1)),
            lastUpdated: 'just now',
          }
        }),
      )
    }, 5000)

    return () => window.clearInterval(interval)
  }, [])

  return { assets }
}
