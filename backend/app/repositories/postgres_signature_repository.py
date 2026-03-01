from typing import List

from sqlalchemy.orm import Session

from app.database.models.signature_model import SignatureModel
from app.domain.signature import Signature
from app.repositories.signature_repository import SignatureRepository


class PostgresSignatureRepository(SignatureRepository):

    def __init__(self, db: Session):
        self.db = db

    def save(self, surat_id: int, signature: Signature) -> Signature:
        db_signature = SignatureModel(
            surat_id=surat_id,
            owner_id=signature.owner_id,
            role=signature.role,
            image_path=signature.image_path,
            signature_hash=signature.signature_hash,
            signed_at=signature.signed_at,
        )
        self.db.add(db_signature)
        self.db.commit()
        self.db.refresh(db_signature)

        signature.signature_id = db_signature.id
        signature.surat_id = surat_id
        return signature

    def update(self, signature: Signature) -> Signature:
        db_sig = (
            self.db.query(SignatureModel)
            .filter(SignatureModel.id == signature.signature_id)
            .first()
        )
        if db_sig:
            db_sig.image_path = signature.image_path
            db_sig.signature_hash = signature.signature_hash
            db_sig.signed_at = signature.signed_at
            self.db.commit()
        return signature

    def find_by_surat_id(self, surat_id: int) -> List[Signature]:
        rows = (
            self.db.query(SignatureModel)
            .filter(SignatureModel.surat_id == surat_id)
            .all()
        )
        return [self._to_domain(r) for r in rows]

    def find_by_surat_and_owner(self, surat_id: int, owner_id: int) -> Signature | None:
        row = (
            self.db.query(SignatureModel)
            .filter(
                SignatureModel.surat_id == surat_id,
                SignatureModel.owner_id == owner_id,
            )
            .first()
        )
        return self._to_domain(row) if row else None

    def find_pending_by_owner(self, owner_id: int) -> List[Signature]:
        rows = (
            self.db.query(SignatureModel)
            .filter(
                SignatureModel.owner_id == owner_id,
                SignatureModel.signed_at.is_(None),
            )
            .all()
        )
        return [self._to_domain(r) for r in rows]

    def find_signed_by_owner(self, owner_id: int) -> List[Signature]:
        rows = (
            self.db.query(SignatureModel)
            .filter(
                SignatureModel.owner_id == owner_id,
                SignatureModel.signed_at.isnot(None),
            )
            .all()
        )
        return [self._to_domain(r) for r in rows]

    @staticmethod
    def _to_domain(db_sig: SignatureModel) -> Signature:
        sig = Signature(
            owner_id=db_sig.owner_id,
            role=db_sig.role,
            image_path=db_sig.image_path,
        )
        sig.signature_id = db_sig.id
        sig.surat_id = db_sig.surat_id
        sig.signature_hash = db_sig.signature_hash
        sig.signed_at = db_sig.signed_at
        sig.created_at = db_sig.created_at
        sig.updated_at = db_sig.updated_at
        return sig
