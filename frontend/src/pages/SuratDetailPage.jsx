import { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
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

const FIELD_LABELS = {
  keperluan_surat_aktif: 'Keperluan Surat Aktif',
  mata_kuliah_yang_dibatalkan: 'Mata Kuliah yang Dibatalkan',
  alasan_pembatalan_kuliah: 'Alasan Pembatalan Kuliah',
};

export default function SuratDetailPage() {
  const { id } = useParams();
  const { user } = useAuth();
  const [surat, setSurat] = useState(null);
  const [signatures, setSignatures] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = async () => {
    try {
      const [suratRes, sigRes] = await Promise.all([
        api.get('/api/surat/' + id),
        api.get('/api/signatures/surat/' + id),
      ]);
      setSurat(suratRes.data);
      setSignatures(sigRes.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Gagal memuat data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [id]);

  const handleSubmit = async () => {
    try {
      await api.post('/api/surat/' + id + '/submit');
      load();
    } catch (err) {
      alert(err.response?.data?.detail || 'Gagal submit');
    }
  };

  const handleStudentSign = async () => {
    try {
      const form = new FormData();
      await api.post('/api/signatures/student/' + id, form);
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

  if (loading) return (
    <div className="flex justify-center items-center h-64">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>
  );

  if (error) return (
    <div className="max-w-3xl mx-auto mt-8">
      <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-md">
        <p className="text-sm font-medium text-red-700">{error}</p>
      </div>
    </div>
  );

  if (!surat) return (
    <div className="max-w-3xl mx-auto mt-8 text-center bg-white p-8 rounded-lg shadow-sm border border-gray-100">
      <p className="text-gray-500 font-medium">Surat tidak ditemukan.</p>
    </div>
  );

  const internalFields = surat.internal_fields || {};
  const internalFieldEntries = Object.entries(internalFields).filter(([, value]) => String(value || '').trim());

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="p-6 sm:p-8 border-b border-gray-100 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-gray-50">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 flex items-center">
              <svg className="w-6 h-6 mr-2 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
              Detail Surat #{surat.id}
            </h2>
            <p className="text-sm text-gray-500 mt-1 pl-8">Informasi lengkap dan status dokumen.</p>
          </div>
          <span className={`px-3 py-1 inline-flex text-sm leading-5 font-semibold rounded-full border ${STATUS_COLORS[surat.status] || 'bg-gray-100 text-gray-800 border-gray-200'}`}>
            {STATUS_LABEL[surat.status]}
          </span>
        </div>

        <div className="p-6 sm:p-8">
          <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
            <div className="sm:col-span-1">
              <dt className="text-sm font-medium text-gray-500">Jenis Surat</dt>
              <dd className="mt-1 text-sm text-gray-900 font-semibold">{surat.jenis}</dd>
            </div>
            <div className="sm:col-span-1">
              <dt className="text-sm font-medium text-gray-500">Tipe Dokumen</dt>
              <dd className="mt-1 text-sm text-gray-900">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium bg-blue-50 text-blue-800 border border-blue-200">
                  {surat.is_external ? 'Eksternal (PDF)' : 'Internal (Template)'}
                </span>
              </dd>
            </div>
            <div className="sm:col-span-1">
              <dt className="text-sm font-medium text-gray-500">Nama Mahasiswa</dt>
              <dd className="mt-1 text-sm text-gray-900 font-semibold">{surat.mahasiswa_name || '-'}</dd>
            </div>
            <div className="sm:col-span-1">
              <dt className="text-sm font-medium text-gray-500">NIM</dt>
              <dd className="mt-1 text-sm text-gray-900">{surat.mahasiswa_nim || '-'}</dd>
            </div>
            <div className="sm:col-span-2">
              <dt className="text-sm font-medium text-gray-500">Keperluan</dt>
              <dd className="mt-1 text-sm text-gray-900">{surat.keperluan}</dd>
            </div>

            {internalFieldEntries.length > 0 && (
              <div className="sm:col-span-2 bg-blue-50 p-4 rounded-md border border-blue-100">
                <dt className="text-sm font-semibold text-blue-900 mb-3">Detail Form Pengajuan</dt>
                <dd className="space-y-3">
                  {internalFieldEntries.map(([key, value]) => (
                    <div key={key}>
                      <div className="text-xs uppercase tracking-wide text-blue-700 font-semibold">
                        {FIELD_LABELS[key] || key.replace(/_/g, ' ')}
                      </div>
                      <div className="text-sm text-blue-900">{value}</div>
                    </div>
                  ))}
                </dd>
              </div>
            )}

            {!surat.is_external && internalFieldEntries.length === 0 && (
              <div className="sm:col-span-2 bg-amber-50 p-4 rounded-md border border-amber-100">
                <dt className="text-sm font-semibold text-amber-900 mb-1">Detail Form Pengajuan</dt>
                <dd className="text-sm text-amber-800">
                  Detail input form belum tersedia untuk surat ini (kemungkinan dibuat sebelum pembaruan sistem).
                </dd>
              </div>
            )}
            
            {surat.rejection_reason && (
              <div className="sm:col-span-2 bg-red-50 p-4 rounded-md border border-red-100">
                <dt className="text-sm font-medium text-red-800 wrap-anywhere mb-1">Alasan Penolakan:</dt>
                <dd className="text-sm text-red-700 italic">"{surat.rejection_reason}"</dd>
              </div>
            )}
            
            {surat.document_hash && (
              <div className="sm:col-span-2">
                <dt className="text-sm font-medium text-gray-500">Document Hash (Digital Signature Verification)</dt>
                <dd className="mt-1 text-xs text-gray-600 bg-gray-100 p-2 rounded border border-gray-200 break-all font-mono">
                  {surat.document_hash}
                </dd>
              </div>
            )}
          </dl>

          <div className="mt-8 pt-6 border-t border-gray-200 flex flex-wrap gap-3">
            <Link to={`/surat/${surat.id}/pdf`} className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors">
              <svg className="-ml-1 mr-2 h-4 w-4 text-gray-500" fill="currentColor" viewBox="0 0 20 20"><path d="M9 2a2 2 0 00-2 2v8a2 2 0 002 2h6a2 2 0 002-2V6.414A2 2 0 0016.414 5L14 2.586A2 2 0 0012.586 2H9z" /><path d="M3 8a2 2 0 012-2v10h8a2 2 0 01-2 2H5a2 2 0 01-2-2V8z" /></svg>
              Lihat PDF
            </Link>

            {user.role === 'MAHASISWA' && surat.status === 'DRAFT' && (
              <>
                <button type="button" onClick={handleStudentSign} className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors">
                  <svg className="-ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" /></svg>
                  Tandatangani (Profil TTD)
                </button>
                <button type="button" onClick={handleSubmit} className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors">
                  <svg className="-ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                  Submit Surat
                </button>
              </>
            )}
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="p-6 border-b border-gray-100 bg-gray-50">
          <h3 className="text-lg font-bold text-gray-900">Progres Tanda Tangan</h3>
        </div>
        
        {signatures.length === 0 ? (
          <div className="p-6 text-center text-sm text-gray-500">
            Belum ada permintaan tanda tangan untuk dokumen ini.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-white">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Pihak</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Status</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Waktu TTD</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {signatures.map((sig) => (
                  <tr key={sig.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {sig.role === 'DOSEN' ? (sig.owner_name || 'Dosen') : sig.role}
                      </div>
                      <div className="text-xs text-gray-500">
                        {sig.role === 'DOSEN'
                          ? (sig.owner_nip ? `NIP: ${sig.owner_nip}` : 'NIP: -')
                          : `ID: ${sig.id}`}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {sig.signed_at ? (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          <svg className="mr-1 h-3 w-3 text-green-600" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" /></svg>
                          Sudah TTD
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                          <svg className="mr-1 h-3 w-3 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                          Menunggu
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 font-mono">
                      {sig.signed_at ? new Date(sig.signed_at).toLocaleString('id-ID') : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
