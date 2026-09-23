import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app.domain.enums import UserRole
from app.domain.user import User
from app.schemas.storage_schema import ExternalPdfUploadRequest, SignedUploadResponse
from app.utils.dependencies import require_role
from app.utils.storage import storage_service


router = APIRouter(prefix="/api/storage", tags=["Storage"])


@router.post("/external-pdf-upload", response_model=SignedUploadResponse)
def create_external_pdf_upload_url(
    body: ExternalPdfUploadRequest,
    current_user: User = Depends(require_role(UserRole.MAHASISWA)),
):
    """Issue a one-time URL so PDFs never transit through Vercel Functions."""
    if body.content_type != "application/pdf":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Hanya PDF yang diizinkan")

    object_key = f"external/{current_user.id}/{uuid.uuid4().hex}.pdf"
    try:
        upload_url = storage_service.create_signed_upload_url(object_key)
    except NotImplementedError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Direct upload hanya tersedia saat Supabase Storage diaktifkan",
        )
    return SignedUploadResponse(object_key=object_key, upload_url=upload_url)
