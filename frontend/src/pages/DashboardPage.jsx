import { useAuth } from '../context/AuthContext'
import MahasiswaDashboard from './dashboards/MahasiswaDashboard'
import DosenDashboard from './dashboards/DosenDashboard'
import AdminDashboard from './dashboards/AdminDashboard'

export default function DashboardPage() {
  const { role, name } = useAuth()

  return (
    <div className="page">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <p>Selamat datang, <strong>{name}</strong> — {role}</p>
      </div>

      {role === 'MAHASISWA' && <MahasiswaDashboard />}
      {role === 'DOSEN' && <DosenDashboard />}
      {role === 'ADMIN' && <AdminDashboard />}
    </div>
  )
}
