import os
import uuid
from typing import Set

from fastapi import HTTPException, UploadFile, status

from app.config import settings

ALLOWED_PDF_EXTENSIONS: Set[str] = {".pdf"}
ALLOWED_IMAGE_EXTENSIONS: Set[str] = {".png", ".jpg", ".jpeg"}

ALLOWED_PDF_MIMES: Set[str] = {"application/pdf"}
ALLOWED_IMAGE_MIMES: Set[str] = {"image/png", "image/jpeg"}

MAX_PDF_SIZE: int = 10 * 1024 * 1024  # 10 MB
MAX_IMAGE_SIZE: int = 2 * 1024 * 1024  # 2 MB


def _get_extension(filename: str | None) -> str:
    if not filename:
        return ""
    return os.path.splitext(filename)[1].lower()


def _validate_upload(
    file: UploadFile,
    allowed_extensions: Set[str],
    allowed_mimes: Set[str],
    max_size: int,
) -> bytes:
    ext = _get_extension(file.filename)
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ekstensi file tidak diizinkan. Gunakan: {', '.join(allowed_extensions)}",
        )

    content_type = file.content_type or ""
    if content_type not in allowed_mimes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipe MIME tidak diizinkan: {content_type}",
        )

    data = file.file.read()
    if len(data) > max_size:
        max_mb = max_size / (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ukuran file melebihi batas maksimum ({max_mb:.0f} MB)",
        )

    return data


def _safe_filename(prefix: str, ext: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}{ext}"


def save_pdf_upload(file: UploadFile, prefix: str, subdir: str = "external") -> str:
    data = _validate_upload(file, ALLOWED_PDF_EXTENSIONS, ALLOWED_PDF_MIMES, MAX_PDF_SIZE)
    ext = _get_extension(file.filename)
    upload_dir = os.path.join(settings.UPLOAD_DIR, subdir)
    os.makedirs(upload_dir, exist_ok=True)
    filename = _safe_filename(prefix, ext)
    filepath = os.path.join(upload_dir, filename)
    with open(filepath, "wb") as f:
        f.write(data)
    return filepath


def save_signature_upload(file: UploadFile, prefix: str) -> str:
    data = _validate_upload(file, ALLOWED_IMAGE_EXTENSIONS, ALLOWED_IMAGE_MIMES, MAX_IMAGE_SIZE)
    ext = _get_extension(file.filename)
    upload_dir = os.path.join(settings.UPLOAD_DIR, "signatures")
    os.makedirs(upload_dir, exist_ok=True)
    filename = _safe_filename(prefix, ext)
    filepath = os.path.join(upload_dir, filename)
    with open(filepath, "wb") as f:
        f.write(data)
    return filepath
