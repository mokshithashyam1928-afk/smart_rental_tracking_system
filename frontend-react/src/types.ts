export type Role = 'ADMIN' | 'MANAGER' | 'OPERATOR' | 'VIEWER'

export type EquipmentStatus = 'AVAILABLE' | 'RENTED' | 'IN_USE' | 'IDLE' | 'MAINTENANCE' | 'OVERDUE' | 'OFFLINE'

export type Asset = {
  id: string
  name: string
  type: string
  site: string
  status: EquipmentStatus
  operator: string
  fuel: number
  speed: number
  engineHours: number
  latitude: number
  longitude: number
  lastUpdated: string
  checkoutDate: string
  checkinDate: string
}

export type Rental = {
  id: string
  equipmentId: string
  equipmentName: string
  operator: string
  site: string
  startDate: string
  endDate: string
  status: 'ACTIVE' | 'OVERDUE' | 'COMPLETED'
}

export type DashboardStat = {
  label: string
  value: number
  change: string
  accent: 'amber' | 'teal' | 'slate' | 'rose'
}

export type User = {
  name: string
  email: string
  role: Role
  token: string
}

export type SiteItem = {
  id: number
  site_code: string
  name: string
  address?: string
  status?: string
}

export type OperatorItem = {
  id: number
  employee_id: string
  name: string
  phone?: string
  email?: string
  status?: string
}

export type ResolvedEquipment = {
  id: number
  equipment_id: string
  equipment_type: string
  manufacturer: string
  model: string
  serial_number?: string
  qr_code?: string
  rfid_uid?: string
  status: string
  site?: number | null
  site_detail?: SiteItem | null
  current_operator?: number | null
  operator_detail?: OperatorItem | null
  active_rental?: {
    id: number
    rental_reference: string
    checkout_at: string
    due_at: string
    status: string
    operator_detail?: OperatorItem
    site_detail?: SiteItem
  } | null
}

