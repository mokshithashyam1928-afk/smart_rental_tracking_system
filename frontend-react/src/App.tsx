import type { ReactNode } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import { AnalyticsPage } from './pages/AnalyticsPage'
import { DashboardPage } from './pages/DashboardPage'
import { EquipmentPage } from './pages/EquipmentPage'
import { InventoryPage } from './pages/InventoryPage'
import { LiveMapPage } from './pages/LiveMapPage'
import { LoginPage } from './pages/LoginPage'
import { RentalsPage } from './pages/RentalsPage'
import { SignupPage } from './pages/SignupPage'

function ProtectedRoute({ children }: { children: ReactNode }) {
  const { user } = useAuth()

  if (!user) {
    return <Navigate to="/" replace />
  }

  return <>{children}</>
}

export default function App() {
  const { user } = useAuth()

  return (
    <Routes>
      <Route path="/" element={user ? <Navigate to="/dashboard" replace /> : <LoginPage />} />
      <Route path="/signup" element={user ? <Navigate to="/dashboard" replace /> : <SignupPage />} />

      <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
      <Route path="/equipment" element={<ProtectedRoute><EquipmentPage /></ProtectedRoute>} />
      <Route path="/inventory" element={<ProtectedRoute><InventoryPage /></ProtectedRoute>} />
      <Route path="/sites" element={<ProtectedRoute><InventoryPage /></ProtectedRoute>} />
      <Route path="/operators" element={<ProtectedRoute><InventoryPage /></ProtectedRoute>} />
      <Route path="/map" element={<ProtectedRoute><LiveMapPage /></ProtectedRoute>} />
      <Route path="/rentals" element={<ProtectedRoute><RentalsPage /></ProtectedRoute>} />
      <Route path="/analytics" element={<ProtectedRoute><AnalyticsPage /></ProtectedRoute>} />

      <Route path="*" element={<Navigate to={user ? '/dashboard' : '/'} replace />} />
    </Routes>
  )
}
