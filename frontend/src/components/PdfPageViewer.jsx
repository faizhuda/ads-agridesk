// Isolated component for react-pdf / pdfjs-dist
// Must stay in its own file so Vite puts it in a separate chunk,
// preventing the pdfjs-dist TDZ circular dependency from crashing the parent page.
import { Document, Page, pdfjs } from 'react-pdf';
import 'react-pdf/dist/Page/AnnotationLayer.css';
import 'react-pdf/dist/Page/TextLayer.css';

pdfjs.GlobalWorkerOptions.workerSrc = `https://cdn.jsdelivr.net/npm/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

export default function PdfPageViewer({ file, currentPage, width, onLoadSuccess }) {
  return (
    <Document
      file={file}
      onLoadSuccess={onLoadSuccess}
      loading={
        <div className="flex items-center justify-center h-96 text-sm text-primary/40">
          Memuat PDF...
        </div>
      }
    >
      <Page
        pageNumber={currentPage}
        width={width}
        renderAnnotationLayer={false}
        renderTextLayer={false}
      />
    </Document>
  );
}
