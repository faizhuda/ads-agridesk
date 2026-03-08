import { useEffect, useMemo, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { downloadSuratPdf, fetchSuratPdfBlobUrl } from '../utils/pdf';

export default function PdfViewerPage() {
  const { id } = useParams();
  const [pdfUrl, setPdfUrl] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;
    let objectUrl = '';
    setLoading(true);
    setError('');

    fetchSuratPdfBlobUrl(id)
      .then((url) => {
        if (!active) return;
        objectUrl = url;
        setPdfUrl(url);
      })
      .catch((err) => {
        if (!active) return;
        setError(err.message || 'Gagal memuat PDF');
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [id]);

  const downloadName = useMemo(() => `surat-${id}.pdf`, [id]);

  if (loading) return (
    <div className="flex flex-col justify-center items-center h-[70vh]">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
      <p className="text-gray-500 font-medium">Menyiapkan dokumen PDF...</p>
    </div>
  );
  
  if (error) return (
    <div className="max-w-3xl mx-auto mt-8">
      <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-md">
        <div className="flex items-center">
          <svg className="h-6 w-6 text-red-500 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
          <p className="text-sm font-medium text-red-700">{error}</p>
        </div>
        <div className="mt-4">
          <Link to={`/surat/${id}`} className="text-red-700 underline font-medium text-sm hover:text-red-800">Kembali ke Detail Surat</Link>
        </div>
      </div>
    </div>
  );

  return (
    <div className="h-[85vh] flex flex-col max-w-6xl mx-auto bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
      <div className="p-4 sm:p-5 border-b border-gray-200 bg-gray-50 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-gray-900 flex items-center">
            <svg className="w-6 h-6 mr-2 text-red-500" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14H9v-2h2v2zm0-4H9V7h2v5zm4 4h-2V7h2v9z"/></svg>
            Preview Dokumen #{id}
          </h2>
          <p className="text-sm text-gray-500 mt-1 pl-8">Pratinjau langsung integrasi tanda tangan elektronik.</p>
        </div>
        
        <div className="flex items-center space-x-3">
          <Link to={`/surat/${id}`} className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors">
            Kembali
          </Link>
          <button 
            type="button" 
            className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
            onClick={() => downloadSuratPdf(id, downloadName)}
          >
            <svg className="-ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
            Unduh PDF
          </button>
        </div>
      </div>

      <div className="flex-1 bg-gray-200 w-full relative">
        {pdfUrl && (
          <iframe
            title={`pdf-surat-${id}`}
            src={pdfUrl}
            className="absolute inset-0 w-full h-full border-none"
          />
        )}
      </div>
    </div>
  );
}
