from sqlalchemy.orm import Session
from typing import List
from app.database.models.surat_model import SuratModel
from app.repositories.surat_repository import SuratRepository
from app.domain.surat import Surat
from app.domain.status_surat import StatusSurat


class PostgresSuratRepository(SuratRepository):

    def __init__(self, db: Session):
        self.db = db

    def save(self, surat: Surat):
        if surat.surat_id is None:
            db_surat = SuratModel(
                mahasiswa_id=surat.mahasiswa_id,
                jenis=surat.jenis,
                keperluan=surat.keperluan,
                is_external=surat.is_external,
                file_path=surat.file_path,
                status=surat.status.value,
                document_hash=surat.document_hash,
                pdf_path=surat.pdf_path,
                qr_path=surat.qr_path,
                rejection_reason=surat.rejection_reason,
            )
            self.db.add(db_surat)
            self.db.commit()
            self.db.refresh(db_surat)
            surat.surat_id = db_surat.id
        else:
            db_surat = self.db.query(SuratModel).filter(SuratModel.id == surat.surat_id).first()
            if db_surat:
                db_surat.status = surat.status.value
                db_surat.document_hash = surat.document_hash
                db_surat.pdf_path = surat.pdf_path
                db_surat.qr_path = surat.qr_path
                db_surat.rejection_reason = surat.rejection_reason
                db_surat.is_external = surat.is_external
                db_surat.keperluan = surat.keperluan
                db_surat.file_path = surat.file_path
                self.db.commit()

        return surat

    def find_by_id(self, surat_id: int):
        db_surat = self.db.query(SuratModel).filter(SuratModel.id == surat_id).first()

        if not db_surat:
            return None

        return self._to_domain(db_surat)

    def find_by_hash(self, document_hash: str):
        db_surat = self.db.query(SuratModel).filter(SuratModel.document_hash == document_hash).first()

        if not db_surat:
            return None

        return self._to_domain(db_surat)

    def find_by_mahasiswa(self, mahasiswa_id: int) -> List[Surat]:
        rows = self.db.query(SuratModel).filter(
            SuratModel.mahasiswa_id == mahasiswa_id
        ).order_by(SuratModel.id.desc()).all()
        return [self._to_domain(r) for r in rows]

    def find_by_status(self, status: str) -> List[Surat]:
        rows = self.db.query(SuratModel).filter(
            SuratModel.status == status
        ).order_by(SuratModel.id.desc()).all()
        return [self._to_domain(r) for r in rows]

    def find_all(self) -> List[Surat]:
        rows = self.db.query(SuratModel).order_by(SuratModel.id.desc()).all()
        return [self._to_domain(r) for r in rows]

    def _to_domain(self, db_surat: SuratModel) -> Surat:
        surat = Surat(
            mahasiswa_id=db_surat.mahasiswa_id,
            jenis=db_surat.jenis,
            is_external=db_surat.is_external,
            keperluan=db_surat.keperluan,
            file_path=db_surat.file_path,
        )
        surat.surat_id = db_surat.id
        surat.status = StatusSurat(db_surat.status)
        surat.document_hash = db_surat.document_hash
        surat.pdf_path = db_surat.pdf_path
        surat.qr_path = db_surat.qr_path
        surat.rejection_reason = db_surat.rejection_reason
        surat.created_at = db_surat.created_at
        surat.updated_at = db_surat.updated_at
        return surat