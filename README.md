# Agridesk

Agridesk adalah sistem pengajuan surat akademik dengan alur persetujuan berjenjang:

1. Mahasiswa mengajukan surat (internal atau eksternal)
2. Dosen melakukan tanda tangan
3. Admin melakukan persetujuan akhir atau penolakan
4. Dokumen dapat diverifikasi publik menggunakan `document_hash`

Repository ini berisi:

- Backend: FastAPI + SQLAlchemy + PostgreSQL
- Frontend: React + Vite + React Router

---

## 1. Fitur Utama

### Autentikasi & Otorisasi

- Registrasi user role-based: `MAHASISWA`, `DOSEN`, `ADMIN`
- Validasi identitas role:
	- `MAHASISWA` wajib `nim`
	- `DOSEN` / `ADMIN` wajib `nip`
- Login dengan JWT (`Bearer token`)
- Guard endpoint berbasis role

### Workflow Surat

- Pengajuan surat internal (generate dari input sistem)
- Pengajuan surat eksternal (upload PDF)
- Tanda tangan dosen
- Approval admin
- Rejection admin + alasan penolakan
- Public verification via hash

### Dokumen & Keamanan Integritas

- `document_hash` dihasilkan saat final approval admin
- QR code verifikasi di-generate saat approval admin
- PDF surat di-generate saat approval admin
- Signature hash tersimpan di tabel `signatures`

### Operasional

- Structured request logging + `X-Request-ID`
- In-memory rate limiter (IP-based)
- Health check endpoint (`/health`)
- Readiness endpoint (`/ready`) untuk validasi koneksi DB
- Audit trail (`audit_logs`)

### Kualitas Kode

- Alembic migrations terstruktur
- Unit + integration tests dengan pytest
- GitHub Actions CI untuk backend

---

## 2. Arsitektur Sistem

Agridesk menggunakan pendekatan layer/clean architecture sederhana.

### Backend layers

1. **Controllers**
	 - Menerima HTTP request
	 - Validasi akses role
	 - Memanggil service
	 - Return response schema

2. **Services**
	 - Menjalankan business rules workflow surat
	 - Menentukan transisi status
	 - Mengelola hash/QR/PDF generation trigger

3. **Domain**
	 - Entity utama: `User`, `Surat`, `Signature`, `AuditLog`
	 - Enum status surat
	 - Domain exceptions

4. **Repositories**
	 - Interface repository (abstraksi)
	 - Implementasi PostgreSQL dengan SQLAlchemy

5. **Database Models**
	 - Mapping tabel SQLAlchemy (`users`, `surat`, `signatures`, `audit_logs`)

### Frontend layers

- **Routing**: React Router
- **State auth**: Context API (`AuthContext`)
- **Pages**: Login, Register, Dashboard role-based, Ajukan Surat, Verify
- **API client**: wrapper `fetch` pada satu modul

### Alur data ringkas

`UI -> API Client -> FastAPI Controller -> Service -> Repository -> PostgreSQL`

---

## 3. Workflow Bisnis

### 3.1 Workflow utama

```text
REGISTER
	↓
LOGIN
	↓
MAHASISWA AJUKAN SURAT
	↓
MENUNGGU_TTD_DOSEN
	↓
DOSEN APPROVE / TTD
	↓
MENUNGGU_PROSES_ADMIN
	↓
ADMIN APPROVE
	↓
SELESAI + HASH (+ QR + PDF)
	↓
VERIFIKASI PUBLIK
```

### 3.2 Jalur penolakan

```text
MENUNGGU_TTD_DOSEN / MENUNGGU_PROSES_ADMIN
	↓
ADMIN REJECT
	↓
DITOLAK + rejection_reason
```

### 3.3 Status transition

```text
DRAFT -> MENUNGGU_TTD_DOSEN -> MENUNGGU_PROSES_ADMIN -> SELESAI
```

atau

```text
... -> DITOLAK
```

---

## 4. Surat Internal vs Eksternal

| Aspek | Internal | Eksternal |
|---|---|---|
| Sumber konten | Input form sistem | Upload file PDF |
| `is_external` | `false` | `true` |
| `file_path` | `null` | path file upload |
| PDF akhir | Digenerate sistem | Tetap digenerate output final approval |
| Hash | Saat admin approve | Saat admin approve |

---

## 5. Struktur Folder

```text
ads-agridesk/
├─ backend/
│  ├─ app/
│  │  ├─ controllers/
│  │  ├─ services/
│  │  ├─ domain/
│  │  ├─ repositories/
│  │  ├─ database/
│  │  │  └─ models/
│  │  ├─ schemas/
│  │  ├─ utils/
│  │  └─ core/
│  ├─ alembic/
│  │  └─ versions/
│  ├─ tests/
│  ├─ requirements.txt
│  └─ .env.example
├─ frontend/
│  ├─ src/
│  │  ├─ components/
│  │  ├─ context/
│  │  ├─ pages/
│  │  └─ api.js
│  ├─ package.json
│  └─ vite.config.js
└─ .github/workflows/
```

---

## 6. Teknologi yang Digunakan

### Backend

