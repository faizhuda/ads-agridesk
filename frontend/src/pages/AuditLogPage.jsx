import { useState, useEffect, useMemo, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Activity, Clock, User, ShieldAlert, Monitor, ChevronLeft, ChevronRight, CheckCircle2, XCircle, AlertCircle } from 'lucide-react';
import api from '../api';
import { format } from 'date-fns';
import { id } from 'date-fns/locale';
import TableSkeleton from '../components/TableSkeleton';

export default function AuditLogPage() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  const [page, setPage] = useState(1);
  const [size] = useState(20);
  const [total, setTotal] = useState(0);

  const fetchLogs = useCallback(async (currentPage) => {
    setLoading(true);
    try {
      const skip = (currentPage - 1) * size;
      const res = await api.get(`/api/audit-logs?skip=${skip}&limit=${size}`);
      setLogs(res.data.items);
      setTotal(res.data.total);
      setError('');
    } catch (err) {
      setError('Gagal memuat log sistem: ' + (err.response?.data?.error?.message || err.message));
    } finally {
      setLoading(false);
    }
  }, [size]);

  useEffect(() => {
    fetchLogs(page);
  }, [page, fetchLogs]);

  const totalPages = Math.max(1, Math.ceil(total / size));

  const getStatusIcon = (status) => {
    if (!status) return <Activity className="w-4 h-4 text-primary/40" />;
    const s = status.toUpperCase();
    if (s.includes('SUCCESS') || s.includes('SELESAI') || s.includes('APPROVE')) return <CheckCircle2 className="w-4 h-4 text-primary" />;
    if (s.includes('FAIL') || s.includes('REJECT') || s.includes('ERROR')) return <XCircle className="w-4 h-4 text-red-600" />;
    if (s.includes('PENDING') || s.includes('PROCESS')) return <Clock className="w-4 h-4 text-primary/60" />;
    return <Activity className="w-4 h-4 text-primary" />;
  };

  const getStatusBadgeClass = (status) => {
    if (!status) return 'bg-sepia-200 text-primary border-transparent';
    const s = status.toUpperCase();
    if (s.includes('SUCCESS') || s.includes('SELESAI') || s.includes('APPROVE')) return 'bg-primary/5 text-primary border-primary/20';
    if (s.includes('FAIL') || s.includes('REJECT') || s.includes('ERROR')) return 'bg-red-50 text-red-900 border-red-200';
    if (s.includes('PENDING') || s.includes('PROCESS')) return 'bg-ivory-dark text-primary border-sepia-200';
    return 'bg-ivory-dark text-primary border-sepia-200';
  };

  if (loading && logs.length === 0) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <TableSkeleton rows={6} />
      </div>
    );
  }

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12"
    >
      <div className="mb-12">
        <p className="text-[10px] tracking-widest text-primary/50 uppercase mb-4">Aktivitas Sistem &middot; Admin</p>
        <div className="max-w-2xl">
          <h1 className="text-3xl sm:text-4xl font-serif text-primary mb-3">
            Audit <span className="italic">Logs.</span>
          </h1>
          <p className="text-sm text-primary/70 leading-relaxed">
            Riwayat lengkap aktivitas, transaksi dokumen, dan kejadian sistem lainnya dalam lingkungan Agridesk.
          </p>
        </div>
      </div>

      {error && (
        <div className="mb-8 p-4 bg-red-50 border border-red-200 rounded-sm">
          <p className="text-sm text-red-900">{error}</p>
        </div>
      )}

      {/* Desktop Table View */}
      <div className="hidden sm:block border border-sepia-200 bg-white rounded-sm overflow-hidden">
        <table className="w-full text-left text-sm text-primary/80">
          <thead className="bg-ivory border-b border-sepia-200 text-xs uppercase tracking-wider text-primary/50">
            <tr>
              <th className="px-6 py-4 font-medium">Waktu</th>
              <th className="px-6 py-4 font-medium">Event</th>
              <th className="px-6 py-4 font-medium">Aktor</th>
              <th className="px-6 py-4 font-medium">Target</th>
              <th className="px-6 py-4 font-medium">Status</th>
              <th className="px-6 py-4 font-medium">Metadata</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-sepia-200">
            {logs.length === 0 ? (
              <tr>
                <td colSpan="6" className="px-6 py-12 text-center text-primary/50 italic">
                  Tidak ada log aktivitas.
                </td>
              </tr>
            ) : (
              logs.map((log) => (
                <tr key={log.id} className="hover:bg-ivory/50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap text-xs">
                    {format(new Date(log.created_at), 'dd MMM yyyy, HH:mm:ss', { locale: id })}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      {getStatusIcon(log.status)}
                      <span className="font-medium text-primary">{log.event_name}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    {log.actor_role ? (
                      <div>
                        <div className="font-medium text-primary text-xs">{log.actor_name || log.actor_role}</div>
                        <div className="text-[10px] text-primary/50">{log.actor_role} (ID: {log.actor_id})</div>
                      </div>
                    ) : (
                      <span className="text-primary/40 text-xs italic">System</span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-xs text-primary/70">
                    {log.target_name ? (
                      <div>
                        <div className="font-medium text-primary line-clamp-2">{log.target_name}</div>
                        <div className="text-[10px] font-mono mt-0.5 text-primary/50 uppercase">{log.target_type} #{log.target_id}</div>
                      </div>
                    ) : log.target_type ? (
                      <span className="font-mono uppercase text-[10px]">{log.target_type} #{log.target_id}</span>
                    ) : (
                      '-'
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {log.status ? (
                      <span className={`inline-flex px-2 py-0.5 text-[10px] uppercase tracking-wider font-medium border rounded-sm ${getStatusBadgeClass(log.status)}`}>
                        {log.status}
                      </span>
                    ) : (
                      <span className="text-primary/30">-</span>
                    )}
                  </td>
                  <td className="px-6 py-4 max-w-[200px] text-xs">
                    <div className="flex items-center gap-2 text-primary/60 mb-1">
                      <Monitor className="w-3 h-3 shrink-0" />
                      <span className="truncate">{log.ip_address || '-'}</span>
                    </div>
                    {log.metadata_json && (() => {
                      try {
                        const data = JSON.parse(log.metadata_json);
                        return (
                          <div className="text-[10px] space-y-0.5 mt-1">
                            {Object.entries(data).map(([k, v]) => (
                              <div key={k} className="flex gap-2">
                                <span className="text-primary/40 capitalize shrink-0">{k.replace(/_/g, ' ')}:</span>
                                <span className="text-primary/70 truncate" title={String(v)}>{typeof v === 'object' ? JSON.stringify(v) : String(v)}</span>
                              </div>
                            ))}
                          </div>
                        );
                      } catch (e) {
                        return <div className="text-[10px] text-primary/40 truncate mt-1" title={log.metadata_json}>{log.metadata_json}</div>;
                      }
                    })()}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Mobile Card View */}
      <div className="sm:hidden space-y-4">
        {logs.length === 0 ? (
          <div className="p-8 text-center text-primary/50 italic border border-sepia-200 bg-white rounded-sm">
            Tidak ada log aktivitas.
          </div>
        ) : (
          logs.map((log) => (
            <div key={log.id} className="border border-sepia-200 bg-white p-4 rounded-sm flex flex-col gap-3">
              <div className="flex justify-between items-start gap-2">
                <div className="flex items-start gap-2">
                  <div className="mt-0.5">{getStatusIcon(log.status)}</div>
                  <div>
                    <h3 className="font-medium text-sm text-primary leading-tight">{log.event_name}</h3>
                    <p className="text-xs text-primary/50 mt-1">
                      {format(new Date(log.created_at), 'dd MMM yyyy, HH:mm:ss', { locale: id })}
                    </p>
                  </div>
                </div>
                {log.status && (
                  <span className={`shrink-0 inline-flex px-2 py-0.5 text-[10px] uppercase tracking-wider font-medium border rounded-sm ${getStatusBadgeClass(log.status)}`}>
                    {log.status}
                  </span>
                )}
              </div>
              
              <div className="grid grid-cols-2 gap-2 text-xs pt-3 border-t border-sepia-200/50 mt-1">
                <div>
                  <p className="text-primary/40 uppercase tracking-wider text-[10px] mb-0.5">Aktor</p>
                  <p className="font-medium text-primary">{log.actor_name || log.actor_role || <span className="italic font-normal">System</span>}</p>
                  {log.actor_role && <p className="text-[10px] text-primary/50 mt-0.5">{log.actor_role}</p>}
                </div>
                <div>
                  <p className="text-primary/40 uppercase tracking-wider text-[10px] mb-0.5">Target</p>
                  <p className="text-primary font-medium line-clamp-1">{log.target_name || (log.target_type ? `${log.target_type} #${log.target_id}` : '-')}</p>
                  {log.target_name && <p className="text-[10px] text-primary/50 font-mono mt-0.5 uppercase">{log.target_type} #{log.target_id}</p>}
                </div>
              </div>
              
              <div className="text-xs">
                 <p className="text-primary/40 uppercase tracking-wider text-[10px] mb-0.5">Keterangan / Metadata</p>
                 <div className="flex items-center gap-2 text-primary/70 mb-1">
                    <Monitor className="w-3 h-3 shrink-0" />
                    <span>{log.ip_address || '-'}</span>
                 </div>
                 {log.metadata_json && (() => {
                    try {
                      const data = JSON.parse(log.metadata_json);
                      return (
                        <div className="text-[10px] space-y-0.5 mt-1">
                          {Object.entries(data).map(([k, v]) => (
                            <div key={k} className="flex gap-2">
                              <span className="text-primary/40 capitalize">{k.replace(/_/g, ' ')}:</span>
                              <span className="text-primary/70">{typeof v === 'object' ? JSON.stringify(v) : String(v)}</span>
                            </div>
                          ))}
                        </div>
                      );
                    } catch (e) {
                      return <p className="text-[10px] text-primary/50 mt-1 break-words">{log.metadata_json}</p>;
                    }
                 })()}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Pagination Controls */}
      {!loading && totalPages > 1 && (
        <div className="mt-8 flex items-center justify-between">
          <p className="text-xs text-primary/50">
            Menampilkan <span className="font-medium">{(page - 1) * size + 1}</span> - <span className="font-medium">{Math.min(page * size, total)}</span> dari <span className="font-medium">{total}</span>
          </p>
          <div className="flex gap-2">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="p-2 border border-sepia-200 bg-white text-primary hover:bg-ivory disabled:opacity-50 disabled:cursor-not-allowed rounded-sm transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="p-2 border border-sepia-200 bg-white text-primary hover:bg-ivory disabled:opacity-50 disabled:cursor-not-allowed rounded-sm transition-colors"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </motion.div>
  );
}
