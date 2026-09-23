import os
from io import BytesIO
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Query, BackgroundTasks
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.domain.enums import UserRole
from app.domain.user import User
from app.schemas.surat_schema import (
    InternalLetterRequest,
    InternalTemplateResponse,
    RejectLetterRequest,
    SuratResponse,
    PaginatedSuratResponse,
)
from app.services.surat_service import SuratService
from app.utils.dependencies import get_current_user, get_current_user_flexible, require_role
from app.utils.upload import save_pdf_upload
from app.utils.storage import storage_service

router = APIRouter(prefix="/api/surat", tags=["Surat"])


# --- Student endpoints ---


@router.post("/internal", response_model=SuratResponse, status_code=status.HTTP_201_CREATED)
def create_internal_letter(
    request: InternalLetterRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MAHASISWA)),
):
    service = SuratService(db)
    return service.create_internal_letter(
        mahasiswa_id=current_user.id,
        jenis=request.jenis,
        keperluan=request.keperluan,
        fields=request.fields,
        lecturer_ids=request.lecturer_ids,
        background_tasks=background_tasks,
    )


@router.post("/external", response_model=SuratResponse, status_code=status.HTTP_201_CREATED)
def create_external_letter(
    jenis: str = Form(...),
    keperluan: str = Form(...),
    lecturer_ids: str = Form(default=""),
    signer_configs_json: str = Form(default=""),
    is_sequential: bool = Form(default=False),
    file: UploadFile | None = File(default=None),
    storage_key: str | None = Form(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MAHASISWA)),
):
    import json
    if bool(file) == bool(storage_key):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kirim tepat satu sumber PDF: file atau storage_key",
        )

    if storage_key:
        expected_prefix = f"external/{current_user.id}/"
        if not storage_key.startswith(expected_prefix) or not storage_key.endswith(".pdf"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Storage key tidak valid")
        try:
            pdf_bytes = storage_service.get_file_content(storage_key)
            from pypdf import PdfReader
            PdfReader(BytesIO(pdf_bytes))
        except FileNotFoundError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PDF belum ditemukan di Storage")
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File Storage bukan PDF yang valid")
        file_path = storage_key
    else:
        file_path = save_pdf_upload(file, prefix=f"ext_{current_user.id}")

    signer_configs = None
    if signer_configs_json.strip():
        try:
            signer_configs = json.loads(signer_configs_json)
        except (json.JSONDecodeError, ValueError):
            signer_configs = None

    lid_list = None
    if not signer_configs and lecturer_ids.strip():
        lid_list = [int(x.strip()) for x in lecturer_ids.split(",") if x.strip()]

    service = SuratService(db)
    return service.create_external_letter(
        mahasiswa_id=current_user.id,
        jenis=jenis,
        keperluan=keperluan,
        file_path=file_path,
        signer_configs=signer_configs,
        is_sequential=is_sequential,
        lecturer_ids=lid_list,
    )


@router.post("/{surat_id}/submit", response_model=SuratResponse)
def submit_letter(
    surat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MAHASISWA)),
):
    service = SuratService(db)
    return service.submit_letter(surat_id, current_user.id)


@router.get("/my", response_model=PaginatedSuratResponse)
def get_my_letters(
    page: int = Query(1, ge=1),
    size: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MAHASISWA)),
):
    service = SuratService(db)
    skip = (page - 1) * size
    items, total = service.get_surat_by_mahasiswa(current_user.id, skip=skip, limit=size)
    return PaginatedSuratResponse(items=items, total=total, page=page, size=size)


@router.get("/templates/internal", response_model=List[InternalTemplateResponse])
def get_internal_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MAHASISWA)),
):
    service = SuratService(db)
    return service.get_internal_templates()


# --- Admin endpoints ---


@router.get("/pending", response_model=PaginatedSuratResponse)
def get_pending_admin(
    page: int = Query(1, ge=1),
    size: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    service = SuratService(db)
    skip = (page - 1) * size
    items, total = service.get_pending_admin(skip=skip, limit=size)
    return PaginatedSuratResponse(items=items, total=total, page=page, size=size)


@router.post("/{surat_id}/approve", response_model=SuratResponse)
def approve_letter(
    surat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    service = SuratService(db)
    # Vercel functions can stop after a response. Generate the final PDF before
    # returning so an approved document is immediately durable and verifiable.
    return service.approve_by_admin(surat_id, current_user.id)


@router.post("/{surat_id}/reject", response_model=SuratResponse)
def reject_letter(
    surat_id: int,
    request: RejectLetterRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.DOSEN)),
):
    service = SuratService(db)
    return service.reject_letter(
        surat_id, current_user.id, current_user.role.value, request.reason,
    )


# --- General ---
# IMPORTANT: static routes (/all, /public/stats) must come before /{surat_id}
# to prevent FastAPI from matching them as integer path params.


@router.get("/all", response_model=PaginatedSuratResponse)
def get_all_surat(
    page: int = Query(1, ge=1),
    size: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    service = SuratService(db)
    skip = (page - 1) * size
    items, total = service.get_all_surat(skip=skip, limit=size)
    return PaginatedSuratResponse(items=items, total=total, page=page, size=size)


@router.get("/public/stats")
def get_public_stats(db: Session = Depends(get_db)):
    return SuratService(db).get_public_stats()


@router.get("/{surat_id}", response_model=SuratResponse)
def get_surat_detail(
    surat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = SuratService(db)
    return service.get_surat_with_access_check(surat_id, current_user.id, current_user.role)


@router.get("/{surat_id}/page-count")
def get_surat_page_count(
    surat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = SuratService(db)
    count = service.get_page_count(surat_id, current_user.id, current_user.role)
    return {"page_count": count}


@router.get("/{surat_id}/pdf")
def view_surat_pdf(
    surat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_flexible),
):
    service = SuratService(db)
    surat = service.get_surat_with_access_check(surat_id, current_user.id, current_user.role)

    file_key = surat.pdf_path or surat.file_path
    if not file_key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PDF belum tersedia")

    try:
        from app.utils.storage import storage_service
        pdf_bytes = storage_service.get_file_content(file_key)
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File PDF tidak ditemukan di storage")

    from app.repositories.signature_repository import SignatureRepository
    sig_repo = SignatureRepository(db)
    signatures = sig_repo.get_by_surat_id(surat_id)
    signed_sigs = [s for s in signatures if s.is_signed() and s.image_path and s.pos_x is not None and s.pos_y is not None]

    if signed_sigs:
        from app.utils.pdf_generator import PDFGenerator
        pdf_bytes = PDFGenerator.overlay_signatures_on_pdf(
            pdf_path_or_bytes=pdf_bytes,
            signatures=signed_sigs,
            document_hash=surat.document_hash,
        )

    filename = os.path.basename(file_key) if "/" in file_key else file_key
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )
