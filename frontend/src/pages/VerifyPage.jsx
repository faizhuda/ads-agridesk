import { useState } from 'react';
import api from '../api';

export default function VerifyPage() {
  const [hash, setHash] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleVerify = async (e) => {
    e.preventDefault();
    if (!hash.trim()) return;
    
    setError('');
    setResult(null);
    setLoading(true);
    
    try {
      const res = await api.get('/verify/' + hash.trim());
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Gagal memverifikasi dokumen. Pastikan hash valid.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-[80vh] py-12 px-4 sm:px-6 lg:px-8 bg-gray-50">
      <div className="w-full max-w-lg space-y-8 bg-white p-8 sm:p-10 rounded-xl shadow-sm border border-gray-100">
        <div className="text-center">
          <div className="mx-auto h-16 w-16 bg-blue-100 rounded-full flex items-center justify-center mb-4 border border-blue-200">
            <svg className="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <h2 className="text-center text-3xl font-extrabold text-gray-900">
            Verifikasi Dokumen
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600 max-w">
            Masukkan Document Hash untuk memvalidasi keaslian tanda tangan digital.
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleVerify}>
          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <label htmlFor="hash" className="sr-only">Document Hash</label>
              <input
                id="hash"
                name="hash"
                type="text"
                required
                className="appearance-none rounded-md relative block w-full px-4 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-blue-600 focus:z-10 sm:text-sm transition-all shadow-sm"
                placeholder="Misal: a1b2c3d4..."
                value={hash}
                onChange={(e) => setHash(e.target.value)}
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading || !hash.trim()}
              className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors shadow-sm disabled:opacity-70 disabled:cursor-not-allowed"
            >
              {loading ? (
                <span className="flex items-center">
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Memverifikasi...
                </span>
              ) : (
                <span className="flex items-center">
                  <svg className="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                  Verifikasi Dokumen
                </span>
              )}
            </button>
          </div>
        </form>

        {error && (
          <div className="rounded-md bg-red-50 p-4 border border-red-100 animate-fade-in-up">
            <div className="flex">
              <div className="shrink-0">
                <svg className="h-5 w-5 text-red-500" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Verifikasi Gagal</h3>
                <div className="mt-2 text-sm text-red-700">
                  <p>{error}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {result && (
          <div
            className={`rounded-lg p-6 border animate-fade-in-up ${
              result.status === 'VALID'
                ? 'bg-green-50 border-green-200'
                : 'bg-red-50 border-red-200'
            }`}
          >
            <div className="flex items-center mb-4">
              <div
                className={`shrink-0 h-10 w-10 rounded-full flex items-center justify-center ${
                  result.status === 'VALID' ? 'bg-green-100' : 'bg-red-100'
                }`}
              >
                {result.status === 'VALID' ? (
                  <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                ) : (
                  <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                )}
              </div>
              <div className="ml-4">
                <h3
                  className={`text-lg font-bold ${
                    result.status === 'VALID' ? 'text-green-800' : 'text-red-800'
                  }`}
                >
                  Status: {result.status}
                </h3>
                <p
                  className={`text-sm ${
                    result.status === 'VALID' ? 'text-green-600' : 'text-red-600'
                  }`}
                >
                  {result.status === 'VALID' 
                    ? 'Dokumen asli dan tanda tangan tervalidasi.' 
                    : 'Dokumen tidak valid atau telah dimodifikasi.'}
                </p>
              </div>
            </div>

            {result.status === 'VALID' && (
              <div className="mt-4 pt-4 border-t border-green-200">
                <dl className="grid grid-cols-1 gap-x-4 gap-y-4 sm:grid-cols-2">
                  <div className="sm:col-span-1">
                    <dt className="text-xs font-medium text-green-800 uppercase tracking-wider">ID Surat</dt>
                    <dd className="mt-1 text-sm font-semibold text-green-900">#{result.surat_id}</dd>
                  </div>
                  <div className="sm:col-span-1">
                    <dt className="text-xs font-medium text-green-800 uppercase tracking-wider">Jenis Surat</dt>
                    <dd className="mt-1 text-sm font-semibold text-green-900">{result.jenis}</dd>
                  </div>
                  <div className="sm:col-span-2">
                    <dt className="text-xs font-medium text-green-800 uppercase tracking-wider">Keperluan</dt>
                    <dd className="mt-1 text-sm text-green-900 bg-green-100/50 p-3 rounded">{result.keperluan}</dd>
                  </div>
                </dl>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
