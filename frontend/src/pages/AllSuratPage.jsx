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

const STATUS_COLORS = {
  DRAFT: 'bg-gray-100 text-gray-800 border-gray-200',
  MENUNGGU_TTD_DOSEN: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  MENUNGGU_PROSES_ADMIN: 'bg-blue-100 text-blue-800 border-blue-200',
  SELESAI: 'bg-green-100 text-green-800 border-green-200',
  DITOLAK: 'bg-red-100 text-red-800 border-red-200',
};

export default function AllSuratPage() {
  const [letters, setLetters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [sortBy, setSortBy] = useState('id_desc');

  const resetFilters = () => {
    setSearch('');
    setStatusFilter('ALL');
    setSortBy('id_desc');
  };

  useEffect(() => {
    api.get('/api/surat/all').then((res) => setLetters(res.data)).finally(() => setLoading(false));
  }, []);

  const visibleLetters = useMemo(() => {
    const keyword = search.trim().toLowerCase();
    let items = [...letters];

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
      if (sortBy === 'status_asc') return String(STATUS_LABEL[a.status] || a.status).localeCompare(String(STATUS_LABEL[b.status] || b.status), 'id');
      return b.id - a.id;
    });

    return items;
  }, [letters, search, statusFilter, sortBy]);

  const summary = useMemo(() => {
    return {
      pending: letters.filter((item) => item.status === 'MENUNGGU_TTD_DOSEN' || item.status === 'MENUNGGU_PROSES_ADMIN').length,
      done: letters.filter((item) => item.status === 'SELESAI').length,
      rejected: letters.filter((item) => item.status === 'DITOLAK').length,
    };
  }, [letters]);

  if (loading) return (
    <div className="flex justify-center items-center h-64">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-4 border-b border-gray-200 gap-3">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 border-l-4 border-gray-700 pl-3">Semua Surat</h2>
          <p className="mt-1 text-sm text-gray-500 pl-3">Daftar seluruh surat yang diajukan dalam sistem.</p>
        </div>
        <Link to="/dashboard/admin" className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 transition-colors">
          Kembali ke Pending
        </Link>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white border border-gray-100 rounded-lg p-4">
          <div className="text-xs text-gray-500 uppercase tracking-wide">Menunggu</div>
          <div className="text-2xl font-bold text-yellow-700 mt-1">{summary.pending}</div>
        </div>
        <div className="bg-white border border-gray-100 rounded-lg p-4">
          <div className="text-xs text-gray-500 uppercase tracking-wide">Selesai</div>
          <div className="text-2xl font-bold text-green-700 mt-1">{summary.done}</div>
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
          placeholder="Cari jenis, keperluan, NIM, ID..."
          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="ALL">Semua Status</option>
          {Object.keys(STATUS_LABEL).filter((status) => status !== 'DRAFT').map((status) => (
            <option key={status} value={status}>{STATUS_LABEL[status]}</option>
          ))}
        </select>
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="id_desc">Urutkan: ID Terbaru</option>
          <option value="id_asc">Urutkan: ID Terlama</option>
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
                <th scope="col" className="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Surat</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Mahasiswa</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Status</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Waktu Update</th>
                <th scope="col" className="px-6 py-3 text-right text-xs font-bold text-gray-500 uppercase tracking-wider">Aksi</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {visibleLetters.length === 0 ? (
                <tr>
                  <td colSpan="5" className="px-6 py-10 text-center text-gray-500">Tidak ada data yang cocok dengan filter.</td>
                </tr>
              ) : visibleLetters.map((s) => (
                <tr key={s.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{s.jenis}</div>
                    <div className="text-xs text-gray-500">ID Surat: #{s.id}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{s.mahasiswa_name || '-'} ({s.mahasiswa_nim || '-'})</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2.5 py-1 inline-flex text-xs leading-5 font-semibold rounded-full border ${STATUS_COLORS[s.status] || 'bg-gray-100 text-gray-800 border-gray-200'}`}>
                      {STATUS_LABEL[s.status]}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {s.updated_at ? new Date(s.updated_at).toLocaleString('id-ID') : '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex justify-end space-x-2">
                      <Link to={`/surat/${s.id}/pdf`} className="text-blue-600 hover:text-blue-900 bg-blue-50 hover:bg-blue-100 px-3 py-1.5 rounded transition-colors hidden sm:inline-block">PDF</Link>
                      <Link to={`/surat/${s.id}`} className="text-gray-600 hover:text-gray-900 bg-gray-100 hover:bg-gray-200 px-3 py-1.5 rounded transition-colors">Detail</Link>
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
