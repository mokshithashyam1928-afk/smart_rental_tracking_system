import { dashboardStats, mockAssets, rentals } from '../data/mockData'
import type { Asset, Rental, Role, User } from '../types'

const userAccounts: Record<string, { password: string; role: Role; name: string }> = {
  'admin@smart-rental.io': { password: 'admin123', role: 'ADMIN', name: 'Alicia Morgan' },
  'manager@smart-rental.io': { password: 'manager123', role: 'MANAGER', name: 'Daniel Ross' },
  'operator@smart-rental.io': { password: 'operator123', role: 'OPERATOR', name: 'Sana Lee' },
  'viewer@smart-rental.io': { password: 'viewer123', role: 'VIEWER', name: 'Marco Ruiz' },
}

export const api = {
  async login(email: string, password: string): Promise<User> {
    const record = userAccounts[email.toLowerCase()]

    if (!record || record.password !== password) {
      throw new Error('Invalid email or password')
    }

    return {
      name: record.name,
      email,
      role: record.role,
      token: `mock-jwt-${record.role.toLowerCase()}`,
    }
  },

  async signup(name: string, email: string, password: string, role: Role): Promise<User> {
    userAccounts[email.toLowerCase()] = { password, role, name }

    return {
      name,
      email,
      role,
      token: `mock-jwt-${role.toLowerCase()}`,
    }
  },

  async getDashboardStats(): Promise<typeof dashboardStats> {
    return dashboardStats
  },

  async getAssets(): Promise<Asset[]> {
    return mockAssets
  },

  async getRentals(): Promise<Rental[]> {
    return rentals
  },
}
