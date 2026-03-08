from datetime import datetime, timezone
from typing import List

from sqlalchemy.orm import Session

from app.domain.enums import SuratStatus, UserRole
from app.models.signature import SignatureModel
from app.repositories.signature_repository import SignatureRepository
from app.repositories.surat_repository import SuratRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.models.audit_log import AuditLogModel
from app.utils.hash_generator import HashGenerator


class SignatureService:
    def __init__(self, db: Session):
        self.db = db
        self.signature_repo = SignatureRepository(db)
        self.surat_repo = SuratRepository(db)
        self.audit_repo = AuditLogRepository(db)

    def add_student_signature(
        self,
        surat_id: int,
        student_id: int,
        image_path: str,
    ) -> SignatureModel:
        signature = SignatureModel(
            surat_id=surat_id,
            owner_id=student_id,
            role=UserRole.MAHASISWA,
            image_path=image_path,
            signed_at=datetime.now(timezone.utc),
            signature_hash=HashGenerator.generate_hash(f"{surat_id}:{student_id}:MAHASISWA"),
        )
        return self.signature_repo.create(signature)

    def sign_by_lecturer(
        self,
        signature_id: int,
        lecturer_id: int,
        image_path: str,
    ) -> SignatureModel:
        signature = self.signature_repo.get_by_id(signature_id)
        if not signature:
            raise ValueError("Signature record tidak ditemukan")
        if signature.owner_id != lecturer_id:
            raise PermissionError("Bukan tanda tangan Anda")
        if signature.signed_at is not None:
            raise ValueError("Sudah ditandatangani")

        signature.image_path = image_path
        signature.signed_at = datetime.now(timezone.utc)
        signature.signature_hash = HashGenerator.generate_hash(
            f"{signature.surat_id}:{lecturer_id}:DOSEN"
        )
        signature = self.signature_repo.update(signature)

        # Check if all lecturers have signed
        if self.check_all_lecturers_signed(signature.surat_id):
            surat = self.surat_repo.get_by_id(signature.surat_id)
            if surat and surat.status == SuratStatus.MENUNGGU_TTD_DOSEN:
                surat.status = SuratStatus.MENUNGGU_PROSES_ADMIN
                self.surat_repo.update(surat)

        self._log_event(
            "SIGNATURE_ADDED",
            lecturer_id,
            UserRole.DOSEN.value,
            signature.surat_id,
            "SIGNED",
        )
        return signature

    def check_all_lecturers_signed(self, surat_id: int) -> bool:
        unsigned = self.signature_repo.get_unsigned_by_surat(surat_id)
        lecturer_unsigned = [s for s in unsigned if s.role == UserRole.DOSEN]
        return len(lecturer_unsigned) == 0

    def get_pending_for_lecturer(self, lecturer_id: int) -> List[SignatureModel]:
        return self.signature_repo.get_pending_for_lecturer(lecturer_id)

    def get_signed_for_lecturer(self, lecturer_id: int) -> List[SignatureModel]:
        return self.signature_repo.get_signed_for_lecturer(lecturer_id)

    def get_signatures_for_surat(self, surat_id: int) -> List[SignatureModel]:
        return self.signature_repo.get_by_surat_id(surat_id)

    def _log_event(self, event: str, actor_id: int, actor_role: str, surat_id: int, status: str):
        log = AuditLogModel(
            event_name=event,
            actor_id=actor_id,
            actor_role=actor_role,
            target_type="surat",
            target_id=surat_id,
            status=status,
        )
        self.audit_repo.create(log)
