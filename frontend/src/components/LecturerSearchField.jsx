import { useState, useEffect } from 'react';
import api from '../api';

/**
 * Reusable lecturer search + selection field.
 *
 * Props:
 *   label          – field label text
 *   placeholder    – input placeholder
 *   helperText     – small grey hint below the label
 *   selectedLecturer – { id, name, nip, email } | null
 *   onSelect(lecturer) – called when a lecturer is chosen from the dropdown
 *   onClear()          – called when the selected lecturer chip's × is clicked
 */
export default function LecturerSearchField({
  label,
  placeholder = 'Ketik nama atau NIP dosen...',
  helperText,
  selectedLecturer,
  onSelect,
  onClear,
}) {
  const [query, setQuery] = useState('');
  const [options, setOptions] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const keyword = query.trim();
    if (!keyword) { setOptions([]); return; }

    const timeout = setTimeout(async () => {
      setLoading(true);
      try {
        const res = await api.get('/api/auth/lecturers/search', {
          params: { q: keyword, limit: 10 },
        });
        setOptions(res.data || []);
      } catch {
        setOptions([]);
      } finally {
        setLoading(false);
      }
    }, 250);

    return () => clearTimeout(timeout);
  }, [query]);

  const choose = (lecturer) => {
    onSelect(lecturer);
    setQuery('');
    setOptions([]);
  };

  return (
    <div>
      <label className="block text-sm font-medium text-primary mb-2">{label}</label>
      {helperText && <p className="text-xs text-primary/60 mb-3">{helperText}</p>}

      {!selectedLecturer ? (
        <div className="relative">
          <input
            type="text"
            className="appearance-none block w-full px-4 py-3 bg-ivory border border-sepia-200 rounded-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary sm:text-sm transition-colors"
            placeholder={placeholder}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />

          {query.trim() && (
            <div className="absolute z-10 mt-1 w-full bg-white border border-sepia-200 shadow-lg max-h-60 rounded-sm py-1 overflow-auto sm:text-sm">
              {loading && (
                <div className="px-4 py-3 text-sm text-primary/50 italic">Mencari dosen...</div>
              )}
              {!loading && options.length === 0 && (
                <div className="px-4 py-3 text-sm text-primary/50 italic">Dosen tidak ditemukan</div>
              )}
              {!loading && options.map((lecturer) => (
                <button
                  key={lecturer.id}
                  type="button"
                  className="w-full text-left px-4 py-3 hover:bg-ivory focus:bg-ivory focus:outline-none transition-colors border-b border-sepia-200/50 last:border-0"
                  onClick={() => choose(lecturer)}
                >
                  <div className="font-medium text-primary">{lecturer.name}</div>
                  <div className="text-xs text-primary/60 mt-0.5">
                    {lecturer.nip || '-'} &middot; {lecturer.email}
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      ) : (
        <div className="flex items-center justify-between w-full px-4 py-3 bg-white border border-primary/20 rounded-sm shadow-sm">
          <div>
            <div className="text-sm font-medium text-primary">{selectedLecturer.name}</div>
            <div className="text-xs text-primary/60">{selectedLecturer.nip || '-'}</div>
          </div>
          <button
            type="button"
            onClick={() => { onClear(); setQuery(''); setOptions([]); }}
            className="shrink-0 ml-4 p-1 text-primary/40 hover:text-red-600 transition-colors focus:outline-none"
            title="Hapus dosen"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      )}
    </div>
  );
}
