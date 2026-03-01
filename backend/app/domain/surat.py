from .status_surat import StatusSurat
from .exceptions import InvalidStatusTransitionError


class Surat:
    """Domain entity representing an academic letter (surat).

    Supports both internal (template-based) and external (uploaded) letters.
    Internal letters may require one or more dosen signatures before admin
    approval.
    """

    def __init__(
        self,
        mahasiswa_id: int,
        jenis: str,
        is_external: bool = False,
        keperluan: str | None = None,
        file_path: str | None = None,
    ):
        self.surat_id: int | None = None
        self.mahasiswa_id = mahasiswa_id
        self.jenis = jenis
        self.is_external = is_external
        self.keperluan = keperluan
        self.file_path = file_path
        self.status = StatusSurat.DRAFT
        self.document_hash: str | None = None
        self.pdf_path: str | None = None
        self.qr_path: str | None = None
        self.rejection_reason: str | None = None
        self.created_at = None
        self.updated_at = None

    # ------------------------------------------------------------------
    # Status transitions
    # ------------------------------------------------------------------

    def ajukan(self, requires_dosen: bool = True):
        """Submit the surat.

        If *requires_dosen* is True the letter enters the dosen-signing
        stage; otherwise it skips directly to admin review.
        """
        if self.status != StatusSurat.DRAFT:
            raise InvalidStatusTransitionError("Surat sudah diajukan")
        if requires_dosen:
            self.status = StatusSurat.MENUNGGU_TTD_DOSEN
        else:
            self.status = StatusSurat.MENUNGGU_PROSES_ADMIN

    def advance_to_admin(self):
        """Transition to admin stage after all dosen have signed."""
        if self.status != StatusSurat.MENUNGGU_TTD_DOSEN:
            raise InvalidStatusTransitionError(
                "Surat tidak dalam tahap tanda tangan dosen"
            )
        self.status = StatusSurat.MENUNGGU_PROSES_ADMIN

    def approve_admin(self):
        if self.status != StatusSurat.MENUNGGU_PROSES_ADMIN:
            raise InvalidStatusTransitionError("Tidak bisa approve admin")
        self.status = StatusSurat.SELESAI

    def reject(self, reason: str):
        self.status = StatusSurat.DITOLAK
        self.rejection_reason = reason

    # ------------------------------------------------------------------
    # Asset setters
    # ------------------------------------------------------------------

    def set_document_hash(self, document_hash: str):
        self.document_hash = document_hash

    def set_pdf_path(self, pdf_path: str):
        self.pdf_path = pdf_path

    def set_qr_path(self, qr_path: str):
        self.qr_path = qr_path

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def is_verified(self) -> bool:
        return self.status == StatusSurat.SELESAI and self.document_hash is not None