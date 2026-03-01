import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
  const { isLoggedIn, role, name, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <nav className="navbar">
      <Link to="/" className="nav-brand">Agridesk</Link>
      <div className="nav-links">
        {!isLoggedIn ? (
          <>
            <Link to="/login">Login</Link>
            <Link to="/register">Register</Link>
          </>
        ) : (
          <>
            <Link to="/dashboard">Dashboard</Link>
            {role === 'MAHASISWA' && <Link to="/ajukan">Ajukan Surat</Link>}
            <Link to="/verify">Verifikasi</Link>
            <span className="nav-user">{name} ({role})</span>
            <button onClick={handleLogout} className="btn-logout">Logout</button>
          </>
        )}
        {!isLoggedIn && <Link to="/verify">Verifikasi</Link>}
      </div>
    </nav>
  )
}
