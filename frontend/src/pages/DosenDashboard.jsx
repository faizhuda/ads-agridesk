import { useState, useEffect, useMemo } from 'react';
import { Link } from 'react-router-dom';
import api from '../api';

export default function DosenDashboard() {
  const [pending, setPending] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState('surat_desc');

  const resetFilters = () => {
    setSearch('');
    setSortBy('surat_desc');
  };

  const load = () => {
    setLoading(true);
    api.get('/api/signatures/pending')
      .then((pendingRes) => {
        setPending(pendingRes.data || []);
      })
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const visiblePending = useMemo(() => {
    const keyword = search.trim().toLowerCase();
    let items = [...pending];

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
      return Number(b.surat_id || 0) - Number(a.surat_id || 0);
    });

    return items;
  }, [pending, search, sortBy]);

  const handleSign = async (signatureId) => {
    try {
      const form = new FormData();
      await api.post('/api/signatures/lecturer/' + signatureId + '/sign', form);
      load();
    } catch (err) {
      const message = err.response?.data?.detail || 'Gagal menandatangani';
      if (String(message).toLowerCase().includes('belum disimpan')) {
        alert('Simpan dulu tanda tangan Anda di menu Tanda Tangan Saya');
        return;
      }
      alert(message);
    }
  };

  const handleReject = async (suratId) => {
    const reason = prompt('Alasan penolakan:');
    if (!reason || !reason.trim()) return;
    try {
      await api.post('/api/surat/' + suratId + '/reject', { reason: reason.trim() });
      load();
    } catch (err) {
      alert(err.response?.data?.detail || 'Gagal menolak surat');
    }
  };

  if (loading) return (
    <div className="flex justify-center items-center h-64">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>
  );

  return (
    <div className="space-y-12">
      <section>
        <div className="pb-4 border-b border-gray-200 mb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 border-l-4 border-yellow-400 pl-3">Tanda Tangan Pending</h2>
            <p className="mt-1 text-sm text-gray-500 pl-3">Surat yang membutuhkan tanda tangan Anda segera.</p>
          </div>
          <Link to="/surat/all-dosen" className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 transition-colors">
            Lihat Semua Surat
          </Link>
        </div>

        <div className="bg-white rounded-lg border border-gray-100 p-4 grid grid-cols-1 md:grid-cols-3 gap-3 mb-6">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Cari jenis surat, mahasiswa, ID surat..."
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="surat_desc">Urutkan: ID Surat Terbaru</option>
            <option value="surat_asc">Urutkan: ID Surat Terlama</option>
            <option value="jenis_asc">Urutkan: Jenis (A-Z)</option>
          </select>
          <button
            type="button"
            onClick={resetFilters}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors"
          >
            Reset Filter
          </button>
        </div>
        
        {pending.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-10 text-center">
            <svg className="mx-auto h-12 w-12 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">Semua Beres!</h3>
            <p className="mt-1 text-sm text-gray-500">Tidak ada tanda tangan yang menunggu saat ini.</p>
          </div>
        ) : (
          <div className="bg-white shadow-sm border border-gray-100 rounded-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Surat</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Mahasiswa</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Status</th>
                    <th scope="col" className="px-6 py-3 text-right text-xs font-bold text-gray-500 uppercase tracking-wider">Aksi</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {visiblePending.length === 0 ? (
                    <tr>
                      <td colSpan="4" className="px-6 py-10 text-center text-gray-500">Tidak ada data yang cocok dengan filter.</td>
                    </tr>
                  ) : visiblePending.map((sig) => (
                    <tr key={sig.id} className="hover:bg-yellow-50/50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{sig.surat_jenis || '-'}</div>
                        <div className="text-xs text-gray-500">ID Surat: #{sig.surat_id}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{sig.mahasiswa_name || '-'}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2.5 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800 border border-yellow-200">
                          Menunggu TTD
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex justify-end space-x-2">
                          <Link to={`/surat/${sig.surat_id}/pdf`} className="text-blue-600 hover:text-blue-900 bg-blue-50 hover:bg-blue-100 px-3 py-1.5 rounded transition-colors hidden sm:inline-block">PDF</Link>
                          <Link to={`/surat/${sig.surat_id}`} className="text-gray-600 hover:text-gray-900 bg-gray-100 hover:bg-gray-200 px-3 py-1.5 rounded transition-colors">Detail</Link>
                          <button className="text-white bg-green-600 hover:bg-green-700 px-3 py-1.5 rounded shadow-sm transition-colors" onClick={() => handleSign(sig.id)}>TTD</button>
                          <button className="text-white bg-red-600 hover:bg-red-700 px-3 py-1.5 rounded shadow-sm transition-colors" onClick={() => handleReject(sig.surat_id)}>Tolak</button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </section>
    </div>
  );
}
