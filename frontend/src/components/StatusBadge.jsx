const STATUS_COLORS = {
  DRAFT: '#718096',
  MENUNGGU_TTD_DOSEN: '#d69e2e',
  MENUNGGU_PROSES_ADMIN: '#3182ce',
  SELESAI: '#38a169',
  DITOLAK: '#e53e3e',
}

const STATUS_LABELS = {
  DRAFT: 'Draft',
  MENUNGGU_TTD_DOSEN: 'Menunggu TTD Dosen',
  MENUNGGU_PROSES_ADMIN: 'Menunggu Proses Admin',
  SELESAI: 'Selesai',
  DITOLAK: 'Ditolak',
}

export default function StatusBadge({ status }) {
  const color = STATUS_COLORS[status] || '#718096'
  const label = STATUS_LABELS[status] || status
  return (
    <span
      className="status-badge"
      style={{ background: color }}
    >
      {label}
    </span>
  )
}
