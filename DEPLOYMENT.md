# Deploying Agridesk on Vercel + Supabase

This deployment starts with an empty database and private file storage. It does
not migrate users, documents, signatures, or audit logs from the mini-PC.

## 1. Create Supabase resources

Create one Supabase project in the desired region. In its SQL Editor, run
[`supabase/setup.sql`](./supabase/setup.sql) to create the private
`agridesk-private` bucket. Copy the session-pooler Postgres URL, project URL,
and service-role key.

From a machine with Python 3.11 or later, initialize the empty database:

```powershell
cd backend
$env:DATABASE_URL = 'postgresql://...'
$env:SECRET_KEY = '<new-random-secret>'
py -3.11 -m alembic upgrade head
```

This bootstrap migration creates all application tables as well as the Alembic
version table. It is designed for a brand-new database; do not use it against
the retired mini-PC database.

The first API startup automatically seeds the built-in letter templates.

## 2. Deploy the API

Create a Vercel project connected to this repository with **Root Directory**
set to `backend`. The function entrypoint is `api/index.py`.

Set these environment variables for Production and Preview as appropriate:

```dotenv
DATABASE_URL=postgresql://...
SECRET_KEY=<new-random-secret>
BASE_URL=https://agridesk.example.com
ALLOWED_ORIGINS=["https://agridesk.example.com"]
STORAGE_BACKEND=supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<service-role-key>
SUPABASE_STORAGE_BUCKET=agridesk-private
```

Set the API project's function memory in Vercel's Functions settings to 2 GB.
The 60-second function duration is configured in `backend/vercel.json`.

## 3. Deploy the frontend

Create a second Vercel project from the same repository with **Root Directory**
set to `frontend`. Configure:

```dotenv
VITE_API_BASE_URL=https://your-api-project.vercel.app
VITE_DIRECT_UPLOADS=true
```

The frontend sends external PDFs directly to Supabase through an API-issued,
time-limited upload URL. The service-role key must never be stored in this
frontend project.

## 4. Cutover checks

1. Register a new student, lecturer, and admin account.
2. Upload an external PDF under 10 MB and place a signature.
3. Complete approval and confirm the final PDF opens.
4. Scan the QR code and confirm the public verification route resolves.
5. Only then attach the production domain to the frontend project and update
   `BASE_URL` plus `ALLOWED_ORIGINS` in the API project.

Old QR codes stop resolving because this deployment intentionally begins with
an empty database.
