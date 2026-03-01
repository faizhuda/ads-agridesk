import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import Navbar from './components/Navbar'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import AjukanSuratPage from './pages/AjukanSuratPage'
import VerifyPage from './pages/VerifyPage'

function ProtectedRoute({ children, allowedRoles }) {
  const { isLoggedIn, role } = useAuth()
  if (!isLoggedIn) return <Navigate to="/login" replace />
  if (allowedRoles && !allowedRoles.includes(role)) return <Navigate to="/dashboard" replace />
  return children
}

function GuestRoute({ children }) {
  const { isLoggedIn } = useAuth()
  if (isLoggedIn) return <Navigate to="/dashboard" replace />
  return children
}

function HomePage() {
  const { isLoggedIn } = useAuth()
  if (isLoggedIn) return <Navigate to="/dashboard" replace />

  return (
    <div className="hero">
      <h1>Agridesk</h1>
      <p>Sistem Pengajuan Surat Akademik — Digital, Terverifikasi, Transparan</p>
      <div className="hero-flow">
        <div className="flow-step">
          <span className="flow-icon">1</span>
          <span>Mahasiswa Ajukan Surat</span>
        </div>
        <span className="flow-arrow">&rarr;</span>
        <div className="flow-step">
          <span className="flow-icon">2</span>
          <span>Dosen Tanda Tangan</span>
        </div>
        <span className="flow-arrow">&rarr;</span>
        <div className="flow-step">
          <span className="flow-icon">3</span>
          <span>Admin Approve</span>
        </div>
        <span className="flow-arrow">&rarr;</span>
        <div className="flow-step">
          <span className="flow-icon">4</span>
          <span>Verifikasi Publik</span>
        </div>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Navbar />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<GuestRoute><LoginPage /></GuestRoute>} />
          <Route path="/register" element={<GuestRoute><RegisterPage /></GuestRoute>} />
          <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
          <Route path="/ajukan" element={<ProtectedRoute allowedRoles={['MAHASISWA']}><AjukanSuratPage /></ProtectedRoute>} />
          <Route path="/verify" element={<VerifyPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}