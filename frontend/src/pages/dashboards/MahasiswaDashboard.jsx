import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { listMySurat } from '../../api'
import { useAuth } from '../../context/AuthContext'
import StatusBadge from '../../components/StatusBadge'

export default function MahasiswaDashboard() {
  const { token } = useAuth()
  const [suratList, setSuratList] = useState([])
  const [loading, setLoading] = useState(true)
  const [expanded, setExpanded] = useState(null)

  useEffect(() => {
    loadSurat()
  }, [])

  async function loadSurat() {
    setLoading(true)
    try {
      const data = await listMySurat(token)
      setSuratList(data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div className="section-header">
        <h2>Surat Saya</h2>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button onClick={loadSurat} className="btn btn-secondary">Refresh</button>
          <Link to="/ajukan" className="btn btn-primary">+ Ajukan Surat Baru</Link>
        </div>
      </div>

      {loading ? (
        <p>Loading...</p>
      ) : suratList.length === 0 ? (
        <div className="empty-state">
          <p>Belum ada surat. Silakan ajukan surat baru.</p>
        </div>
      ) : (
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Jenis</th>
                <th>Tipe</th>
                <th>Keperluan</th>
                <th>Status</th>
                <th>Signatures</th>
                <th>Hash</th>
              </tr>
            </thead>
            <tbody>
              {suratList.map((s) => (
                <>
                  <tr key={s.surat_id} onClick={() => setExpanded(expanded === s.surat_id ? null : s.surat_id)} style={{ cursor: 'pointer' }}>
                    <td>{s.surat_id}</td>
                    <td>{s.jenis}</td>
                    <td>{s.is_external ? 'Eksternal' : 'Internal'}</td>
                    <td>{s.keperluan || '-'}</td>
                    <td><StatusBadge status={s.status} /></td>
                    <td>
                      {s.signatures && s.signatures.length > 0
                        ? s.signatures.map((sig) => (
                            <span key={sig.signature_id} className={`sig-chip ${sig.signed ? 'sig-signed' : 'sig-pending'}`}>
                              {sig.owner_name} {sig.signed ? '✓' : '…'}
                            </span>
                          ))
                        : '-'}
                    </td>
                    <td className="hash-cell">{s.document_hash ? s.document_hash.substring(0, 16) + '...' : '-'}</td>
                  </tr>
                  {expanded === s.surat_id && (
                    <tr key={`${s.surat_id}-detail`}>
                      <td colSpan={7}>
                        <div className="detail-row">
                          {s.rejection_reason && (
                            <div className="alert alert-error" style={{ marginBottom: '8px' }}>
                              <strong>Alasan Penolakan:</strong> {s.rejection_reason}
                            </div>
                          )}
                          {s.created_at && <p className="text-muted" style={{ fontSize: '13px' }}>Dibuat: {new Date(s.created_at).toLocaleString('id-ID')}</p>}
                          {s.document_hash && <p style={{ fontSize: '13px' }}>Hash: <code>{s.document_hash}</code></p>}
                        </div>
                      </td>
                    </tr>
                  )}
                </>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
