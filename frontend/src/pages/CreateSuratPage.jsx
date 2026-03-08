import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';

const FIELD_LABELS = {
  keperluan_surat_aktif: 'Keperluan Surat Aktif',
  mata_kuliah_yang_dibatalkan: 'Mata Kuliah yang Dibatalkan',
  alasan_pembatalan_kuliah: 'Alasan Pembatalan Kuliah',
};

export default function CreateSuratPage() {
  const navigate = useNavigate();
  const [mode, setMode] = useState('internal');
  const [templates, setTemplates] = useState([]);
  const [selectedTemplateName, setSelectedTemplateName] = useState('');
  const [internalFields, setInternalFields] = useState({});

  const [jenis, setJenis] = useState('');
  const [keperluan, setKeperluan] = useState('');
  const [lecturerQuery, setLecturerQuery] = useState('');
  const [lecturerOptions, setLecturerOptions] = useState([]);
  const [selectedLecturers, setSelectedLecturers] = useState([]);
  const [lecturerSearchLoading, setLecturerSearchLoading] = useState(false);
  const [file, setFile] = useState(null);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (mode !== 'internal') return;
    const fetchTemplates = async () => {
      try {
        const res = await api.get('/api/surat/templates/internal');
        setTemplates(res.data || []);
        if (res.data?.length && !selectedTemplateName) {
          setSelectedTemplateName(res.data[0].name);
        }
      } catch (err) {
        setError(err.response?.data?.detail || 'Gagal memuat jenis surat internal');
      }
    };
    fetchTemplates();
  }, [mode, selectedTemplateName]);

  const selectedTemplate = useMemo(
    () => templates.find((t) => t.name === selectedTemplateName) || null,
    [templates, selectedTemplateName]
  );

  useEffect(() => {
    const keyword = lecturerQuery.trim();
    if (!keyword) {
      setLecturerOptions([]);
      return;
    }

    const timeout = setTimeout(async () => {
      setLecturerSearchLoading(true);
      try {
        const res = await api.get('/api/auth/lecturers/search', {
          params: { q: keyword, limit: 10 },
        });
        setLecturerOptions(res.data || []);
      } catch (err) {
        setLecturerOptions([]);
      } finally {
        setLecturerSearchLoading(false);
      }
    }, 250);

    return () => clearTimeout(timeout);
  }, [lecturerQuery]);

  const addLecturer = (lecturer) => {
    setSelectedLecturers((prev) => {
      if (prev.some((item) => item.id === lecturer.id)) return prev;
      return [...prev, lecturer];
    });
    setLecturerQuery('');
    setLecturerOptions([]);
  };

  const removeLecturer = (lecturerId) => {
    setSelectedLecturers((prev) => prev.filter((item) => item.id !== lecturerId));
  };

  const deriveKeperluanFromFields = () => {
    if (internalFields.keperluan_surat_aktif?.trim()) {
      return internalFields.keperluan_surat_aktif.trim();
    }
    if (internalFields.alasan_pembatalan_kuliah?.trim()) {
      return internalFields.alasan_pembatalan_kuliah.trim();
    }
    return 'Pengajuan surat internal';
  };

  const buildInternalPayload = () => {
    if (!selectedTemplate) {
      throw new Error('Pilih jenis surat internal terlebih dahulu');
    }

    const requiredFields = selectedTemplate.required_fields || [];
    const normalizedFields = {};

    for (const key of requiredFields) {
      const value = (internalFields[key] || '').trim();
      if (!value) {
        throw new Error('Field ' + (FIELD_LABELS[key] || key) + ' wajib diisi');
      }
      normalizedFields[key] = value;
    }

    return {
      jenis: selectedTemplate.name,
      keperluan: deriveKeperluanFromFields(),
      fields: normalizedFields,
      lecturer_ids: selectedLecturers.length ? selectedLecturers.map((item) => item.id) : null,
    };
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      if (mode === 'internal') {
        const payload = buildInternalPayload();
        await api.post('/api/surat/internal', payload);
      } else {
        if (!file) { setError('File PDF wajib diupload'); setSubmitting(false); return; }
        const form = new FormData();
        form.append('jenis', jenis);
        form.append('keperluan', keperluan);
        form.append('lecturer_ids', selectedLecturers.map((item) => item.id).join(','));
        form.append('file', file);
        await api.post('/api/surat/external', form);
      }
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Gagal membuat surat');
    } finally {
      setSubmitting(false);
    }
  };

  const renderLecturerPicker = () => (
    <div className="mt-6 bg-white p-5 rounded-lg shadow-sm border border-gray-100">
      <label className="block text-sm font-medium text-gray-700 mb-2">Dosen Penandatangan (Opsional)</label>
      <div className="relative">
        <input
          type="text"
          className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm transition-colors"
          placeholder="Ketik nama atau NIP dosen..."
          value={lecturerQuery}
          onChange={(e) => setLecturerQuery(e.target.value)}
        />

        {lecturerQuery.trim() && (
          <div className="absolute z-10 mt-1 w-full bg-white shadow-lg max-h-60 rounded-md py-1 text-base ring-1 ring-black ring-opacity-5 overflow-auto sm:text-sm">
            {lecturerSearchLoading && <div className="px-4 py-2 text-sm text-gray-500">Mencari dosen...</div>}
            {!lecturerSearchLoading && lecturerOptions.length === 0 && (
              <div className="px-4 py-2 text-sm text-gray-500">Dosen tidak ditemukan</div>
            )}
            {!lecturerSearchLoading && lecturerOptions.map((lecturer) => (
              <button
                key={lecturer.id}
                type="button"
                className="w-full text-left px-4 py-2 hover:bg-blue-50 focus:bg-blue-50 focus:outline-none transition-colors"
                onClick={() => addLecturer(lecturer)}
              >
                <div className="font-semibold text-gray-900">{lecturer.name}</div>
                <div className="text-xs text-gray-500">{lecturer.nip || '-'} | {lecturer.email}</div>
              </button>
            ))}
          </div>
        )}
      </div>

      {selectedLecturers.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-2">
          {selectedLecturers.map((lecturer) => (
            <span key={lecturer.id} className="inline-flex items-center py-1.5 pl-3 pr-2 border border-blue-200 bg-blue-50 text-blue-700 rounded-full text-sm font-medium">
              {lecturer.name}
              <button
                type="button"
                onClick={() => removeLecturer(lecturer.id)}
                className="ml-1 shrink-0 h-4 w-4 rounded-full inline-flex items-center justify-center text-blue-400 hover:bg-blue-200 hover:text-blue-500 focus:outline-none focus:bg-blue-500 focus:text-white transition-colors"
              >
                <span className="sr-only">Hapus opsi</span>
                <svg className="h-2 w-2" stroke="currentColor" fill="none" viewBox="0 0 8 8"><path strokeLinecap="round" strokeWidth="1.5" d="M1 1l6 6m0-6L1 7" /></svg>
              </button>
            </span>
          ))}
        </div>
      )}
    </div>
  );

  return (
    <div className="max-w-3xl mx-auto pb-12">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900">Buat Surat Baru</h2>
        <p className="mt-1 text-sm text-gray-500">Pilih mode surat dan lengkapi form di bawah ini.</p>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 border-l-4 border-red-500 p-4 rounded-md">
          <p className="text-sm text-red-700 font-medium">{error}</p>
        </div>
      )}

      <div className="bg-white rounded-xl shadow-md border border-gray-100 overflow-hidden">
        <div className="flex border-b border-gray-200">
          <button
            type="button"
            className={"flex-1 py-4 px-6 text-sm font-medium text-center transition-colors " + (mode === 'internal' ? 'bg-blue-50 text-blue-700 border-b-2 border-blue-700' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50')}
            onClick={() => setMode('internal')}
          >
            Internal (Template)
          </button>
          <button
            type="button"
            className={"flex-1 py-4 px-6 text-sm font-medium text-center transition-colors " + (mode === 'external' ? 'bg-blue-50 text-blue-700 border-b-2 border-blue-700' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50')}
            onClick={() => setMode('external')}
          >
            Eksternal (Upload PDF)
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 sm:p-8">
          {mode === 'internal' && (
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">Pilih Template Surat</label>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  {templates.map((template) => (
                    <button
                      key={template.id}
                      type="button"
                      className={"relative rounded-lg border p-4 flex flex-col focus:outline-none transition-all " + (selectedTemplateName === template.name ? 'bg-blue-50 border-blue-500 ring-1 ring-blue-500' : 'bg-white border-gray-300 hover:border-blue-400')}
                      onClick={() => {
                        setSelectedTemplateName(template.name);
                        setInternalFields({});
                      }}
                    >
                      <span className={"block text-sm font-medium " + (selectedTemplateName === template.name ? 'text-blue-900' : 'text-gray-900')}>
                        {template.name}
                      </span>
                      <span className={"mt-1 flex items-center text-xs " + (selectedTemplateName === template.name ? 'text-blue-700' : 'text-gray-500')}>
                        {template.description}
                      </span>
                    </button>
                  ))}
                </div>
              </div>

              {selectedTemplate && (
                <div className="bg-gray-50 p-5 rounded-lg border border-gray-200 space-y-4">
                  <h3 className="text-sm font-medium text-gray-900 border-b border-gray-200 pb-2">Informasi Surat</h3>
                  {(selectedTemplate.required_fields || []).map((fieldKey) => (
                    <div key={fieldKey}>
                      <label className="block text-sm font-medium text-gray-700">{FIELD_LABELS[fieldKey] || fieldKey}</label>
                      <input
                        type="text"
                        className="mt-1 appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm transition-colors"
                        value={internalFields[fieldKey] || ''}
                        onChange={(e) => setInternalFields((prev) => ({ ...prev, [fieldKey]: e.target.value }))}
                        required
                      />
                    </div>
                  ))}
                </div>
              )}

              {renderLecturerPicker()}
            </div>
          )}

          {mode === 'external' && (
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700">Jenis Surat</label>
                <input type="text" className="mt-1 appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm transition-colors" placeholder="Misal: Surat Keterangan Lulus" value={jenis} onChange={(e) => setJenis(e.target.value)} required />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Keperluan</label>
                <input type="text" className="mt-1 appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm transition-colors" placeholder="Misal: Syarat beasiswa" value={keperluan} onChange={(e) => setKeperluan(e.target.value)} required />
              </div>

              {renderLecturerPicker()}

              <div className="mt-6 border-2 border-gray-300 border-dashed rounded-lg p-6 text-center hover:bg-gray-50 transition-colors">
                <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48" aria-hidden="true">
                  <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                <div className="mt-4 flex text-sm text-gray-600 justify-center">
                  <label htmlFor="file-upload" className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500">
                    <span>Upload file PDF</span>
                    <input id="file-upload" name="file-upload" type="file" accept=".pdf" className="sr-only" onChange={(e) => setFile(e.target.files[0])} />
                  </label>
                  <p className="pl-1">atau drag and drop</p>
                </div>
                <p className="text-xs text-gray-500 mt-2">PDF up to 5MB</p>
                {file && <p className="mt-2 text-sm font-semibold text-green-600">File terpilih: {file.name}</p>}
              </div>
            </div>
          )}

          <div className="mt-8 pt-5 border-t border-gray-200">
            <button
              type="submit"
              disabled={submitting}
              className="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {submitting ? 'Memproses...' : 'Buat Surat Sekarang'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
