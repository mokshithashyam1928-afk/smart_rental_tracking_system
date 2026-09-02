import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  AlertCircle,
  AlertTriangle,
  Bell,
  Camera,
  CheckCircle2,
  HelpCircle,
  LogOut,
  Settings,
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { api } from '../services/api'
import type { Rental } from '../types'

interface NotificationItem {
  id: string
  type: 'OVERDUE' | 'APPROACHING' | 'INFO'
  title: string
  message: string
  equipmentId: string
  site: string
  operator: string
  timeText: string
}

export function Navbar() {
  const { user, logout } = useAuth()
  const [notificationsOpen, setNotificationsOpen] = useState(false)
  const [notifications, setNotifications] = useState<NotificationItem[]>([])
  const [readIds, setReadIds] = useState<Set<string>>(new Set())
  const dropdownRef = useRef<HTMLDivElement>(null)

  // Load real rental overdue & approaching return alerts
  useEffect(() => {
    const loadAlerts = async () => {
      try {
        const rentals: Rental[] = await api.getRentals().catch(() => [])
        const now = Date.now()
        const alertList: NotificationItem[] = []

        rentals.forEach((r) => {
          if (r.status === 'ACTIVE' && r.endDate) {
            const due = new Date(r.endDate).getTime()
            if (!isNaN(due)) {
              if (now > due) {
                // OVERDUE ALERT
                const diffHours = Math.floor((now - due) / (1000 * 60 * 60))
                alertList.push({
                  id: `ovd-${r.id}`,
                  type: 'OVERDUE',
                  title: `OVERDUE: ${r.equipmentName} (${r.equipmentId})`,
                  message: `Return schedule expired ${diffHours > 0 ? `${diffHours}h ago` : 'recently'}. Immediate check-in required.`,
                  equipmentId: r.equipmentId,
                  site: r.site || 'Job Site',
                  operator: r.operator || 'Assigned Operator',
                  timeText: 'Past Due',
                })
              } else if (due - now <= 4 * 3600 * 1000) {
                // APPROACHING RETURN REMINDER
                const remHours = Math.max(1, Math.floor((due - now) / (1000 * 60 * 60)))
                alertList.push({
                  id: `app-${r.id}`,
                  type: 'APPROACHING',
                  title: `Return Approaching: ${r.equipmentName}`,
                  message: `Scheduled return in ~${remHours} hour${remHours > 1 ? 's' : ''}. Prepare for depot gate check-in.`,
                  equipmentId: r.equipmentId,
                  site: r.site || 'Job Site',
                  operator: r.operator || 'Assigned Operator',
                  timeText: `Due in ${remHours}h`,
                })
              }
            }
          }
        })

        setNotifications(alertList)
      } catch (err) {
        console.error('Failed to load notification alerts:', err)
      }
    }

    loadAlerts()
    const interval = setInterval(loadAlerts, 30000)
    return () => clearInterval(interval)
  }, [])

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setNotificationsOpen(false)
      }
    }
    if (notificationsOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [notificationsOpen])

  const unreadCount = notifications.filter((n) => !readIds.has(n.id)).length

  const markAllAsRead = () => {
    setReadIds(new Set(notifications.map((n) => n.id)))
  }

  return (
    <header className="flex items-center justify-between border-b border-stone-200 bg-[#fff8f6] px-6 py-4 relative z-30">
      <div>
        <p className="text-xs uppercase tracking-[0.25em] text-stone-500 font-semibold">Fleet command</p>
        <h2 className="text-xl font-extrabold text-stone-900 tracking-tight">Rental Operations</h2>
      </div>

      <div className="flex items-center gap-3">
        {/* Notifications Button & Dropdown */}
        <div className="relative" ref={dropdownRef}>
          <button
            onClick={() => setNotificationsOpen((prev) => !prev)}
            className="relative rounded-full border border-stone-200 p-2 text-stone-700 hover:bg-stone-100 transition cursor-pointer"
            aria-label="Notifications"
            title="Overdue Alerts & Notifications"
          >
            <Bell size={18} />
            {unreadCount > 0 && (
              <span className="absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-rose-600 text-[10px] font-bold text-white shadow-xs animate-pulse">
                {unreadCount}
              </span>
            )}
          </button>

          {/* Notifications Popover */}
          {notificationsOpen && (
            <div className="absolute right-0 mt-3 w-80 sm:w-96 rounded-3xl border border-stone-200 bg-white p-4 shadow-xl z-50 animate-in fade-in duration-150">
              <div className="flex items-center justify-between pb-3 border-b border-stone-100">
                <div className="flex items-center gap-2">
                  <Bell size={16} className="text-amber-600" />
                  <h4 className="font-extrabold text-stone-900 text-sm">Overdue Alerts & Reminders</h4>
                </div>
                {unreadCount > 0 && (
                  <button
                    onClick={markAllAsRead}
                    className="text-[11px] font-bold text-[#ab6639] hover:underline cursor-pointer"
                  >
                    Mark read
                  </button>
                )}
              </div>

              <div className="mt-3 max-h-80 overflow-y-auto space-y-2.5 divide-y divide-stone-100">
                {notifications.length === 0 ? (
                  <div className="py-8 text-center text-xs text-stone-500">
                    <CheckCircle2 size={24} className="text-emerald-500 mx-auto mb-1.5" />
                    <p className="font-bold text-stone-800">No overdue alerts</p>
                    <p className="text-[11px] text-stone-400 mt-0.5">All fleet vehicles are returning on schedule.</p>
                  </div>
                ) : (
                  notifications.map((n) => (
                    <div
                      key={n.id}
                      className={`pt-2.5 first:pt-0 rounded-xl p-2.5 transition ${
                        n.type === 'OVERDUE'
                          ? 'bg-rose-50/80 border border-rose-200'
                          : 'bg-amber-50/80 border border-amber-200'
                      }`}
                    >
                      <div className="flex items-start gap-2.5">
                        {n.type === 'OVERDUE' ? (
                          <AlertCircle size={16} className="text-rose-600 shrink-0 mt-0.5" />
                        ) : (
                          <AlertTriangle size={16} className="text-amber-600 shrink-0 mt-0.5" />
                        )}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between">
                            <span
                              className={`text-[9px] font-extrabold uppercase px-1.5 py-0.5 rounded ${
                                n.type === 'OVERDUE'
                                  ? 'bg-rose-200 text-rose-900'
                                  : 'bg-amber-200 text-amber-900'
                              }`}
                            >
                              {n.type}
                            </span>
                            <span className="text-[10px] font-semibold text-stone-500">{n.timeText}</span>
                          </div>
                          <p className="text-xs font-bold text-stone-900 mt-1">{n.title}</p>
                          <p className="text-[11px] text-stone-600 mt-0.5 leading-snug">{n.message}</p>
                          <div className="mt-2 flex items-center justify-between text-[10px] pt-1.5 border-t border-stone-200/60">
                            <span className="text-stone-500 truncate max-w-[140px]">
                              {n.site}
                            </span>
                            <Link
                              to="/checkin-checkout"
                              onClick={() => setNotificationsOpen(false)}
                              className="font-bold text-[#ab6639] hover:underline inline-flex items-center gap-1"
                            >
                              <Camera size={11} />
                              Check In →
                            </Link>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>

              {notifications.length > 0 && (
                <div className="mt-3 pt-2.5 border-t border-stone-100 text-center">
                  <Link
                    to="/rentals"
                    onClick={() => setNotificationsOpen(false)}
                    className="text-xs font-bold text-[#ab6639] hover:underline"
                  >
                    View All Rental Contracts & Alerts →
                  </Link>
                </div>
              )}
            </div>
          )}
        </div>

        <button className="rounded-full border border-stone-200 p-2 text-stone-700 hover:bg-stone-100" aria-label="Settings" title="Settings">
          <Settings size={18} />
        </button>
        <button className="rounded-full border border-stone-200 p-2 text-stone-700 hover:bg-stone-100" aria-label="Support" title="Support">
          <HelpCircle size={18} />
        </button>

        <div className="ml-2 flex items-center gap-3 rounded-full border border-stone-200 bg-white px-3 py-2 shadow-xs">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[#ab6639] text-xs font-bold text-white">
            {user?.name?.slice(0, 1) || 'U'}
          </div>
          <div>
            <p className="text-sm font-semibold text-stone-900">{user?.name || 'User'}</p>
            <p className="text-[10px] uppercase tracking-[0.2em] text-stone-500">{user?.role || 'VIEWER'}</p>
          </div>
          <button onClick={logout} className="ml-2 rounded-full bg-stone-900 p-2 text-white hover:bg-stone-700 cursor-pointer" aria-label="Logout">
            <LogOut size={16} />
          </button>
        </div>
      </div>
    </header>
  )
}
