import os
import uuid
from abc import ABC, abstractmethod
from urllib.parse import quote, urljoin

import httpx

from app.config import settings


class StorageBackend(ABC):
    @abstractmethod
    def upload_file(self, file_content: bytes, original_filename: str) -> str: ...

    @abstractmethod
    def get_file_content(self, path_or_key: str) -> bytes: ...

    @abstractmethod
    def file_exists(self, path_or_key: str) -> bool: ...

    def create_signed_upload_url(self, object_key: str) -> str:
        raise NotImplementedError("Direct upload is only available with Supabase Storage")


class StorageService(StorageBackend):
    """
    Local-filesystem storage service.

    Files are stored under UPLOAD_DIR (default: "uploads/").
    USE_S3 is intentionally kept as a no-op flag so that the old
    environment variable doesn't cause a startup error, but we no
    longer connect to MinIO / S3 at all — the mini-pc stores
    everything on /disk/data-01/tristan/data-agd/uploads via a
    Docker bind-mount into /app/uploads inside the container.
    """

    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR or "uploads"
        os.makedirs(self.upload_dir, exist_ok=True)

    def upload_file(self, file_content: bytes, original_filename: str) -> str:
        """Save *file_content* to the upload directory and return the relative path."""
        ext = original_filename.split(".")[-1] if "." in original_filename else "bin"
        filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(self.upload_dir, filename)
        with open(filepath, "wb") as f:
            f.write(file_content)
        return filepath

    def get_file_content(self, path_or_key: str) -> bytes:
        """Return the raw bytes for the given file path."""
        upload_dir_real = os.path.realpath(os.path.abspath(self.upload_dir))

        # Resolve the requested path relative to the upload dir.
        # Never strip or ignore leading slashes before the traversal check —
        # doing so would allow "/etc/passwd" to be silently rewritten to
        # "uploads/etc/passwd" and bypass the guard below.
        if os.path.isabs(path_or_key):
            filepath = os.path.realpath(os.path.abspath(path_or_key))
        elif path_or_key.startswith(self.upload_dir + os.sep) or path_or_key == self.upload_dir:
            filepath = os.path.realpath(os.path.abspath(path_or_key))
        else:
            filepath = os.path.realpath(os.path.abspath(os.path.join(self.upload_dir, path_or_key)))

        # Path traversal guard: resolved path must be inside upload_dir.
        if not filepath.startswith(upload_dir_real + os.sep) and filepath != upload_dir_real:
            raise PermissionError("Access denied: path resolves outside upload directory")

        if os.path.exists(filepath):
            with open(filepath, "rb") as f:
                return f.read()

        raise FileNotFoundError(f"File not found in storage: {path_or_key}")

    def file_exists(self, path_or_key: str) -> bool:
        """Return True if the file exists on disk."""
        try:
            self.get_file_content(path_or_key)
            return True
        except FileNotFoundError:
            return False


class SupabaseStorageService(StorageBackend):
    """Private Supabase Storage adapter used by the serverless deployment."""

    def __init__(self):
        self.base_url = settings.SUPABASE_URL.rstrip("/")
        self.bucket = settings.SUPABASE_STORAGE_BUCKET
        self.headers = {
            "apikey": settings.SUPABASE_SERVICE_ROLE_KEY,
            "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
        }

    def _object_url(self, object_key: str, authenticated: bool = False) -> str:
        key = quote(object_key.lstrip("/"), safe="/")
        kind = "authenticated/" if authenticated else ""
        return f"{self.base_url}/storage/v1/object/{kind}{self.bucket}/{key}"

    def upload_file(self, file_content: bytes, original_filename: str) -> str:
        ext = original_filename.rsplit(".", 1)[-1].lower() if "." in original_filename else "bin"
        object_key = f"generated/{uuid.uuid4().hex}.{ext}"
        headers = {**self.headers, "content-type": _content_type_for_extension(ext), "x-upsert": "false"}
        response = httpx.post(self._object_url(object_key), content=file_content, headers=headers, timeout=60)
        response.raise_for_status()
        return object_key

    def get_file_content(self, path_or_key: str) -> bytes:
        response = httpx.get(self._object_url(path_or_key, authenticated=True), headers=self.headers, timeout=60)
        if response.status_code == 404:
            raise FileNotFoundError(f"File not found in Supabase Storage: {path_or_key}")
        response.raise_for_status()
        return response.content

    def file_exists(self, path_or_key: str) -> bool:
        response = httpx.head(self._object_url(path_or_key, authenticated=True), headers=self.headers, timeout=30)
        if response.status_code == 404:
            return False
        response.raise_for_status()
        return True

    def create_signed_upload_url(self, object_key: str) -> str:
        key = quote(object_key.lstrip("/"), safe="/")
        endpoint = f"{self.base_url}/storage/v1/object/upload/sign/{self.bucket}/{key}"
        response = httpx.post(endpoint, json={}, headers=self.headers, timeout=30)
        response.raise_for_status()
        relative_url = response.json().get("url")
        if not relative_url:
            raise RuntimeError("Supabase did not return a signed upload URL")
        return urljoin(f"{self.base_url}/storage/v1/", relative_url.lstrip("/"))


def _content_type_for_extension(extension: str) -> str:
    return {
        "pdf": "application/pdf",
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
    }.get(extension, "application/octet-stream")


storage_service: StorageBackend = (
    SupabaseStorageService()
    if settings.STORAGE_BACKEND.lower() == "supabase"
    else StorageService()
)
