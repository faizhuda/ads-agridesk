from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.domain.enums import UserRole, SuratStatus
from app.models.user import UserModel
from app.schemas.surat_schema import (
    InternalLetterRequest,
    RejectLetterRequest,
    SuratResponse,
)
from app.services.surat_service import SuratService
from app.utils.dependencies import get_current_user, require_role
from app.utils.upload import save_pdf_upload

router = APIRouter(prefix="/api/surat", tags=["Surat"])


# --- Student endpoints ---


@router.post("/internal", response_model=SuratResponse, status_code=status.HTTP_201_CREATED)
def create_internal_letter(
    request: InternalLetterRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_role(UserRole.MAHASISWA)),
):
    service = SuratService(db)
    surat = service.create_internal_letter(
        mahasiswa_id=current_user.id,
        jenis=request.jenis,
        keperluan=request.keperluan,
        fields=request.fields,
        lecturer_ids=request.lecturer_ids,
    )
    return surat


@router.post("/external", response_model=SuratResponse, status_code=status.HTTP_201_CREATED)
def create_external_letter(
    jenis: str = Form(...),
    keperluan: str = Form(...),
    lecturer_ids: str = Form(default=""),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_role(UserRole.MAHASISWA)),
):
    # Validate and save uploaded PDF
    file_path = save_pdf_upload(file, prefix=f"ext_{current_user.id}")

    # Parse lecturer IDs
    lid_list = None
    if lecturer_ids.strip():
        lid_list = [int(x.strip()) for x in lecturer_ids.split(",") if x.strip()]

    service = SuratService(db)
    surat = service.create_external_letter(
        mahasiswa_id=current_user.id,
        jenis=jenis,
        keperluan=keperluan,
        file_path=file_path,
        lecturer_ids=lid_list,
    )
    return surat


@router.post("/{surat_id}/submit", response_model=SuratResponse)
def submit_letter(
    surat_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_role(UserRole.MAHASISWA)),
):
    try:
        service = SuratService(db)
        return service.submit_letter(surat_id, current_user.id)
    except (ValueError, PermissionError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/my", response_model=List[SuratResponse])
def get_my_letters(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_role(UserRole.MAHASISWA)),
):
    service = SuratService(db)
    return service.get_surat_by_mahasiswa(current_user.id)


# --- Admin endpoints ---


@router.get("/pending", response_model=List[SuratResponse])
def get_pending_admin(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_role(UserRole.ADMIN)),
):
    service = SuratService(db)
    return service.get_pending_admin()


@router.post("/{surat_id}/approve", response_model=SuratResponse)
def approve_letter(
    surat_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_role(UserRole.ADMIN)),
):
    try:
        service = SuratService(db)
        return service.approve_by_admin(surat_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{surat_id}/reject", response_model=SuratResponse)
def reject_letter(
    surat_id: int,
    request: RejectLetterRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_role(UserRole.ADMIN, UserRole.DOSEN)),
):
    try:
        service = SuratService(db)
        return service.reject_letter(surat_id, current_user.id, current_user.role.value, request.reason)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# --- General ---


@router.get("/all", response_model=List[SuratResponse])
def get_all_surat(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_role(UserRole.ADMIN)),
):
    service = SuratService(db)
    return service.get_all_surat()


@router.get("/{surat_id}", response_model=SuratResponse)
def get_surat_detail(
    surat_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    service = SuratService(db)
    surat = service.get_surat_by_id(surat_id)
    if not surat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Surat tidak ditemukan")

    # Access control: student can only see own letters
    if current_user.role == UserRole.MAHASISWA and surat.mahasiswa_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Akses ditolak")

    return surat
