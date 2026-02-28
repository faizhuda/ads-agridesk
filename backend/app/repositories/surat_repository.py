from abc import ABC, abstractmethod
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