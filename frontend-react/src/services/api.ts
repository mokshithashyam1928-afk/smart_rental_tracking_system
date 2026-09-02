/**
 * api.ts — Real backend integration for Caterpillar Smart Rental Tracking System
 * Connects to Django backend at http://localhost:8000 via JWT-authenticated REST API.
 */
import type { Asset, DashboardStat, OperatorItem, Rental, ResolvedEquipment, Role, SiteItem, User } from '../types'

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
// Core fetch wrapper with auto-refresh on 401 and response unwrapping
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
        const raw = await refreshRes.json()
        const payload = raw?.data ?? raw
        const access = payload.access
        if (access) {
          sessionStorage.setItem('access_token', access)
          headers['Authorization'] = `Bearer ${access}`
          res = await fetch(`${BASE_URL}${path}`, { ...options, headers })
        }
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
    const errJson = await res.json().catch(() => null)
    const message =
      errJson?.error?.message ||
      errJson?.detail ||
      errJson?.message ||
      (typeof errJson === 'string' ? errJson : `API error: ${res.status}`)
    throw new Error(message)
  }

  if (res.status === 204) return {} as T
  const json = await res.json()
  // Automatically unwrap APIResponse { success: true, data: ... }
  if (json && typeof json === 'object' && 'data' in json && 'success' in json) {
    return json.data as T
  }
  return json as T
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
  const eq = (r.equipment_detail as Record<string, unknown>) || (r.equipment as Record<string, unknown>) || {}
  const site = (r.site_detail as Record<string, unknown>) || (r.site as Record<string, unknown>) || {}
  const operator = (r.operator_detail as Record<string, unknown>) || (r.operator as Record<string, unknown>) || {}
  return {
    id: (r.rental_reference as string) || (r.id ? `RNT-${r.id}` : 'RNT'),
    equipmentId: (eq.equipment_id as string) || '',
    equipmentName: (eq.model as string) || (eq.equipment_type as string) || (eq.equipment_id as string) || 'Equipment',
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
// Public API surface
// ---------------------------------------------------------------------------
export const api = {
  // Auth
  async login(email: string, password: string): Promise<User> {
    const res = await fetch(`${BASE_URL}/api/auth/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email.trim(), password }),
    })
    const json = await res.json().catch(() => ({}))
    if (!res.ok) {
      const err =
        json?.error?.message ||
        json?.detail ||
        json?.message ||
        'Invalid email or password'
      throw new Error(err)
    }

    const payload = json?.data ?? json
    const user = payload.user
    const access = payload.access
    const refresh = payload.refresh

    setTokens(access, refresh)
    return {
      name: `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.email,
      email: user.email,
      role: user.role,
      token: access,
    }
  },

  async signup(name: string, email: string, password: string, role: Role): Promise<User> {
    const [firstName, ...rest] = name.trim().split(' ')
    const res = await fetch(`${BASE_URL}/api/auth/register/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: email.trim(),
        password,
        first_name: firstName,
        last_name: rest.join(' '),
        role,
      }),
    })
    const json = await res.json().catch(() => ({}))
    if (!res.ok) {
      const err =
        json?.error?.message ||
        json?.detail ||
        json?.message ||
        'Registration failed'
      throw new Error(err)
    }

    const payload = json?.data ?? json
    const user = payload.user
    const access = payload.access
    const refresh = payload.refresh

    setTokens(access, refresh)
    return {
      name,
      email: user.email,
      role: user.role,
      token: access,
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
    const array = Array.isArray(items) ? items : []
    return array.map((eq) => adaptEquipment(eq as Record<string, unknown>))
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

  // QR / Identifier Resolution
  async resolveEquipmentIdentifier(identifier: string, identifierType: 'QR' | 'RFID' = 'QR'): Promise<ResolvedEquipment> {
    return request<ResolvedEquipment>('/api/equipment/resolve_identifier/', {
      method: 'POST',
      body: JSON.stringify({
        identifier_type: identifierType,
        identifier: identifier.trim(),
      }),
    })
  },

  // Operators list
  async getOperators(): Promise<OperatorItem[]> {
    const res = await request<{ results?: OperatorItem[] } | OperatorItem[]>('/api/operators/')
    return Array.isArray(res) ? res : (res as { results?: OperatorItem[] }).results ?? []
  },

  // Sites list
  async getSites(): Promise<SiteItem[]> {
    const res = await request<{ results?: SiteItem[] } | SiteItem[]>('/api/sites/')
    return Array.isArray(res) ? res : (res as { results?: SiteItem[] }).results ?? []
  },

  // Raw Equipment list with full database IDs
  async getRawEquipment(): Promise<ResolvedEquipment[]> {
    const res = await request<{ results?: ResolvedEquipment[] } | ResolvedEquipment[]>('/api/equipment/')
    return Array.isArray(res) ? res : (res as { results?: ResolvedEquipment[] }).results ?? []
  },

  // Register new vehicle
  async registerEquipment(payload: {
    equipment_id: string
    model: string
    equipment_type: string
    site?: number | null
    serial_number?: string
  }): Promise<ResolvedEquipment> {
    return request<ResolvedEquipment>('/api/equipment/', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  },

  // Unified atomic QR Gate Scan
  async scanQrGate(payload: {
    qr_code: string
    operator_id?: number | ''
    site_id?: number | ''
    due_hours?: number
  }): Promise<{
    action: 'CHECK_OUT' | 'CHECK_IN'
    equipment: ResolvedEquipment
    rental: Record<string, unknown> | null
  }> {
    return request<{
      action: 'CHECK_OUT' | 'CHECK_IN'
      equipment: ResolvedEquipment
      rental: Record<string, unknown> | null
    }>('/api/rentals/qr_scan/', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  },
}

