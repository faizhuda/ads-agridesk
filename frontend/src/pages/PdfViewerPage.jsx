import { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import { toast } from 'sonner';
import { ArrowLeft, Download, ExternalLink } from 'lucide-react';
import { downloadSuratPdf, fetchSuratPdfBlobUrl } from '../utils/pdf';

export default function PdfViewerPage() {
  const { id } = useParams();
  const [pdfBlobUrl, setPdfBlobUrl] = useState(null);

  useEffect(() => {
    let url = null;
    fetchSuratPdfBlobUrl(id).then(blobUrl => {
      url = blobUrl;
      setPdfBlobUrl(blobUrl);
    }).catch(() => {});
    return () => { if (url) URL.revokeObjectURL(url); };
  }, [id]);

  return (
    <div className="flex flex-col h-dvh">
      {/* Toolbar */}
      <div className="shrink-0 px-4 sm:px-6 py-3 bg-ivory border-b border-sepia-200 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link
            to={`/surat/${id}`}
            className="p-2 border border-sepia-200 text-primary hover:border-primary transition-colors rounded-sm bg-white"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <h2 className="text-base font-serif text-primary">Dokumen #{id}</h2>
            <p className="text-[10px] tracking-widest uppercase text-primary/50">Pratinjau Resmi</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={async () => { try { await downloadSuratPdf(id); } catch { toast.error('Gagal mengunduh PDF'); } }}
            className="flex items-center gap-2 px-4 py-2 text-sm border border-sepia-200 text-primary hover:border-primary hover:bg-white transition-colors rounded-sm"
          >
            <Download className="w-4 h-4" />
            <span className="hidden sm:inline">Unduh</span>
          </button>
          {pdfBlobUrl && (
            <a
              href={pdfBlobUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-4 py-2 text-sm border border-sepia-200 text-primary hover:border-primary hover:bg-white transition-colors rounded-sm"
            >
              <ExternalLink className="w-4 h-4" />
              <span className="hidden sm:inline">Tab Baru</span>
            </a>
          )}
        </div>
      </div>

      {/* PDF Iframe — fills all remaining space */}
      <div className="flex-1 min-h-0">
        <iframe
          src={pdfBlobUrl || ''}
          title={`Dokumen Surat #${id}`}
          className="w-full h-full border-0 bg-white"
          allow="fullscreen"
        />
      </div>
    </div>
  );
}
