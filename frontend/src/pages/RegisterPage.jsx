import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { registerUser } from '../api'

const ROLES = ['MAHASISWA', 'DOSEN', 'ADMIN']

export default function RegisterPage() {
  const [form, setForm] = useState({
    name: '', email: '', password: '', role: 'MAHASISWA', nim: '', nip: '',
  })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  function update(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setSuccess('')
    setLoading(true)
    try {
      const payload = {
        name: form.name,
        email: form.email,
        password: form.password,
        role: form.role,
        nim: form.role === 'MAHASISWA' ? form.nim : null,
        nip: form.role !== 'MAHASISWA' ? form.nip : null,
      }
      await registerUser(payload)
      setSuccess('Registrasi berhasil! Silakan login.')
      setTimeout(() => navigate('/login'), 1500)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h2>Register</h2>
        <p className="auth-subtitle">Buat akun Agridesk baru</p>
        {error && <div className="alert alert-error">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}
        <form onSubmit={handleSubmit} className="form">
          <label>Nama Lengkap</label>
          <input value={form.name} onChange={(e) => update('name', e.target.value)} placeholder="Nama lengkap" required />

          <label>Email</label>
          <input type="email" value={form.email} onChange={(e) => update('email', e.target.value)} placeholder="email@example.com" required />

          <label>Password</label>
          <input type="password" value={form.password} onChange={(e) => update('password', e.target.value)} placeholder="Password" required />

          <label>Role</label>
          <select value={form.role} onChange={(e) => { update('role', e.target.value); update('nim', ''); update('nip', '') }}>
            {ROLES.map((r) => <option key={r} value={r}>{r}</option>)}
          </select>

          {form.role === 'MAHASISWA' ? (
            <>
              <label>NIM</label>
              <input value={form.nim} onChange={(e) => update('nim', e.target.value)} placeholder="Nomor Induk Mahasiswa" required />
            </>
          ) : (
            <>
              <label>NIP</label>
              <input value={form.nip} onChange={(e) => update('nip', e.target.value)} placeholder="Nomor Induk Pegawai" required />
            </>
          )}

          <button type="submit" disabled={loading}>
            {loading ? 'Loading...' : 'Register'}
          </button>
        </form>
        <p className="auth-footer">
          Sudah punya akun? <Link to="/login">Login</Link>
        </p>
      </div>
    </div>
  )
}
