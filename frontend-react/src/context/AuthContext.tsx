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

async function loginService(email: string, password: string) {
  const { api } = await import('../services/api')
  return api.login(email, password)
}

async function signupService(name: string, email: string, password: string, role: Role) {
  const { api } = await import('../services/api')
  return api.signup(name, email, password, role)
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)

  useEffect(() => {
    const saved = localStorage.getItem(AUTH_KEY)
    if (saved) {
      setUser(JSON.parse(saved) as User)
    }
  }, [])

  const saveUser = (nextUser: User) => {
    localStorage.setItem(AUTH_KEY, JSON.stringify(nextUser))
    setUser(nextUser)
  }

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      login: async (email: string, password: string) => {
        const nextUser = await loginService(email, password)
        saveUser(nextUser)
        return nextUser
      },
      signup: async (name: string, email: string, password: string, role: Role) => {
        const nextUser = await signupService(name, email, password, role)
        saveUser(nextUser)
        return nextUser
      },
      logout: () => {
        localStorage.removeItem(AUTH_KEY)
        setUser(null)
      },
    }),
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
