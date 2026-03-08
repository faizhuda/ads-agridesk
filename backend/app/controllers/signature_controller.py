from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.domain.enums import UserRole
from app.models.user import UserModel
from app.schemas.signature_schema import SignatureResponse
from app.services.signature_service import SignatureService
from app.utils.dependencies import get_current_user, require_role
from app.utils.upload import save_signature_upload

router = APIRouter(prefix="/api/signatures", tags=["Signatures"])


@router.post("/student/{surat_id}", response_model=SignatureResponse, status_code=status.HTTP_201_CREATED)
def add_student_signature(
    surat_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_role(UserRole.MAHASISWA)),
):
    # Validate and save signature image
    image_path = save_signature_upload(file, prefix=f"student_{current_user.id}_{surat_id}")

    service = SignatureService(db)
    return service.add_student_signature(surat_id, current_user.id, image_path)


@router.post("/lecturer/{signature_id}/sign", response_model=SignatureResponse)
def sign_by_lecturer(
    signature_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_role(UserRole.DOSEN)),
):
    # Validate and save signature image
    image_path = save_signature_upload(file, prefix=f"lecturer_{current_user.id}_{signature_id}")

    try:
        service = SignatureService(db)
        return service.sign_by_lecturer(signature_id, current_user.id, image_path)
    except (ValueError, PermissionError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/pending", response_model=List[SignatureResponse])
def get_pending_signatures(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_role(UserRole.DOSEN)),
):
    service = SignatureService(db)
    return service.get_pending_for_lecturer(current_user.id)


@router.get("/surat/{surat_id}", response_model=List[SignatureResponse])
def get_signatures_for_surat(
    surat_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    service = SignatureService(db)
    return service.get_signatures_for_surat(surat_id)
