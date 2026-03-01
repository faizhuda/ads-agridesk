import { useEffect, useState } from 'react'
import { listPendingAdmin, listHistoryAdmin, approveSurat, rejectSurat } from '../../api'
import { useAuth } from '../../context/AuthContext'
import StatusBadge from '../../components/StatusBadge'

export default function AdminDashboard() {
  const { token } = useAuth()
  const [tab, setTab] = useState('pending')
  const [suratList, setSuratList] = useState([])
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(null)
  const [message, setMessage] = useState('')
  const [rejectModal, setRejectModal] = useState({ open: false, suratId: null, reason: '' })

  useEffect(() => { loadSurat() }, [tab])

  async function loadSurat() {
    setLoading(true)
    try {
      const data = tab === 'pending'
        ? await listPendingAdmin(token)
        : await listHistoryAdmin(token)
      setSuratList(data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  async function handleApprove(suratId) {
    setActionLoading(suratId)
    setMessage('')
    try {
      const result = await approveSurat(token, suratId)
      setMessage(`Surat #${suratId} disetujui. Hash: ${result.document_hash}`)
      loadSurat()
    } catch (err) {
      setMessage(`Error: ${err.message}`)
    } finally {
      setActionLoading(null)
    }
  }

  function openRejectModal(suratId) {
    setRejectModal({ open: true, suratId, reason: '' })
  }

  async function handleReject() {
    const { suratId, reason } = rejectModal
    if (!reason.trim()) return
    setActionLoading(suratId)
    setMessage('')
    try {
      await rejectSurat(token, suratId, reason)
      setMessage(`Surat #${suratId} ditolak.`)
      setRejectModal({ open: false, suratId: null, reason: '' })
      loadSurat()
    } catch (err) {
      setMessage(`Error: ${err.message}`)
    } finally {
      setActionLoading(null)
    }
  }

  return (
    <div>
      <div className="section-header">
        <h2>{tab === 'pending' ? 'Menunggu Persetujuan Admin' : 'Semua Surat'}</h2>
        <div style={{ display: 'flex', gap: '8px' }}>
          <div className="tab-group">
            <button className={`tab ${tab === 'pending' ? 'tab-active' : ''}`} onClick={() => setTab('pending')}>Pending</button>
            <button className={`tab ${tab === 'history' ? 'tab-active' : ''}`} onClick={() => setTab('history')}>Semua</button>
          </div>
          <button onClick={loadSurat} className="btn btn-secondary">Refresh</button>
        </div>
      </div>

      {message && <div className="alert alert-info">{message}</div>}

      {loading ? (
        <p>Loading...</p>
      ) : suratList.length === 0 ? (
        <div className="empty-state">
          <p>{tab === 'pending' ? 'Tidak ada surat yang menunggu persetujuan.' : 'Belum ada surat.'}</p>
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
                {tab === 'pending' && <th>Aksi</th>}
              </tr>
            </thead>
            <tbody>
              {suratList.map((s) => (
                <tr key={s.surat_id}>
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
                  {tab === 'pending' && (
                    <td className="action-cell">
                      <button
                        className="btn btn-primary btn-sm"
                        onClick={() => handleApprove(s.surat_id)}
                        disabled={actionLoading === s.surat_id}
                      >
                        Approve
                      </button>
                      <button
                        className="btn btn-danger btn-sm"
                        onClick={() => openRejectModal(s.surat_id)}
                        disabled={actionLoading === s.surat_id}
                      >
                        Reject
                      </button>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Reject Modal */}
      {rejectModal.open && (
        <div className="modal-overlay" onClick={() => setRejectModal({ open: false, suratId: null, reason: '' })}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Tolak Surat #{rejectModal.suratId}</h3>
            <label>Alasan Penolakan</label>
            <textarea
              value={rejectModal.reason}
              onChange={(e) => setRejectModal((prev) => ({ ...prev, reason: e.target.value }))}
              placeholder="Masukkan alasan penolakan..."
              rows={4}
            />
            <div className="modal-actions">
              <button className="btn btn-secondary" onClick={() => setRejectModal({ open: false, suratId: null, reason: '' })}>
                Batal
              </button>
              <button className="btn btn-danger" onClick={handleReject} disabled={!rejectModal.reason.trim()}>
                Tolak Surat
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
