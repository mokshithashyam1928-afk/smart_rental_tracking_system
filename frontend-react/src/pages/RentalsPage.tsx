import { useEffect, useState } from 'react'
import { Navbar } from '../components/Navbar'
import { Sidebar } from '../components/Sidebar'
import { useAuth } from '../context/AuthContext'
import { api } from '../services/api'
import type { Rental } from '../types'

export function RentalsPage() {
  const { user } = useAuth()
  const [rentals, setRentals] = useState<Rental[]>([])

  useEffect(() => {
    const load = async () => {
      const nextRentals = await api.getRentals()
      setRentals(nextRentals)
    }
    load()
  }, [])

  return (
    <div className="flex min-h-screen bg-[#fff8f6] text-stone-900">
      <Sidebar role={user?.role ?? 'VIEWER'} />

      <div className="flex-1">
        <Navbar />

        <main className="p-6">
          <div className="mb-6">
            <p className="text-xs uppercase tracking-[0.25em] text-stone-500">Rentals</p>
            <h2 className="mt-2 text-3xl font-bold">Current contracts</h2>
          </div>

          <div className="rounded-3xl border border-stone-200 bg-white p-5 shadow-sm">
            <table className="min-w-full text-left text-sm">
              <thead>
                <tr className="border-b border-stone-200 text-stone-500">
                  <th className="pb-3 pr-4 font-medium">Rental ID</th>
                  <th className="pb-3 pr-4 font-medium">Equipment</th>
                  <th className="pb-3 pr-4 font-medium">Operator</th>
                  <th className="pb-3 pr-4 font-medium">Site</th>
                  <th className="pb-3 pr-4 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {rentals.map((rental) => (
                  <tr key={rental.id} className="border-b border-stone-100">
                    <td className="py-3 pr-4 font-semibold text-stone-900">{rental.id}</td>
                    <td className="py-3 pr-4">{rental.equipmentName}</td>
                    <td className="py-3 pr-4">{rental.operator}</td>
                    <td className="py-3 pr-4">{rental.site}</td>
                    <td className="py-3 pr-4">
                      <span className={`rounded-full px-2 py-1 text-[10px] font-bold ${rental.status === 'ACTIVE' ? 'bg-[#ccfbf1] text-[#115e59]' : rental.status === 'OVERDUE' ? 'bg-rose-100 text-rose-700' : 'bg-stone-200 text-stone-700'}`}>
                        {rental.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </main>
      </div>
    </div>
  )
}
