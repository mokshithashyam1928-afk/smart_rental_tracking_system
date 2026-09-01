import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import type { Role, User } from '../types'

const AUTH_KEY = 'smart-rental-auth'

type AuthContextValue = {
  user: User | null
  login: (email: string, password: string) => Promise<User>
  signup: (name: string, email: string, password: string, role: Role) => Promise<User>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)

  // Restore user session on page load
  useEffect(() => {
    const saved = localStorage.getItem(AUTH_KEY)
    if (saved) {
      try {
        setUser(JSON.parse(saved) as User)
      } catch {
        localStorage.removeItem(AUTH_KEY)
      }
    }
  }, [])

  const saveUser = (nextUser: User) => {
    localStorage.setItem(AUTH_KEY, JSON.stringify(nextUser))
    // Also keep the access token in sessionStorage for api.ts to pick up
    if (nextUser.token) {
      sessionStorage.setItem('access_token', nextUser.token)
    }
    setUser(nextUser)
  }

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      login: async (email: string, password: string) => {
        const { api } = await import('../services/api')
        const nextUser = await api.login(email, password)
        saveUser(nextUser)
        return nextUser
      },
      signup: async (name: string, email: string, password: string, role: Role) => {
        const { api } = await import('../services/api')
        const nextUser = await api.signup(name, email, password, role)
        saveUser(nextUser)
        return nextUser
      },
      logout: () => {
        import('../services/api').then(({ api }) => api.logout())
        localStorage.removeItem(AUTH_KEY)
        setUser(null)
      },
    }),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [user],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
