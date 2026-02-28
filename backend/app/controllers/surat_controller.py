from fastapi import APIRouter, Depends
from app.domain.surat import Surat
from app.services.surat_service import SuratService
from app.repositories.inmemory_surat_repository import InMemorySuratRepository
from app.utils.dependencies import require_role


router = APIRouter()

# temporary setup (nanti bisa pakai dependency injection)
repository = InMemorySuratRepository()
service = SuratService(repository)


@router.post("/surat")
def ajukan_surat(
    mahasiswa_id: int,
    jenis: str,
    user=Depends(require_role("MAHASISWA"))
):
    surat = Surat(mahasiswa_id=mahasiswa_id, jenis=jenis)
    saved = service.ajukan_surat(surat)
    return {
        "surat_id": id(saved),
        "status": saved.status
    }


@router.post("/surat/{surat_id}/ttd-dosen")
def tanda_tangan_dosen(
    surat_id: int,
    dosen_id: int,
    user=Depends(require_role("DOSEN"))
):
    updated = service.tanda_tangan_dosen(
        surat_id=surat_id,
        dosen_id=dosen_id,
        image_path="dummy_path.png"
    )
    return {"status": updated.status}


@router.post("/surat/{surat_id}/approve-admin")
def approve_admin(
    surat_id: int,
    user=Depends(require_role("ADMIN"))
):
    updated = service.approve_admin(surat_id)
    return {
        "status": updated.status,
        "document_hash": updated.document_hash
    }

@router.get("/verify/{document_hash}")
def verify_surat(document_hash: str):
    surat = repository.find_by_hash(document_hash)

    if not surat:
        return {
            "status": "INVALID",
            "message": "Dokumen tidak terdaftar"
        }

    if surat.status.value != "SELESAI":
        return {
            "status": "INVALID",
            "message": "Surat belum final atau tidak sah"
        }

    return {
        "status": "VALID",
        "mahasiswa_id": surat.mahasiswa_id,
        "jenis": surat.jenis,
        "document_hash": surat.document_hash
    }

