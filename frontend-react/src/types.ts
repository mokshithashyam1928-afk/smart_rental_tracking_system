export type Role = 'ADMIN' | 'MANAGER' | 'OPERATOR' | 'VIEWER'

export type EquipmentStatus = 'AVAILABLE' | 'RENTED' | 'IN_USE' | 'IDLE' | 'MAINTENANCE' | 'OVERDUE' | 'OFFLINE'

export type Asset = {
  id: string
  name: string
  type: string
  site: string
  siteCode?: string
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
  siteCode?: string
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

export type ForecastItem = {
  id: number
  site: number
  site_name?: string
  equipment_type: string
  forecast_date: string
  predicted_demand: number
  confidence: number
  model_version: string
  generated_at?: string
}

export type AnomalyItem = {
  id: number
  equipment: number
  equipment_id?: string
  equipment_model?: string
  detected_at: string
  anomaly_type: string
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
  score: number
  reason: string
  status: 'OPEN' | 'ACKNOWLEDGED' | 'RESOLVED' | 'FALSE_POSITIVE'
  metadata?: Record<string, unknown>
}

export type RecommendationItem = {
  id: number
  equipment: number
  equipment_id?: string
  equipment_model?: string
  source_site: number
  source_site_name?: string
  target_site: number
  target_site_name?: string
  reason: string
  current_utilization: number
  predicted_target_demand: number
  score: number
  status: 'PENDING' | 'ACCEPTED' | 'DISMISSED' | 'EXPIRED'
  created_at: string
}


