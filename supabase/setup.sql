-- Run once in Supabase SQL Editor before deploying the API.
-- All files are private. The FastAPI server uses the service-role key and
-- clients receive only narrowly scoped, time-limited upload URLs.
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values (
  'agridesk-private',
  'agridesk-private',
  false,
  10485760,
  array['application/pdf', 'image/png', 'image/jpeg']
)
on conflict (id) do update
set public = excluded.public,
    file_size_limit = excluded.file_size_limit,
    allowed_mime_types = excluded.allowed_mime_types;
