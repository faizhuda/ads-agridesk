from typing import List

from app.repositories.surat_repository import SuratRepository
from app.domain.surat import Surat


class InMemorySuratRepository(SuratRepository):

    def __init__(self):
        self.storage = {}
        self._next_id = 1

    def save(self, surat: Surat):
        if surat.surat_id is None:
            surat.surat_id = self._next_id
            self._next_id += 1
        self.storage[surat.surat_id] = surat
        return surat

    def find_by_id(self, surat_id: int) -> Surat:
        return self.storage.get(surat_id)

    def find_by_hash(self, document_hash: str) -> Surat:
        for surat in self.storage.values():
            if surat.document_hash == document_hash:
                return surat
        return None

    def find_by_mahasiswa(self, mahasiswa_id: int) -> List[Surat]:
        return [s for s in self.storage.values() if s.mahasiswa_id == mahasiswa_id]

    def find_by_status(self, status: str) -> List[Surat]:
        return [s for s in self.storage.values() if s.status.value == status]

    def find_all(self) -> List[Surat]:
        return list(self.storage.values())