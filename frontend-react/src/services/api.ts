/**
 * api.ts — Real backend integration for Caterpillar Smart Rental Tracking System
 * Connects to Django backend at http://localhost:8000 via JWT-authenticated REST API.
 */
import type { Asset, DashboardStat, Rental, Role, User } from '../types'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// ---------------------------------------------------------------------------
// Token management
// ---------------------------------------------------------------------------
function getToken(): string | null {
  return sessionStorage.getItem('access_token')
}

function setTokens(access: string, refresh: string) {
  sessionStorage.setItem('access_token', access)
  localStorage.setItem('refresh_token', refresh)
}

function clearTokens() {
  sessionStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
}

// ---------------------------------------------------------------------------
// Core fetch wrapper with auto-refresh on 401
// ---------------------------------------------------------------------------
async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  }
  if (token) headers['Authorization'] = `Bearer ${token}`

  let res = await fetch(`${BASE_URL}${path}`, { ...options, headers })

  // Auto-refresh on 401
  if (res.status === 401) {
    const refresh = localStorage.getItem('refresh_token')
    if (refresh) {
      const refreshRes = await fetch(`${BASE_URL}/api/auth/token/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh }),
      })
      if (refreshRes.ok) {
        const { access } = await refreshRes.json()
        sessionStorage.setItem('access_token', access)
        headers['Authorization'] = `Bearer ${access}`
        res = await fetch(`${BASE_URL}${path}`, { ...options, headers })
      } else {
        clearTokens()
        window.location.href = '/login'
        throw new Error('Session expired. Please log in again.')
      }
    } else {
      clearTokens()
      window.location.href = '/login'
      throw new Error('Not authenticated')
    }
  }

  if (!res.ok) {
    const detail = await res.text()
    throw new Error(detail || `API error: ${res.status}`)
  }

  // Handle empty response (204 No Content)
  if (res.status === 204) return {} as T
  return res.json() as Promise<T>
}

// ---------------------------------------------------------------------------
// Response → frontend type adapters
// ---------------------------------------------------------------------------
function adaptEquipment(eq: Record<string, unknown>): Asset {
  const liveState = (eq.live_state as Record<string, unknown>) || {}
  return {
    id: eq.equipment_id as string,
    name: (eq.model as string) || (eq.equipment_type as string),
    type: eq.equipment_type as string,
    site: ((eq.site as Record<string, unknown>)?.name as string) || 'Unassigned',
    status: (eq.status as Asset['status']) || 'OFFLINE',
    operator: ((eq.current_operator as Record<string, unknown>)?.name as string) || 'Unassigned',
    fuel: (liveState.fuel_level as number) ?? 0,
    speed: (liveState.speed as number) ?? 0,
    engineHours: (liveState.engine_hours as number) ?? 0,
    latitude: (liveState.latitude as number) ?? 12.9716,
    longitude: (liveState.longitude as number) ?? 77.5946,
    lastUpdated: liveState.updated_at
      ? new Date(liveState.updated_at as string).toLocaleTimeString()
      : 'Unknown',
    checkoutDate: '',
    checkinDate: '',
  }
}

function adaptRental(r: Record<string, unknown>): Rental {
  const eq = (r.equipment as Record<string, unknown>) || {}
  const site = (r.site as Record<string, unknown>) || {}
  const operator = (r.operator as Record<string, unknown>) || {}
  return {
    id: r.rental_reference as string,
    equipmentId: eq.equipment_id as string,
    equipmentName: (eq.model as string) || (eq.equipment_type as string),
    operator: (operator.name as string) || '',
    site: (site.name as string) || '',
    startDate: r.checkout_at ? (r.checkout_at as string).split('T')[0] : '',
    endDate: r.due_at ? (r.due_at as string).split('T')[0] : '',
    status:
      r.status === 'CHECKED_IN'
        ? 'COMPLETED'
        : r.status === 'OVERDUE'
          ? 'OVERDUE'
          : 'ACTIVE',
  }
}

function adaptDashboardStats(summary: Record<string, unknown>): DashboardStat[] {
  return [
    { label: 'Total Assets', value: (summary.total_equipment as number) || 0, change: '', accent: 'amber' },
    { label: 'Available', value: (summary.available as number) || 0, change: '', accent: 'teal' },
    { label: 'Rented', value: (summary.rented as number) || 0, change: '', accent: 'slate' },
    { label: 'In Use', value: (summary.in_use as number) || 0, change: '', accent: 'amber' },
    { label: 'Idle', value: (summary.idle as number) || 0, change: '', accent: 'slate' },
    { label: 'Overdue', value: (summary.overdue as number) || 0, change: '', accent: 'rose' },
    { label: 'Offline', value: (summary.offline as number) || 0, change: '', accent: 'slate' },
  ]
}

// ---------------------------------------------------------------------------
// Public API surface (drop-in replacement for the old mock api)
// ---------------------------------------------------------------------------
export const api = {
  // Auth
  async login(email: string, password: string): Promise<User> {
    const res = await fetch(`${BASE_URL}/api/auth/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error((err as { detail?: string }).detail || 'Invalid email or password')
    }
    const data = await res.json() as {
      access: string; refresh: string;
      user: { id: number; email: string; first_name: string; last_name: string; role: Role }
    }
    setTokens(data.access, data.refresh)
    return {
      name: `${data.user.first_name} ${data.user.last_name}`.trim() || data.user.email,
      email: data.user.email,
      role: data.user.role,
      token: data.access,
    }
  },

  async signup(name: string, email: string, password: string, role: Role): Promise<User> {
    const [firstName, ...rest] = name.trim().split(' ')
    const res = await fetch(`${BASE_URL}/api/auth/register/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email,
        password,
        first_name: firstName,
        last_name: rest.join(' '),
        role,
      }),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(JSON.stringify(err) || 'Registration failed')
    }
    const data = await res.json() as {
      access: string; refresh: string;
      user: { email: string; first_name: string; last_name: string; role: Role }
    }
    setTokens(data.access, data.refresh)
    return {
      name,
      email: data.user.email,
      role: data.user.role,
      token: data.access,
    }
  },

  logout() {
    clearTokens()
  },

  // Dashboard
  async getDashboardStats(): Promise<DashboardStat[]> {
    const summary = await request<Record<string, unknown>>('/api/dashboard/summary/')
    return adaptDashboardStats(summary)
  },

  // Equipment / Assets
  async getAssets(): Promise<Asset[]> {
    const res = await request<{ results?: unknown[] } | unknown[]>('/api/equipment/')
    const items = Array.isArray(res) ? res : (res as { results?: unknown[] }).results ?? []
    return items.map((eq) => adaptEquipment(eq as Record<string, unknown>))
  },

  async getLiveAssets(): Promise<Asset[]> {
    const items = await request<unknown[]>('/api/dashboard/live_assets/')
    return items.map((eq) => adaptEquipment(eq as Record<string, unknown>))
  },

  // Rentals
  async getRentals(): Promise<Rental[]> {
    const res = await request<{ results?: unknown[] } | unknown[]>('/api/rentals/')
    const items = Array.isArray(res) ? res : (res as { results?: unknown[] }).results ?? []
    return items.map((r) => adaptRental(r as Record<string, unknown>))
  },

  // Analytics
  async getAnalytics(): Promise<Record<string, unknown>> {
    return request('/api/analytics/')
  },

  // Anomalies
  async getAnomalies(): Promise<unknown[]> {
    const res = await request<{ results?: unknown[] } | unknown[]>('/api/anomalies/')
    return Array.isArray(res) ? res : (res as { results?: unknown[] }).results ?? []
  },

  // Notifications
  async getNotifications(): Promise<unknown[]> {
    const res = await request<{ results?: unknown[] } | unknown[]>('/api/notifications/')
    return Array.isArray(res) ? res : (res as { results?: unknown[] }).results ?? []
  },

  async getUnreadCount(): Promise<number> {
    const res = await request<{ unread_count: number }>('/api/notifications/unread_count/')
    return res.unread_count
  },

  // Checkout / Checkin
  async checkout(equipmentId: number, operatorId: number, siteId: number, dueAt: string) {
    return request('/api/rentals/checkout/', {
      method: 'POST',
      body: JSON.stringify({ equipment_id: equipmentId, operator_id: operatorId, site_id: siteId, due_at: dueAt }),
    })
  },

  async checkin(rentalId: number) {
    return request('/api/rentals/checkin/', {
      method: 'POST',
      body: JSON.stringify({ rental_id: rentalId }),
    })
  },
}
