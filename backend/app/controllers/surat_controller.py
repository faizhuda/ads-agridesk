import logging
import os
import uuid
from typing import List

from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.domain.surat import Surat
from app.services.surat_service import SuratService
from app.services.audit_service import AuditService
from app.schemas.surat_schema import (
    AjukanSuratRequest,
    TandaTanganDosenRequest,
    RejectSuratRequest,
    SuratResponse,
    SignatureInfo,
    VerifyResponse,
)
from app.utils.dependencies import require_role, get_current_user
from app.database.db import get_db
from app.core.settings import settings
from app.repositories.postgres_audit_log_repository import PostgresAuditLogRepository
from app.repositories.postgres_surat_repository import PostgresSuratRepository
from app.repositories.postgres_signature_repository import PostgresSignatureRepository
from app.repositories.postgres_user_repository import PostgresUserRepository
from app.utils.document_generator import LocalDocumentGenerator

router = APIRouter()
logger = logging.getLogger(__name__)

UPLOAD_DIR = os.path.join(settings.documents_dir, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def _safe_audit_log(
    db: Session,
    event_name: str,
    actor_id: int | None,
    actor_role: str | None,
    target_type: str | None,
    target_id: str | None,
    metadata: dict | None,
):
    try:
        audit_service = AuditService(PostgresAuditLogRepository(db))
        audit_service.log_event(
            event_name=event_name,
            actor_id=actor_id,
            actor_role=actor_role,
            target_type=target_type,
            target_id=target_id,
            metadata=metadata,
            ip_address=None,
        )
    except Exception as exc:
        logger.warning("Failed to write audit log: %s", exc)


def _build_service(db: Session) -> SuratService:
    return SuratService(
        repository=PostgresSuratRepository(db),
        signature_repository=PostgresSignatureRepository(db),
        user_repository=PostgresUserRepository(db),
        document_generator=LocalDocumentGenerator(),
    )


def _surat_to_response(
    surat: Surat,
    db: Session | None = None,
    include_signatures: bool = False,
) -> SuratResponse:
    sigs: list[SignatureInfo] | None = None
    if include_signatures and db is not None:
        sig_repo = PostgresSignatureRepository(db)
        user_repo = PostgresUserRepository(db)
        raw_sigs = sig_repo.find_by_surat_id(surat.surat_id)
        owner_ids = [s.owner_id for s in raw_sigs]
        owners = {u.user_id: u for u in user_repo.find_by_ids(owner_ids)} if owner_ids else {}
        sigs = [
            SignatureInfo(
                signature_id=s.signature_id,
                owner_id=s.owner_id,
                owner_name=owners[s.owner_id].name if s.owner_id in owners else None,
                role=s.role,
                signed=s.is_signed(),
                signed_at=s.signed_at,
            )
            for s in raw_sigs
        ]

    return SuratResponse(
        surat_id=surat.surat_id,
        mahasiswa_id=surat.mahasiswa_id,
        jenis=surat.jenis,
        keperluan=surat.keperluan,
        is_external=surat.is_external,
        file_path=surat.file_path,
        status=surat.status.value,
        document_hash=surat.document_hash,
        pdf_path=surat.pdf_path,
        qr_path=surat.qr_path,
        rejection_reason=surat.rejection_reason,
        created_at=surat.created_at,
        signatures=sigs,
    )


# ------------------------------------------------------------------
# CREATE – internal surat
# ------------------------------------------------------------------


@router.post("/surat", response_model=SuratResponse)
def ajukan_surat(
    request: AjukanSuratRequest,
    db: Session = Depends(get_db),
    user=Depends(require_role("MAHASISWA")),
):
    service = _build_service(db)

    surat = Surat(
        mahasiswa_id=int(user["sub"]),
        jenis=request.jenis,
        keperluan=request.keperluan,
        is_external=request.is_external,
    )
    saved = service.create_surat(surat, dosen_ids=request.dosen_ids)

    _safe_audit_log(
        db=db,
        event_name="SURAT_SUBMIT",
        actor_id=int(user["sub"]),
        actor_role=user.get("role"),
        target_type="SURAT",
        target_id=str(saved.surat_id),
        metadata={
            "jenis": saved.jenis,
            "status": saved.status.value,
            "dosen_ids": request.dosen_ids,
        },
    )

    return _surat_to_response(saved, db, include_signatures=True)


# ------------------------------------------------------------------
# CREATE – upload external surat
# ------------------------------------------------------------------


@router.post("/surat/upload", response_model=SuratResponse)
async def upload_surat_eksternal(
    jenis: str = Form(...),
    keperluan: str = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(require_role("MAHASISWA")),
):
    ext = os.path.splitext(file.filename or "doc.pdf")[1] or ".pdf"
    safe_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, safe_name)
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    service = _build_service(db)

    surat = Surat(
        mahasiswa_id=int(user["sub"]),
        jenis=jenis,
        keperluan=keperluan,
        is_external=True,
        file_path=file_path,
    )
    saved = service.create_surat(surat)

    _safe_audit_log(
        db=db,
        event_name="SURAT_UPLOAD",
        actor_id=int(user["sub"]),
        actor_role=user.get("role"),
        target_type="SURAT",
        target_id=str(saved.surat_id),
        metadata={"jenis": saved.jenis, "file": safe_name},
    )

    return _surat_to_response(saved, db)


# ------------------------------------------------------------------
# LIST – Mahasiswa
# ------------------------------------------------------------------


@router.get("/surat/me", response_model=List[SuratResponse])
def list_surat_mahasiswa(
    db: Session = Depends(get_db),
    user=Depends(require_role("MAHASISWA")),
):
    service = _build_service(db)
    result = service.list_by_mahasiswa(int(user["sub"]))
    return [_surat_to_response(s, db, include_signatures=True) for s in result]


