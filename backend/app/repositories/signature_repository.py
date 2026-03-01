from abc import ABC, abstractmethod
from typing import List

from app.domain.signature import Signature


class SignatureRepository(ABC):

    @abstractmethod
    def save(self, surat_id: int, signature: Signature) -> Signature:
        pass

    @abstractmethod
    def update(self, signature: Signature) -> Signature:
        pass

    @abstractmethod
    def find_by_surat_id(self, surat_id: int) -> List[Signature]:
        pass

    @abstractmethod
    def find_by_surat_and_owner(self, surat_id: int, owner_id: int) -> Signature | None:
        pass

    @abstractmethod
    def find_pending_by_owner(self, owner_id: int) -> List[Signature]:
        pass

    @abstractmethod
    def find_signed_by_owner(self, owner_id: int) -> List[Signature]:
        pass