- Python 3.12+
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- passlib + bcrypt
- python-jose (JWT)
- qrcode
- reportlab
- pytest + pytest-cov

### Frontend

- React 18
- Vite 5
- React Router DOM

---

## 7. Konfigurasi Environment

Buat file `backend/.env` dari template:

```bash
cp backend/.env.example backend/.env
```

Contoh isi:

```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/agridesk
JWT_SECRET_KEY=change_this_jwt_secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
AGRIDESK_HASH_SECRET=change_this_hash_secret
AGRIDESK_DOCUMENTS_DIR=backend/storage/documents
AGRIDESK_RATE_LIMIT_ENABLED=true
AGRIDESK_RATE_LIMIT_WINDOW_SECONDS=60
AGRIDESK_RATE_LIMIT_REQUESTS=120
```

---

## 8. Setup Lokal (End-to-End)

### 8.1 Prasyarat

- Python 3.12+
- Node.js 18+
- PostgreSQL 14+

### 8.2 Backend setup

```bash
cd backend
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Backend akan berjalan di: `http://127.0.0.1:8000`

### 8.3 Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Frontend akan berjalan di: `http://127.0.0.1:5173`

Vite proxy sudah diarahkan ke backend melalui prefix `/api`.

---

## 9. API Endpoint Ringkas

### Auth

- `POST /register`
- `POST /login` (form-urlencoded)

### Surat (Mahasiswa)

- `POST /surat` (internal)
- `POST /surat/upload` (eksternal, multipart)
- `GET /surat/me`

### Surat (Dosen)

- `GET /surat/pending-dosen`
- `POST /surat/{surat_id}/ttd-dosen`

### Surat (Admin)

- `GET /surat/pending-admin`
- `POST /surat/{surat_id}/approve-admin`
- `POST /surat/{surat_id}/reject`

### Publik

- `GET /verify/{document_hash}`

### Operasional

- `GET /health`
- `GET /ready`

---

## 10. Skema Database (Konseptual)

### `users`

- id, name, email, password_hash, role
- nim (nullable, unique)
- nip (nullable, unique)
- created_at, updated_at

### `surat`

- id, mahasiswa_id, jenis, keperluan
- is_external, file_path
- status, document_hash, pdf_path, qr_path
- rejection_reason
- created_at, updated_at

### `signatures`

- id, surat_id, owner_id, role
- image_path, signature_hash, signed_at
- created_at, updated_at

### `audit_logs`

- id, event_name
- actor_id, actor_role
- target_type, target_id
- status, metadata_json, ip_address
- created_at

---

## 11. Migrasi Database (Alembic)

Revisi saat ini:

1. `20260301_0001` - kolom tambahan dasar surat/users
2. `20260301_0002` - signatures + document assets
3. `20260301_0003` - audit logs table
4. `20260301_0004` - nim/nip pada users
5. `20260301_0005` - keperluan/file_path pada surat

Perintah penting:

```bash
alembic upgrade head
alembic downgrade -1
alembic current
```

---

## 12. Testing & CI

### Jalankan test lokal

```bash
cd backend
pytest -q
```

### Coverage

```bash
pytest -q --cov=app --cov-report=term-missing --cov-report=xml
```

### CI

Workflow GitHub Actions backend:

- Menyalakan PostgreSQL service
- Install dependencies
- Jalankan alembic migration
- Jalankan test + coverage

---

## 13. Frontend Routing & Role Access

### Public routes

- `/`
- `/verify`
- `/login`
- `/register`

### Protected routes

- `/dashboard` untuk semua role login
- `/ajukan` khusus role `MAHASISWA`

Dashboard otomatis menampilkan komponen berbeda untuk:

- Mahasiswa: list surat pribadi
- Dosen: list pending tanda tangan
- Admin: list pending approval + aksi approve/reject

---

## 14. Keamanan & Observability

- Password disimpan dalam bentuk hash bcrypt
- Token JWT berisi `sub`, `email`, `role`, `name`
- Rate limit configurable via env
- Audit log untuk aksi penting
- Structured logging request dengan durasi respons

> Catatan: implementasi rate limiter saat ini bersifat in-memory (single instance). Untuk skala produksi multi-instance, disarankan migrasi ke Redis-based rate limiter.

---

## 15. Catatan Produksi (Disarankan)

- Gunakan secret key acak yang kuat
- Pisahkan konfigurasi dev/staging/prod
- Gunakan object storage untuk file eksternal dan dokumen final
- Tambahkan reverse proxy (Nginx) + TLS
- Gunakan process manager (systemd / container orchestrator)
- Tambahkan backup strategy PostgreSQL

---

## 16. Quick Smoke Test Manual

1. Register 3 akun: Mahasiswa, Dosen, Admin
2. Login masing-masing role
3. Mahasiswa ajukan surat internal
4. Dosen tanda tangan surat
5. Admin approve surat
6. Ambil `document_hash`
7. Verifikasi via endpoint publik `/verify/{hash}`

Expected:

- Status berubah sesuai workflow
- Hash, QR, PDF tersedia setelah approval admin
- Verifikasi publik menghasilkan status `VALID`

---

## 17. Lisensi

Mengacu ke file `LICENSE` pada repository ini.
