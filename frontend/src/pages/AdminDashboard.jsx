import { useState, useEffect, useMemo } from 'react';
import { Link } from 'react-router-dom';
import api from '../api';

const STATUS_LABEL = {
  DRAFT: 'Draft',
  MENUNGGU_TTD_DOSEN: 'Menunggu TTD Dosen',
  MENUNGGU_PROSES_ADMIN: 'Menunggu Proses Admin',
  SELESAI: 'Selesai',
  DITOLAK: 'Ditolak',
};

export default function AdminDashboard() {
  const [pending, setPending] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [sortBy, setSortBy] = useState('id_desc');

  const resetFilters = () => {
    setSearch('');
    setStatusFilter('ALL');
    setSortBy('id_desc');
  };

  const load = () => {
    api.get('/api/surat/pending').then((res) => setPending(res.data)).finally(() => setLoading(false));
  };

  useEffect(load, []);

  const visiblePending = useMemo(() => {
    const keyword = search.trim().toLowerCase();
    let items = [...pending];

    if (statusFilter !== 'ALL') {
      items = items.filter((item) => item.status === statusFilter);
    }

    if (keyword) {
      items = items.filter((item) => {
        const haystack = [item.jenis, item.keperluan, item.mahasiswa_nim, String(item.id)]
          .filter(Boolean)
          .join(' ')
          .toLowerCase();
        return haystack.includes(keyword);
      });
    }

    items.sort((a, b) => {
      if (sortBy === 'id_asc') return a.id - b.id;
      if (sortBy === 'jenis_asc') return String(a.jenis || '').localeCompare(String(b.jenis || ''), 'id');
      return b.id - a.id;
    });

    return items;
  }, [pending, search, statusFilter, sortBy]);

  const handleApprove = async (id) => {
    try {
      await api.post('/api/surat/' + id + '/approve');
      load();
    } catch (err) {
      alert(err.response?.data?.detail || 'Gagal menyetujui');
    }
  };

  const handleReject = async (id) => {
    const reason = prompt('Alasan penolakan:');
    if (!reason) return;
    try {
      await api.post('/api/surat/' + id + '/reject', { reason });
      load();
    } catch (err) {
      alert(err.response?.data?.detail || 'Gagal menolak');
    }
  };

  if (loading) return (
    <div className="flex justify-center items-center h-64">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-4 border-b border-gray-200">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 border-l-4 border-blue-600 pl-3">Pending Admin</h2>
          <p className="mt-1 text-sm text-gray-500 pl-3">Surat yang membutuhkan persetujuan Anda segera.</p>
        </div>
        <Link to="/surat/all" className="mt-4 sm:mt-0 inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors">
          Lihat Semua Surat
        </Link>
      </div>

      <div className="bg-white rounded-lg border border-gray-100 p-4 grid grid-cols-1 md:grid-cols-4 gap-3">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Cari jenis, keperluan, NIM, ID..."
          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="ALL">Semua Status</option>
          <option value="MENUNGGU_PROSES_ADMIN">Menunggu Proses Admin</option>
          <option value="MENUNGGU_TTD_DOSEN">Menunggu TTD Dosen</option>
        </select>
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="id_desc">Urutkan: ID Terbaru</option>
          <option value="id_asc">Urutkan: ID Terlama</option>
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
        <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-12 text-center">
          <svg className="mx-auto h-12 w-12 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M5 13l4 4L19 7" />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">Semua Beres!</h3>
          <p className="mt-1 text-sm text-gray-500">Tidak ada surat yang menunggu proses admin.</p>
        </div>
      ) : (
        <div className="bg-white shadow-sm border border-gray-100 rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">ID</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Jenis Surat</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Keperluan</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Status</th>
                  <th scope="col" className="px-6 py-3 text-right text-xs font-bold text-gray-500 uppercase tracking-wider">Aksi</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {visiblePending.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="px-6 py-10 text-center text-gray-500">Tidak ada data yang cocok dengan filter.</td>
                  </tr>
                ) : visiblePending.map((s) => (
                  <tr key={s.id} className="hover:bg-blue-50/50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">#{s.id}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{s.jenis}</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-500 max-w-xs truncate" title={s.keperluan}>{s.keperluan}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2.5 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800 border border-blue-200">
                        {STATUS_LABEL[s.status]}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex justify-end items-center space-x-2">
                        <Link to={`/surat/${s.id}/pdf`} className="text-blue-600 hover:text-blue-900 bg-blue-50 hover:bg-blue-100 px-3 py-1.5 rounded transition-colors hidden sm:inline-block">PDF</Link>
                        <button className="text-white bg-green-600 hover:bg-green-700 px-3 py-1.5 rounded shadow-sm transition-colors" onClick={() => handleApprove(s.id)}>Setujui</button>
                        <button className="text-white bg-red-600 hover:bg-red-700 px-3 py-1.5 rounded shadow-sm transition-colors" onClick={() => handleReject(s.id)}>Tolak</button>
                        <Link to={`/surat/${s.id}`} className="text-gray-600 hover:text-gray-900 bg-gray-100 hover:bg-gray-200 px-3 py-1.5 rounded transition-colors">Detail</Link>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
