const API_BASE = import.meta.env.VITE_API_BASE || '/api'

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, options)
  const contentType = response.headers.get('content-type') || ''
  const payload = contentType.includes('application/json')
    ? await response.json()
    : await response.text()

  if (!response.ok) {
    const detail =
      typeof payload === 'object' && payload?.detail
        ? payload.detail
        : JSON.stringify(payload)
    throw new Error(detail || `HTTP ${response.status}`)
  }

  return payload
}

function authHeaders(token) {
  return { Authorization: `Bearer ${token}` }
}

// ---- AUTH ----
export async function registerUser(data) {
  return request('/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
}

export async function loginUser(email, password) {
  const body = new URLSearchParams({ username: email, password })
  return request('/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body,
  })
}

// ---- USERS ----
export async function listDosenUsers(token) {
  return request('/users/dosen', { headers: authHeaders(token) })
}

// ---- SURAT ----
export async function createSurat(token, payload) {
  return request('/surat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders(token) },
    body: JSON.stringify(payload),
  })
}

export async function uploadSuratEksternal(token, jenis, keperluan, file) {
  const formData = new FormData()
  formData.append('jenis', jenis)
  if (keperluan) formData.append('keperluan', keperluan)
  formData.append('file', file)
  return request('/surat/upload', {
    method: 'POST',
    headers: { ...authHeaders(token) },
    body: formData,
  })
}

export async function listMySurat(token) {
  return request('/surat/me', { headers: authHeaders(token) })
}

export async function listPendingDosen(token) {
  return request('/surat/pending-dosen', { headers: authHeaders(token) })
}

export async function listHistoryDosen(token) {
  return request('/surat/history-dosen', { headers: authHeaders(token) })
}

export async function listPendingAdmin(token) {
  return request('/surat/pending-admin', { headers: authHeaders(token) })
}

export async function listHistoryAdmin(token) {
  return request('/surat/history-admin', { headers: authHeaders(token) })
}

export async function signSurat(token, suratId, imagePath) {
  return request(`/surat/${suratId}/ttd-dosen`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders(token) },
    body: JSON.stringify({ image_path: imagePath }),
  })
}

export async function rejectDosenSurat(token, suratId, reason) {
  return request(`/surat/${suratId}/reject-dosen`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders(token) },
    body: JSON.stringify({ reason }),
  })
}

export async function approveSurat(token, suratId) {
  return request(`/surat/${suratId}/approve-admin`, {
    method: 'POST',
    headers: authHeaders(token),
  })
}

export async function rejectSurat(token, suratId, reason) {
  return request(`/surat/${suratId}/reject`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders(token) },
    body: JSON.stringify({ reason }),
  })
}

export async function verifyDocument(documentHash) {
  return request(`/verify/${documentHash}`)
}