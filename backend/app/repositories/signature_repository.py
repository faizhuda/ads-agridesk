from typing import Optional, List

from sqlalchemy.orm import Session

from app.models.signature import SignatureModel


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
            .filter(
                SignatureModel.owner_id == lecturer_id,
                SignatureModel.signed_at.is_(None),
            )
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
