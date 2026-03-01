from __future__ import annotations

from typing import List

from app.domain.surat import Surat
from app.domain.signature import Signature
from app.domain.status_surat import StatusSurat
from app.domain.exceptions import (
    DomainException,
    SuratNotFoundException,
    InvalidDocumentError,
    InvalidStatusTransitionError,
)
from app.repositories.surat_repository import SuratRepository
from app.repositories.signature_repository import SignatureRepository
from app.repositories.user_repository import UserRepository
from app.utils.hash_generator import HashGenerator
from app.utils.document_generator import LocalDocumentGenerator


class SuratService:
    """Orchestrates the full academic-letter lifecycle.

    Supports:
    - Internal surat with optional multi-dosen signature stage
    - External surat (file upload, straight to dosen/admin stages)
    - Dosen sign / reject
    - Admin approve / reject
    - Public verification
    - History queries per role
    """

    def __init__(
        self,
        repository: SuratRepository,
        signature_repository: SignatureRepository | None = None,
        user_repository: UserRepository | None = None,
        document_generator: LocalDocumentGenerator | None = None,
    ):
        self.repository = repository
        self.signature_repository = signature_repository
        self.user_repository = user_repository
        self.document_generator = document_generator

    # ------------------------------------------------------------------
    # Creation
    # ------------------------------------------------------------------

    def create_surat(
        self,
        surat: Surat,
        dosen_ids: list[int] | None = None,
    ) -> Surat:
        """Create an internal or external surat.

        *dosen_ids* – if provided, creates pending signature records and sets
        status to ``MENUNGGU_TTD_DOSEN``.  If empty/None the letter skips to
        ``MENUNGGU_PROSES_ADMIN``.
        """
        requires_dosen = bool(dosen_ids)

        # Validate selected dosen exist and have DOSEN role
        if requires_dosen and self.user_repository:
            users = self.user_repository.find_by_ids(dosen_ids)
            found_ids = {u.user_id for u in users}
            for did in dosen_ids:
                if did not in found_ids:
                    raise DomainException(f"Dosen dengan ID {did} tidak ditemukan", 404)
            for u in users:
                if u.role.value != "DOSEN":
                    raise DomainException(
                        f"User {u.name} bukan DOSEN", 400
                    )

        surat.ajukan(requires_dosen=requires_dosen)

        # Generate initial PDF
        if self.document_generator:
            pdf_path = self.document_generator.generate_surat_pdf(surat)
            surat.set_pdf_path(pdf_path)

        saved = self.repository.save(surat)

        # Create pending signature records
        if requires_dosen and self.signature_repository:
            for dosen_id in dosen_ids:
                sig = Signature(owner_id=dosen_id, role="DOSEN")
                self.signature_repository.save(saved.surat_id, sig)

        return saved

    # Backward-compatible alias used by tests / simple paths
    def ajukan_surat(self, surat: Surat) -> Surat:
        return self.create_surat(surat)

    # ------------------------------------------------------------------
    # Dosen stage
    # ------------------------------------------------------------------

    def tanda_tangan_dosen(
        self,
        surat_id: int,
        dosen_id: int,
        image_path: str,
    ) -> Surat:
        """Sign a surat as dosen.

        After all required dosen have signed the status transitions to
        ``MENUNGGU_PROSES_ADMIN``.
        """
        surat = self._get_surat(surat_id)

        if surat.status != StatusSurat.MENUNGGU_TTD_DOSEN:
            raise InvalidStatusTransitionError(
                "Surat tidak dalam tahap tanda tangan dosen"
            )

        signature_hash = HashGenerator.generate_signature_hash(surat_id, dosen_id)

        if self.signature_repository:
            # Multi-dosen path: find the pending record for this dosen
            sig = self.signature_repository.find_by_surat_and_owner(surat_id, dosen_id)
            if sig is None:
                raise DomainException(
                    "Anda tidak ditugaskan untuk menandatangani surat ini", 403
                )
            if sig.is_signed():
                raise DomainException("Anda sudah menandatangani surat ini", 400)

            sig.sign(image_path, signature_hash)
            self.signature_repository.update(sig)

            # Check if all signatures are complete
            all_sigs = self.signature_repository.find_by_surat_id(surat_id)
            if all(s.is_signed() for s in all_sigs):
                surat.advance_to_admin()

            # Regenerate PDF with signatures
            if self.document_generator:
                pdf_path = self.document_generator.generate_surat_pdf(
                    surat, signatures=all_sigs
                )
                surat.set_pdf_path(pdf_path)
        else:
            # Simple single-dosen path (unit-test fallback)
            surat.advance_to_admin()

        return self.repository.save(surat)

    def reject_dosen(self, surat_id: int, dosen_id: int, reason: str) -> Surat:
        """Dosen rejects the surat."""
        surat = self._get_surat(surat_id)

        if surat.status != StatusSurat.MENUNGGU_TTD_DOSEN:
            raise InvalidStatusTransitionError(
                "Surat tidak dalam tahap tanda tangan dosen"
            )

        if self.signature_repository:
            sig = self.signature_repository.find_by_surat_and_owner(surat_id, dosen_id)
            if sig is None:
                raise DomainException(
                    "Anda tidak ditugaskan untuk menandatangani surat ini", 403
                )

        surat.reject(reason)
        return self.repository.save(surat)

    # ------------------------------------------------------------------
    # Admin stage
    # ------------------------------------------------------------------

    def approve_admin(self, surat_id: int) -> Surat:
        surat = self._get_surat(surat_id)
        surat.approve_admin()

        document_hash = HashGenerator.generate_document_hash(
            surat_id, surat.mahasiswa_id
        )
        surat.set_document_hash(document_hash)

        if self.document_generator:
            qr_path = self.document_generator.generate_verification_qr(
                document_hash, surat_id
            )
            surat.set_qr_path(qr_path)

            signatures: list[Signature] = []
            if self.signature_repository:
                signatures = self.signature_repository.find_by_surat_id(surat_id)

            pdf_path = self.document_generator.generate_surat_pdf(
                surat, signatures=signatures
            )
            surat.set_pdf_path(pdf_path)

        return self.repository.save(surat)

    def reject_surat(self, surat_id: int, reason: str) -> Surat:
        """Admin rejects the surat."""
        surat = self._get_surat(surat_id)
        surat.reject(reason)
        return self.repository.save(surat)

    # ------------------------------------------------------------------
    # Verification
    # ------------------------------------------------------------------

    def verify_surat(self, document_hash: str) -> Surat:
        surat = self.repository.find_by_hash(document_hash)

        if not surat:
            raise InvalidDocumentError("Dokumen tidak terdaftar")

        if not surat.is_verified():
            raise InvalidDocumentError("Surat belum final atau tidak sah")

        return surat

    # ------------------------------------------------------------------
    # List / History queries
    # ------------------------------------------------------------------

    def list_by_mahasiswa(self, mahasiswa_id: int) -> List[Surat]:
        return self.repository.find_by_mahasiswa(mahasiswa_id)

    def list_by_status(self, status: str) -> List[Surat]:
        return self.repository.find_by_status(status)

    def list_pending_dosen(self, dosen_id: int) -> List[Surat]:
        """Surat that still require a signature from *dosen_id*."""
        if not self.signature_repository:
            return []
        pending = self.signature_repository.find_pending_by_owner(dosen_id)
        surat_ids = list({sig.surat_id for sig in pending})
        return [
            s
            for sid in surat_ids
            if (s := self.repository.find_by_id(sid)) is not None
        ]

    def list_history_dosen(self, dosen_id: int) -> List[Surat]:
        """Surat where *dosen_id* has already signed."""
        if not self.signature_repository:
            return []
        signed = self.signature_repository.find_signed_by_owner(dosen_id)
        surat_ids = list({sig.surat_id for sig in signed})
        return [
            s
            for sid in surat_ids
            if (s := self.repository.find_by_id(sid)) is not None
        ]

    def list_pending_admin(self) -> List[Surat]:
        return self.repository.find_by_status(StatusSurat.MENUNGGU_PROSES_ADMIN.value)

    def list_history_admin(self) -> List[Surat]:
        return self.repository.find_all()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_surat(self, surat_id: int) -> Surat:
        surat = self.repository.find_by_id(surat_id)
        if not surat:
            raise SuratNotFoundException()
        return surat