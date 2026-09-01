export type Role = 'ADMIN' | 'MANAGER' | 'OPERATOR' | 'VIEWER'

export type EquipmentStatus = 'IN_USE' | 'AVAILABLE' | 'IDLE' | 'OVERDUE' | 'OFFLINE'

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
