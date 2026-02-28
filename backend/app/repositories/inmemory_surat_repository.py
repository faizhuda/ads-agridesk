from app.repositories.surat_repository import SuratRepository
from app.domain.surat import Surat


class InMemorySuratRepository(SuratRepository):

    def __init__(self):
        self.storage = {}

    def save(self, surat: Surat):
        surat_id = id(surat)
        self.storage[surat_id] = surat
        return surat

    def find_by_id(self, surat_id: int) -> Surat:
        return self.storage.get(surat_id)

    def find_by_hash(self, document_hash: str) -> Surat:
        for surat in self.storage.values():
            if surat.document_hash == document_hash:
                return surat
        return None