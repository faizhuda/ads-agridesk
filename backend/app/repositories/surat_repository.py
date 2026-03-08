from typing import Optional, List

from sqlalchemy.orm import Session

from app.models.surat import SuratModel
from app.domain.enums import SuratStatus


class SuratRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, surat: SuratModel) -> SuratModel:
        self.db.add(surat)
        self.db.commit()
        self.db.refresh(surat)
        return surat

    def get_by_id(self, surat_id: int) -> Optional[SuratModel]:
        return self.db.query(SuratModel).filter(SuratModel.id == surat_id).first()

    def get_by_mahasiswa_id(self, mahasiswa_id: int) -> List[SuratModel]:
        return self.db.query(SuratModel).filter(SuratModel.mahasiswa_id == mahasiswa_id).all()

    def get_by_status(self, status: SuratStatus) -> List[SuratModel]:
        return self.db.query(SuratModel).filter(SuratModel.status == status).all()

    def get_by_document_hash(self, document_hash: str) -> Optional[SuratModel]:
        return self.db.query(SuratModel).filter(SuratModel.document_hash == document_hash).first()

    def get_pending_admin(self) -> List[SuratModel]:
        return self.get_by_status(SuratStatus.MENUNGGU_PROSES_ADMIN)

    def get_all(self) -> List[SuratModel]:
        return self.db.query(SuratModel).all()

    def update(self, surat: SuratModel) -> SuratModel:
        self.db.commit()
        self.db.refresh(surat)
        return surat

    def delete(self, surat_id: int) -> bool:
        surat = self.get_by_id(surat_id)
        if surat:
            self.db.delete(surat)
            self.db.commit()
            return True
        return False
