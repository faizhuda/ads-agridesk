import os
from typing import List, Optional

from sqlalchemy.orm import Session

from app.config import settings
from app.domain.enums import SuratStatus, UserRole
from app.models.surat import SuratModel
from app.models.signature import SignatureModel
from app.repositories.surat_repository import SuratRepository
from app.repositories.signature_repository import SignatureRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.models.audit_log import AuditLogModel
from app.utils.hash_generator import HashGenerator
from app.utils.qr_generator import QRCodeGenerator
from app.utils.pdf_generator import PDFGenerator


class SuratService:
    def __init__(self, db: Session):
        self.db = db
        self.surat_repo = SuratRepository(db)
        self.signature_repo = SignatureRepository(db)
        self.audit_repo = AuditLogRepository(db)

    def create_internal_letter(
        self,
        mahasiswa_id: int,
        jenis: str,
        keperluan: str,
        fields: dict,
        lecturer_ids: Optional[List[int]] = None,
    ) -> SuratModel:
        # Generate PDF from template
        filename = f"surat_{jenis}_{mahasiswa_id}.pdf"
        pdf_path = PDFGenerator.generate_from_template(jenis, fields, filename)

        status = SuratStatus.DRAFT
        if lecturer_ids:
            status = SuratStatus.MENUNGGU_TTD_DOSEN

        surat = SuratModel(
            mahasiswa_id=mahasiswa_id,
            jenis=jenis,
            keperluan=keperluan,
            is_external=False,
            pdf_path=pdf_path,
            status=status,
        )
        surat = self.surat_repo.create(surat)

        # Create signature placeholders for lecturers
        if lecturer_ids:
            for lid in lecturer_ids:
                sig = SignatureModel(
                    surat_id=surat.id,
                    owner_id=lid,
                    role=UserRole.DOSEN,
                )
                self.signature_repo.create(sig)

        self._log_event("SURAT_CREATED", mahasiswa_id, UserRole.MAHASISWA.value, surat.id, status.value)
        return surat

    def create_external_letter(
        self,
        mahasiswa_id: int,
        jenis: str,
        keperluan: str,
        file_path: str,
        lecturer_ids: Optional[List[int]] = None,
    ) -> SuratModel:
        status = SuratStatus.DRAFT
        if lecturer_ids:
            status = SuratStatus.MENUNGGU_TTD_DOSEN

        surat = SuratModel(
            mahasiswa_id=mahasiswa_id,
            jenis=jenis,
            keperluan=keperluan,
            is_external=True,
            file_path=file_path,
            status=status,
        )
        surat = self.surat_repo.create(surat)

        if lecturer_ids:
            for lid in lecturer_ids:
                sig = SignatureModel(
                    surat_id=surat.id,
                    owner_id=lid,
                    role=UserRole.DOSEN,
                )
                self.signature_repo.create(sig)

        self._log_event("SURAT_CREATED", mahasiswa_id, UserRole.MAHASISWA.value, surat.id, status.value)
        return surat

    def submit_letter(self, surat_id: int, mahasiswa_id: int) -> SuratModel:
        surat = self._get_surat_or_raise(surat_id)
        if surat.mahasiswa_id != mahasiswa_id:
            raise PermissionError("Bukan surat Anda")

        # Check if any lecturer signatures are needed
        unsigned = self.signature_repo.get_unsigned_by_surat(surat_id)
        lecturer_sigs = [s for s in unsigned if s.role == UserRole.DOSEN]

        if lecturer_sigs:
            surat.status = SuratStatus.MENUNGGU_TTD_DOSEN
        else:
            surat.status = SuratStatus.MENUNGGU_PROSES_ADMIN

        surat = self.surat_repo.update(surat)
        self._log_event("SURAT_SUBMITTED", mahasiswa_id, UserRole.MAHASISWA.value, surat.id, surat.status.value)
        return surat

    def approve_by_admin(self, surat_id: int, admin_id: int) -> SuratModel:
        surat = self._get_surat_or_raise(surat_id)
        if surat.status != SuratStatus.MENUNGGU_PROSES_ADMIN:
            raise ValueError("Surat tidak dalam status menunggu proses admin")

        # Generate document hash
        document_hash = HashGenerator.generate_document_hash(surat.id, surat.mahasiswa_id)
        surat.document_hash = document_hash

        # Generate QR code
        verification_url = f"/verify/{document_hash}"
        qr_filename = f"qr_{surat.id}.png"
        qr_path = QRCodeGenerator.generate_qr_code(verification_url, qr_filename)
        surat.qr_path = qr_path

        # Generate final PDF
        source_pdf = surat.pdf_path or surat.file_path or ""
        final_filename = f"final_{surat.id}.pdf"
        final_pdf_path = PDFGenerator.generate_final_pdf(source_pdf, qr_path, final_filename)
        surat.pdf_path = final_pdf_path

        surat.status = SuratStatus.SELESAI
        surat = self.surat_repo.update(surat)

        self._log_event("SURAT_APPROVED", admin_id, UserRole.ADMIN.value, surat.id, surat.status.value)
        return surat

    def reject_letter(self, surat_id: int, actor_id: int, actor_role: str, reason: str) -> SuratModel:
        surat = self._get_surat_or_raise(surat_id)
        surat.status = SuratStatus.DITOLAK
        surat.rejection_reason = reason
        surat = self.surat_repo.update(surat)

        self._log_event("SURAT_REJECTED", actor_id, actor_role, surat.id, surat.status.value)
        return surat

    def get_surat_by_id(self, surat_id: int) -> Optional[SuratModel]:
        return self.surat_repo.get_by_id(surat_id)

    def get_surat_by_mahasiswa(self, mahasiswa_id: int) -> List[SuratModel]:
        return self.surat_repo.get_by_mahasiswa_id(mahasiswa_id)

    def get_pending_admin(self) -> List[SuratModel]:
        return self.surat_repo.get_pending_admin()

    def get_all_surat(self) -> List[SuratModel]:
        return self.surat_repo.get_all()

    def _get_surat_or_raise(self, surat_id: int) -> SuratModel:
        surat = self.surat_repo.get_by_id(surat_id)
        if not surat:
            raise ValueError("Surat tidak ditemukan")
        return surat

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
