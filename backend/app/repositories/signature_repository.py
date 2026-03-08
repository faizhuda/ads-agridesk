from typing import Optional, List

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.models.signature import SignatureModel
from app.models.surat import SuratModel
from app.domain.enums import SuratStatus


class SignatureRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, signature: SignatureModel) -> SignatureModel:
        self.db.add(signature)
        self.db.commit()
        self.db.refresh(signature)
        return signature

    def get_by_id(self, signature_id: int) -> Optional[SignatureModel]:
        return self.db.query(SignatureModel).filter(SignatureModel.id == signature_id).first()

    def get_by_surat_id(self, surat_id: int) -> List[SignatureModel]:
        return self.db.query(SignatureModel).filter(SignatureModel.surat_id == surat_id).all()

    def get_by_owner_id(self, owner_id: int) -> List[SignatureModel]:
        return self.db.query(SignatureModel).filter(SignatureModel.owner_id == owner_id).all()

    def get_pending_for_lecturer(self, lecturer_id: int) -> List[SignatureModel]:
        return (
            self.db.query(SignatureModel)
            .options(
                joinedload(SignatureModel.surat).joinedload(SuratModel.mahasiswa)
            )
            .join(SuratModel, SignatureModel.surat_id == SuratModel.id)
            .filter(
                SignatureModel.owner_id == lecturer_id,
                SignatureModel.signed_at.is_(None),
                SuratModel.status == SuratStatus.MENUNGGU_TTD_DOSEN,
            )
            .all()
        )

    def get_signed_for_lecturer(self, lecturer_id: int) -> List[SignatureModel]:
        return (
            self.db.query(SignatureModel)
            .options(
                joinedload(SignatureModel.surat).joinedload(SuratModel.mahasiswa)
            )
            .join(SuratModel, SignatureModel.surat_id == SuratModel.id)
            .filter(
                SignatureModel.owner_id == lecturer_id,
                or_(
                    SignatureModel.signed_at.is_not(None),
                    SuratModel.status == SuratStatus.DITOLAK,
                ),
            )
            .order_by(SignatureModel.signed_at.desc())
            .all()
        )

    def get_unsigned_by_surat(self, surat_id: int) -> List[SignatureModel]:
        return (
            self.db.query(SignatureModel)
            .filter(
                SignatureModel.surat_id == surat_id,
                SignatureModel.signed_at.is_(None),
            )
            .all()
        )

    def update(self, signature: SignatureModel) -> SignatureModel:
        self.db.commit()
        self.db.refresh(signature)
        return signature
