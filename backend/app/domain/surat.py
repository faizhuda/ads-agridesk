from .status_surat import StatusSurat
from app.utils.hash_generator import HashGenerator

class Surat:

    def __init__(self, mahasiswa_id: int, jenis: str, is_external: bool = False):
        self.mahasiswa_id = mahasiswa_id
        self.jenis = jenis
        self.is_external = is_external
        self.status = StatusSurat.DRAFT
        self.document_hash = None
        self.rejection_reason = None
        self.mahasiswa_signature = None
        self.dosen_signature = None

    def ajukan(self):
        if self.status != StatusSurat.DRAFT:
            raise Exception("Surat sudah diajukan")
        self.status = StatusSurat.MENUNGGU_TTD_DOSEN

    def tambah_signature_mahasiswa(self, signature):
        self.mahasiswa_signature = signature

    def tambah_signature_dosen(self, signature):
        if self.status != StatusSurat.MENUNGGU_TTD_DOSEN:
            raise Exception("Belum bisa tanda tangan dosen")
        self.dosen_signature = signature
        self.status = StatusSurat.MENUNGGU_PROSES_ADMIN

    def generate_document_hash(self, surat_id: int):
        self.document_hash = HashGenerator.generate_document_hash(
            surat_id, self.mahasiswa_id
        )

    def approve_dosen(self):
        if self.status != StatusSurat.MENUNGGU_TTD_DOSEN:
            raise Exception("Tidak bisa approve dosen")
        self.status = StatusSurat.MENUNGGU_PROSES_ADMIN

    def approve_admin(self):
        if self.status != StatusSurat.MENUNGGU_PROSES_ADMIN:
            raise Exception("Tidak bisa approve admin")
        self.status = StatusSurat.SELESAI

    def reject(self, reason: str):
        self.status = StatusSurat.DITOLAK
        self.rejection_reason = reason