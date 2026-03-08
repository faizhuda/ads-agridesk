import { useEffect, useRef, useState } from 'react';
import api from '../api';
import { useAuth } from '../context/AuthContext';

export default function SignatureProfilePage() {
  const { user } = useAuth();
  const canvasRef = useRef(null);
  const drawingRef = useRef(false);
  const [hasSaved, setHasSaved] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState(false);
  const [previewUrl, setPreviewUrl] = useState('');

  const loadSignatureProfile = async () => {
    try {
      const res = await api.get('/api/signatures/me');
      const exists = Boolean(res.data?.has_saved_signature);
      setHasSaved(exists);
      if (!exists) {
        setPreviewUrl('');
        return;
      }
      const imgRes = await api.get('/api/signatures/me/image', {
        responseType: 'blob',
        params: { t: Date.now() },
        headers: {
          'Cache-Control': 'no-cache',
          Pragma: 'no-cache',
        },
      });
      const blobUrl = URL.createObjectURL(new Blob([imgRes.data]));
      setPreviewUrl((prev) => {
        if (prev) URL.revokeObjectURL(prev);
        return blobUrl;
      });
    } catch {
      setHasSaved(false);
      setPreviewUrl('');
    }
  };

  useEffect(() => {
    loadSignatureProfile();
  }, [user?.id]);

  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
    };
  }, [previewUrl]);

  const getPoint = (e) => {
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    if ('touches' in e && e.touches.length > 0) {
      return {
        x: e.touches[0].clientX - rect.left,
        y: e.touches[0].clientY - rect.top,
      };
    }
    return {
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
    };
  };

  const startDraw = (e) => {
    drawingRef.current = true;
    const ctx = canvasRef.current.getContext('2d');
    const { x, y } = getPoint(e);
    ctx.beginPath();
    ctx.moveTo(x, y);
  };

  const draw = (e) => {
    if (!drawingRef.current) return;
    if (e.cancelable) e.preventDefault(); // Prevent scrolling on touch
    const ctx = canvasRef.current.getContext('2d');
    const { x, y } = getPoint(e);
    ctx.lineTo(x, y);
    ctx.strokeStyle = '#1e3a8a';
    ctx.lineWidth = 3;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.stroke();
  };

  const endDraw = () => {
    drawingRef.current = false;
  };

  const clearCanvas = () => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    setMessage('');
  };

  const saveSignature = async () => {
    setMessage('');
    setError(false);
    setSaving(true);
    try {
      const canvas = canvasRef.current;
      const blob = await new Promise((resolve) => canvas.toBlob(resolve, 'image/png'));
      if (!blob) throw new Error('Gagal membuat gambar tanda tangan');

      const form = new FormData();
      form.append('file', blob, 'signature.png');
      await api.post('/api/signatures/me', form);
      await loadSignatureProfile();
      setMessage('Tanda tangan berhasil disimpan. Anda kini dapat langsung menandatangani dokumen.');
    } catch (err) {
      setError(true);
      setMessage(err.response?.data?.detail || err.message || 'Gagal menyimpan tanda tangan');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="p-6 sm:p-8 border-b border-gray-100">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Profil Tanda Tangan</h2>
              <p className="mt-1 text-sm text-gray-500">Kelola tanda tangan digital untuk keperluan administrasi.</p>
            </div>
            <span className={"inline-flex items-center px-3 py-1 rounded-full text-sm font-medium " + (hasSaved ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800')}>
              {hasSaved ? 'Tersimpan' : 'Belum Tersimpan'}
            </span>
          </div>
        </div>

        <div className="p-6 sm:p-8 bg-gray-50/50">
          <div className="max-w-xl mx-auto">
            <label className="block text-sm font-medium text-gray-700 mb-3 text-center">Gambar Tanda Tangan Anda Disini</label>
            <div className="bg-white border-2 border-dashed border-gray-300 rounded-xl overflow-hidden shadow-inner relative touch-none">
              <canvas
                ref={canvasRef}
                width={600}
                height={200}
                className="w-full h-auto cursor-crosshair bg-white"
                onMouseDown={startDraw}
                onMouseMove={draw}
                onMouseUp={endDraw}
                onMouseLeave={endDraw}
                onTouchStart={startDraw}
                onTouchMove={draw}
                onTouchEnd={endDraw}
              />
              <div className="absolute bottom-2 left-2 text-xs text-gray-400 pointer-events-none select-none">
                Gunakan mouse atau sentuhan
              </div>
            </div>

            <div className="mt-6 flex flex-col sm:flex-row gap-3 justify-center">
              <button 
                type="button" 
                className="inline-flex justify-center items-center px-5 py-2.5 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
                onClick={clearCanvas}
              >
                <svg className="-ml-1 mr-2 h-4 w-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                Hapus
              </button>
              <button 
                type="button" 
                className="inline-flex justify-center items-center px-5 py-2.5 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors disabled:opacity-50"
                onClick={saveSignature} 
                disabled={saving}
              >
                {saving ? (
                  <><svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Menyimpan...</>
                ) : (
                  <><svg className="-ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg> Simpan Profil</>
                )}
              </button>
            </div>

            {message && (
              <div className={"mt-4 p-3 rounded-md text-sm text-center " + (error ? 'bg-red-50 text-red-700 border border-red-100' : 'bg-green-50 text-green-700 border border-green-100')}>
                {message}
              </div>
            )}
          </div>
        </div>
      </div>

      {previewUrl && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="p-6 border-b border-gray-100 bg-gray-50">
            <h3 className="text-sm font-medium text-gray-900">Preview Tanda Tangan Tersertifikasi</h3>
          </div>
          <div className="p-6 flex justify-center bg-white">
            <div className="border border-gray-200 rounded-lg p-2 bg-gray-50 shadow-inner inline-block">
              <img src={previewUrl} alt="Preview tanda tangan" className="max-h-32 object-contain" />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
