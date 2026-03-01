from abc import ABC, abstractmethod
from typing import List
from app.domain.surat import Surat


class SuratRepository(ABC):

    @abstractmethod
    def save(self, surat: Surat):
        pass

    @abstractmethod
    def find_by_id(self, surat_id: int) -> Surat:
        pass

    @abstractmethod
    def find_by_hash(self, document_hash: str) -> Surat:
        pass

    @abstractmethod
    def find_by_mahasiswa(self, mahasiswa_id: int) -> List[Surat]:
        pass

    @abstractmethod
    def find_by_status(self, status: str) -> List[Surat]:
        pass

    @abstractmethod
    def find_all(self) -> List[Surat]:
        pass