from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base
from app.domain.enums import UserRole


class SignatureModel(Base):
    __tablename__ = "signatures"

    id = Column(Integer, primary_key=True, index=True)
    surat_id = Column(Integer, ForeignKey("surat.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(SAEnum(UserRole), nullable=False)
    image_path = Column(String, nullable=True)
    signature_hash = Column(String, nullable=True)
    signed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    surat = relationship("SuratModel", back_populates="signatures")
    owner = relationship("UserModel", back_populates="signatures")

    @property
    def surat_jenis(self) -> Optional[str]:
        return self.surat.jenis if self.surat else None

    @property
    def mahasiswa_name(self) -> Optional[str]:
        return self.surat.mahasiswa.name if self.surat and self.surat.mahasiswa else None

    @property
    def owner_name(self) -> Optional[str]:
        return self.owner.name if self.owner else None

    @property
    def owner_nip(self) -> Optional[str]:
        return self.owner.nip if self.owner else None