# ------------------------------------------------------------------
# LIST – Dosen
# ------------------------------------------------------------------


@router.get("/surat/pending-dosen", response_model=List[SuratResponse])
def list_pending_dosen(
    db: Session = Depends(get_db),
    user=Depends(require_role("DOSEN")),
):
    service = _build_service(db)
    result = service.list_pending_dosen(int(user["sub"]))
    return [_surat_to_response(s, db, include_signatures=True) for s in result]


@router.get("/surat/history-dosen", response_model=List[SuratResponse])
def list_history_dosen(
    db: Session = Depends(get_db),
    user=Depends(require_role("DOSEN")),
):
    service = _build_service(db)
    result = service.list_history_dosen(int(user["sub"]))
    return [_surat_to_response(s, db, include_signatures=True) for s in result]


# ------------------------------------------------------------------
# LIST – Admin
# ------------------------------------------------------------------


@router.get("/surat/pending-admin", response_model=List[SuratResponse])
def list_pending_admin(
    db: Session = Depends(get_db),
    user=Depends(require_role("ADMIN")),
):
    service = _build_service(db)
    result = service.list_pending_admin()
    return [_surat_to_response(s, db, include_signatures=True) for s in result]


@router.get("/surat/history-admin", response_model=List[SuratResponse])
def list_history_admin(
    db: Session = Depends(get_db),
    user=Depends(require_role("ADMIN")),
):
    service = _build_service(db)
    result = service.list_history_admin()
    return [_surat_to_response(s, db, include_signatures=True) for s in result]


# ------------------------------------------------------------------
# SIGN – Dosen
# ------------------------------------------------------------------


@router.post("/surat/{surat_id}/ttd-dosen")
def tanda_tangan_dosen(
    surat_id: int,
    request: TandaTanganDosenRequest,
    db: Session = Depends(get_db),
    user=Depends(require_role("DOSEN")),
):
    service = _build_service(db)
    updated = service.tanda_tangan_dosen(
        surat_id=surat_id,
        dosen_id=int(user["sub"]),
        image_path=request.image_path,
    )

    _safe_audit_log(
        db=db,
        event_name="SURAT_SIGN_DOSEN",
        actor_id=int(user["sub"]),
        actor_role=user.get("role"),
        target_type="SURAT",
        target_id=str(surat_id),
        metadata={"status": updated.status.value},
    )

    return _surat_to_response(updated, db, include_signatures=True).model_dump()


# ------------------------------------------------------------------
# REJECT – Dosen
# ------------------------------------------------------------------


@router.post("/surat/{surat_id}/reject-dosen")
def reject_dosen(
    surat_id: int,
    request: RejectSuratRequest,
    db: Session = Depends(get_db),
    user=Depends(require_role("DOSEN")),
):
    service = _build_service(db)
    updated = service.reject_dosen(surat_id, int(user["sub"]), request.reason)

    _safe_audit_log(
        db=db,
        event_name="SURAT_REJECT_DOSEN",
        actor_id=int(user["sub"]),
        actor_role=user.get("role"),
        target_type="SURAT",
        target_id=str(surat_id),
        metadata={"status": updated.status.value, "reason": request.reason},
    )

    return {"status": updated.status.value, "rejection_reason": updated.rejection_reason}


# ------------------------------------------------------------------
# APPROVE / REJECT – Admin
# ------------------------------------------------------------------


@router.post("/surat/{surat_id}/approve-admin")
def approve_admin(
    surat_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_role("ADMIN")),
):
    service = _build_service(db)
    updated = service.approve_admin(surat_id)

    _safe_audit_log(
        db=db,
        event_name="SURAT_APPROVE_ADMIN",
        actor_id=int(user["sub"]),
        actor_role=user.get("role"),
        target_type="SURAT",
        target_id=str(surat_id),
        metadata={
            "status": updated.status.value,
            "document_hash": updated.document_hash,
        },
    )

    return {
        "status": updated.status.value,
        "document_hash": updated.document_hash,
        "pdf_path": updated.pdf_path,
        "qr_path": updated.qr_path,
    }


@router.post("/surat/{surat_id}/reject")
def reject_surat(
    surat_id: int,
    request: RejectSuratRequest,
    db: Session = Depends(get_db),
    user=Depends(require_role("ADMIN")),
):
    service = _build_service(db)
    updated = service.reject_surat(surat_id, request.reason)

    _safe_audit_log(
        db=db,
        event_name="SURAT_REJECT",
        actor_id=int(user["sub"]),
        actor_role=user.get("role"),
        target_type="SURAT",
        target_id=str(surat_id),
        metadata={"status": updated.status.value, "reason": request.reason},
    )

    return {"status": updated.status.value, "rejection_reason": updated.rejection_reason}


# ------------------------------------------------------------------
# PUBLIC VERIFICATION
# ------------------------------------------------------------------


@router.get("/verify/{document_hash}", response_model=VerifyResponse)
def verify_surat(
    document_hash: str,
    db: Session = Depends(get_db),
):
    service = _build_service(db)
    surat = service.verify_surat(document_hash)

    _safe_audit_log(
        db=db,
        event_name="SURAT_VERIFY_PUBLIC",
        actor_id=None,
        actor_role=None,
        target_type="DOCUMENT",
        target_id=document_hash,
        metadata={"status": "VALID", "surat_id": surat.surat_id},
    )

    return VerifyResponse(
        status="VALID",
        mahasiswa_id=surat.mahasiswa_id,
        jenis=surat.jenis,
        document_hash=surat.document_hash,
    )