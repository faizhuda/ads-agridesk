from app.domain.surat import Surat
from app.domain.signature import Signature
from app.utils.hash_generator import HashGenerator
from app.repositories.surat_repository import SuratRepository
from app.domain.surat import Surat


class SuratService:

    def __init__(self, repository: SuratRepository):
        self.repository = repository

    def ajukan_surat(self, surat: Surat):
        surat.ajukan()
        return self.repository.save(surat)

    def tanda_tangan_dosen(self, surat_id: int, dosen_id: int, image_path: str):
        surat = self.repository.find_by_id(surat_id)

        if not surat:
            raise Exception("Surat tidak ditemukan")

        signature = Signature(
            owner_id=dosen_id,
            role="DOSEN",
            image_path=image_path
        )

        signature.generate_signature_hash(surat_id)

        surat.tambah_signature_dosen(signature)

        return self.repository.save(surat)

    def approve_admin(self, surat_id: int):
        surat = self.repository.find_by_id(surat_id)

        if not surat:
            raise Exception("Surat tidak ditemukan")

        surat.approve_admin()
        surat.generate_document_hash(surat_id)

        return self.repository.save(surat)