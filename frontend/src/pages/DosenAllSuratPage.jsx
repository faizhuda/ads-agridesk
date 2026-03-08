import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../api';

const STATUS_STYLE = {
  MENUNGGU_TTD: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  SUDAH_TTD: 'bg-green-100 text-green-800 border-green-200',
  DITOLAK: 'bg-red-100 text-red-800 border-red-200',
};

export default function DosenAllSuratPage() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [sortBy, setSortBy] = useState('surat_desc');

  const resetFilters = () => {
    setSearch('');
    setStatusFilter('ALL');
    setSortBy('surat_desc');
  };

  useEffect(() => {
    setLoading(true);
    Promise.all([
      api.get('/api/signatures/pending'),
      api.get('/api/signatures/signed'),
    ])
      .then(([pendingRes, signedRes]) => {
        const pendingRows = (pendingRes.data || []).map((sig) => ({
          ...sig,
          statusLabel: 'MENUNGGU_TTD',
        }));
        const signedRows = (signedRes.data || []).map((sig) => ({
          ...sig,
          statusLabel: sig.signed_at ? 'SUDAH_TTD' : 'DITOLAK',
        }));

        const merged = [...pendingRows, ...signedRows];
        const uniqueBySignature = Array.from(new Map(merged.map((item) => [item.id, item])).values());

        uniqueBySignature.sort((a, b) => {
          const aTime = a.signed_at ? new Date(a.signed_at).getTime() : 0;
          const bTime = b.signed_at ? new Date(b.signed_at).getTime() : 0;
          if (aTime !== bTime) return bTime - aTime;
          return b.id - a.id;
        });

        setRows(uniqueBySignature);
      })
      .finally(() => setLoading(false));
  }, []);

  const summary = useMemo(() => {
    return {
      pending: rows.filter((r) => r.statusLabel === 'MENUNGGU_TTD').length,
      signed: rows.filter((r) => r.statusLabel === 'SUDAH_TTD').length,
      rejected: rows.filter((r) => r.statusLabel === 'DITOLAK').length,
    };
  }, [rows]);

  const visibleRows = useMemo(() => {
    const keyword = search.trim().toLowerCase();
    let items = [...rows];

    if (statusFilter !== 'ALL') {
      items = items.filter((item) => item.statusLabel === statusFilter);
    }

    if (keyword) {
      items = items.filter((item) => {
        const haystack = [item.surat_jenis, item.mahasiswa_name, String(item.surat_id)]
          .filter(Boolean)
          .join(' ')
          .toLowerCase();
        return haystack.includes(keyword);
      });
    }

    items.sort((a, b) => {
      if (sortBy === 'surat_asc') return Number(a.surat_id || 0) - Number(b.surat_id || 0);
      if (sortBy === 'jenis_asc') return String(a.surat_jenis || '').localeCompare(String(b.surat_jenis || ''), 'id');
      if (sortBy === 'status_asc') return String(a.statusLabel || '').localeCompare(String(b.statusLabel || ''), 'id');
      return Number(b.surat_id || 0) - Number(a.surat_id || 0);
    });

    return items;
  }, [rows, search, statusFilter, sortBy]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-4 border-b border-gray-200 gap-3">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 border-l-4 border-blue-500 pl-3">Semua Surat Dosen</h2>
          <p className="mt-1 text-sm text-gray-500 pl-3">Rekap seluruh surat yang pernah menjadi tugas Anda.</p>
        </div>
        <Link to="/dashboard/dosen" className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 transition-colors">
          Kembali ke Pending
        </Link>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white border border-gray-100 rounded-lg p-4">
          <div className="text-xs text-gray-500 uppercase tracking-wide">Menunggu TTD</div>
          <div className="text-2xl font-bold text-yellow-700 mt-1">{summary.pending}</div>
        </div>
        <div className="bg-white border border-gray-100 rounded-lg p-4">
          <div className="text-xs text-gray-500 uppercase tracking-wide">Sudah TTD</div>
          <div className="text-2xl font-bold text-green-700 mt-1">{summary.signed}</div>
        </div>
        <div className="bg-white border border-gray-100 rounded-lg p-4">
          <div className="text-xs text-gray-500 uppercase tracking-wide">Ditolak</div>
          <div className="text-2xl font-bold text-red-700 mt-1">{summary.rejected}</div>
        </div>
      </div>

      <div className="bg-white rounded-lg border border-gray-100 p-4 grid grid-cols-1 md:grid-cols-4 gap-3">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Cari jenis surat, mahasiswa, ID surat..."
          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="ALL">Semua Status</option>
          <option value="MENUNGGU_TTD">Menunggu TTD</option>
          <option value="SUDAH_TTD">Sudah TTD</option>
          <option value="DITOLAK">Ditolak</option>
        </select>
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="surat_desc">Urutkan: ID Surat Terbaru</option>
          <option value="surat_asc">Urutkan: ID Surat Terlama</option>
          <option value="jenis_asc">Urutkan: Jenis (A-Z)</option>
          <option value="status_asc">Urutkan: Status</option>
        </select>
        <button
          type="button"
          onClick={resetFilters}
          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors"
        >
          Reset Filter
        </button>
      </div>

      <div className="bg-white shadow-sm border border-gray-100 rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Surat</th>
                <th className="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Mahasiswa</th>
                <th className="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Waktu</th>
                <th className="px-6 py-3 text-right text-xs font-bold text-gray-500 uppercase tracking-wider">Aksi</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {visibleRows.length === 0 ? (
                <tr>
                  <td colSpan="5" className="px-6 py-10 text-center text-sm text-gray-500">Tidak ada data yang cocok dengan filter.</td>
                </tr>
              ) : visibleRows.map((sig) => (
                <tr key={sig.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{sig.surat_jenis || '-'}</div>
                    <div className="text-xs text-gray-500">ID Surat: #{sig.surat_id}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{sig.mahasiswa_name || '-'}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2.5 py-1 inline-flex text-xs leading-5 font-semibold rounded-full border ${STATUS_STYLE[sig.statusLabel]}`}>
                      {sig.statusLabel === 'MENUNGGU_TTD' ? 'Menunggu TTD' : sig.statusLabel === 'SUDAH_TTD' ? 'Sudah TTD' : 'Ditolak'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {sig.signed_at ? new Date(sig.signed_at).toLocaleString('id-ID') : (sig.statusLabel === 'DITOLAK' ? 'Ditolak' : '-')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex justify-end space-x-2">
                      <Link to={`/surat/${sig.surat_id}/pdf`} className="text-blue-600 hover:text-blue-900 bg-blue-50 hover:bg-blue-100 px-3 py-1.5 rounded transition-colors">PDF</Link>
                      <Link to={`/surat/${sig.surat_id}`} className="text-gray-600 hover:text-gray-900 bg-gray-100 hover:bg-gray-200 px-3 py-1.5 rounded transition-colors">Detail</Link>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
