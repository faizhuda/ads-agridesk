import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { createSurat, uploadSuratEksternal, listDosenUsers } from '../api'
import { useAuth } from '../context/AuthContext'

const JENIS_OPTIONS = [
  'Surat Aktif Kuliah',
  'Surat Keterangan',
  'Surat Pengantar',
  'Surat Izin Penelitian',
  'Surat Rekomendasi',
  'Lainnya',
]

export default function AjukanSuratPage() {
  const { token } = useAuth()
  const navigate = useNavigate()
  const [mode, setMode] = useState('internal')
  const [jenis, setJenis] = useState(JENIS_OPTIONS[0])
  const [keperluan, setKeperluan] = useState('')
  const [file, setFile] = useState(null)

  // Dosen selection
  const [requiresDosen, setRequiresDosen] = useState(true)
  const [dosenList, setDosenList] = useState([])
  const [selectedDosen, setSelectedDosen] = useState([])

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    listDosenUsers(token)
      .then(setDosenList)
      .catch((err) => console.error('Failed to load dosen list', err))
  }, [token])

  function toggleDosen(id) {
    setSelectedDosen((prev) =>
      prev.includes(id) ? prev.filter((d) => d !== id) : [...prev, id]
    )
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setSuccess('')
    setLoading(true)
    try {
      let result
      if (mode === 'internal') {
        const payload = {
          jenis,
          keperluan: keperluan || null,
          is_external: false,
          dosen_ids: requiresDosen && selectedDosen.length > 0 ? selectedDosen : null,
        }
        if (requiresDosen && selectedDosen.length === 0) {
          setError('Pilih minimal satu dosen untuk tanda tangan')
          setLoading(false)
          return
        }
        result = await createSurat(token, payload)
      } else {
        if (!file) {
          setError('Pilih file PDF untuk di-upload')
          setLoading(false)
          return
        }
        result = await uploadSuratEksternal(token, jenis, keperluan || null, file)
      }
      setSuccess(`Surat berhasil diajukan! ID: ${result.surat_id}`)
      setTimeout(() => navigate('/dashboard'), 2000)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <h1>Ajukan Surat</h1>
      <p>Pilih tipe surat dan isi informasi yang diperlukan.</p>

      <div className="tab-group">
        <button className={`tab ${mode === 'internal' ? 'tab-active' : ''}`} onClick={() => setMode('internal')}>
          Surat Internal (Generate)
        </button>
        <button className={`tab ${mode === 'external' ? 'tab-active' : ''}`} onClick={() => setMode('external')}>
          Surat Eksternal (Upload)
        </button>
      </div>

      <div className="card" style={{ marginTop: '16px' }}>
        {error && <div className="alert alert-error">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}

        <form onSubmit={handleSubmit} className="form">
          <label>Jenis Surat</label>
          <select value={jenis} onChange={(e) => setJenis(e.target.value)}>
            {JENIS_OPTIONS.map((j) => <option key={j} value={j}>{j}</option>)}
          </select>

          <label>Keperluan</label>
          <textarea
            value={keperluan}
            onChange={(e) => setKeperluan(e.target.value)}
            placeholder="Keperluan pengajuan (opsional)"
            rows={3}
          />

          {mode === 'internal' && (
            <>
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={requiresDosen}
                  onChange={(e) => {
                    setRequiresDosen(e.target.checked)
                    if (!e.target.checked) setSelectedDosen([])
                  }}
                />
                Butuh tanda tangan dosen?
              </label>

              {requiresDosen && (
                <div className="dosen-select-box">
                  <label>Pilih Dosen (bisa lebih dari satu)</label>
                  {dosenList.length === 0 ? (
                    <p className="text-muted">Tidak ada dosen terdaftar.</p>
                  ) : (
                    <div className="dosen-list">
                      {dosenList.map((d) => (
                        <label key={d.user_id} className={`dosen-item ${selectedDosen.includes(d.user_id) ? 'selected' : ''}`}>
                          <input
                            type="checkbox"
                            checked={selectedDosen.includes(d.user_id)}
                            onChange={() => toggleDosen(d.user_id)}
                          />
                          <div>
                            <strong>{d.name}</strong>
                            <span className="text-muted"> — {d.email}</span>
                            {d.nip && <span className="text-muted"> (NIP: {d.nip})</span>}
                          </div>
                        </label>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </>
          )}

          {mode === 'external' && (
            <>
              <label>Upload File (PDF)</label>
              <input type="file" accept=".pdf" onChange={(e) => setFile(e.target.files?.[0] || null)} />
            </>
          )}

          <div className="info-box">
            {mode === 'internal' ? (
              requiresDosen ? (
                <p>Surat akan melalui tahap tanda tangan{selectedDosen.length > 0 ? ` ${selectedDosen.length} dosen` : ''} sebelum diproses admin.</p>
              ) : (
                <p>Surat akan langsung dikirim ke admin tanpa tanda tangan dosen.</p>
              )
            ) : (
              <p>Surat dari luar sistem akan masuk ke alur persetujuan Dosen dan Admin.</p>
            )}
          </div>

          <button type="submit" disabled={loading}>
            {loading ? 'Mengajukan...' : 'Ajukan Surat'}
          </button>
        </form>
      </div>
    </div>
  )
}
