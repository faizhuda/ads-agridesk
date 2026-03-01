import { useState } from 'react'
import { verifyDocument } from '../api'

export default function VerifyPage() {
  const [hash, setHash] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleVerify(e) {
    e.preventDefault()
    if (!hash.trim()) return
    setError('')
    setResult(null)
    setLoading(true)
    try {
      const data = await verifyDocument(hash.trim())
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <div className="verify-container">
        <h1>Verifikasi Dokumen</h1>
        <p>Masukkan document hash untuk memverifikasi keaslian surat.</p>

        <form onSubmit={handleVerify} className="form">
          <input
            type="text"
            value={hash}
            onChange={(e) => setHash(e.target.value)}
            placeholder="Masukkan document hash..."
          />
          <button type="submit" disabled={loading || !hash.trim()}>
            {loading ? 'Memverifikasi...' : 'Verifikasi'}
          </button>
        </form>

        {error && (
          <div className="verify-result verify-invalid">
            <h3>INVALID</h3>
            <p>{error}</p>
          </div>
        )}

        {result && (
          <div className="verify-result verify-valid">
            <h3>VALID</h3>
            <table className="detail-table">
              <tbody>
                <tr><td>Status</td><td>{result.status}</td></tr>
                <tr><td>Mahasiswa ID</td><td>{result.mahasiswa_id}</td></tr>
                <tr><td>Jenis Surat</td><td>{result.jenis}</td></tr>
                <tr><td>Document Hash</td><td className="hash-cell">{result.document_hash}</td></tr>
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
