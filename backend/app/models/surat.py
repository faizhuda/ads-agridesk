from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base
from app.domain.enums import SuratStatus


class SuratModel(Base):
    __tablename__ = "surat"

    id = Column(Integer, primary_key=True, index=True)
    mahasiswa_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    jenis = Column(String, nullable=False)
    keperluan = Column(String, nullable=False)
    is_external = Column(Boolean, default=False)
    file_path = Column(String, nullable=True)
    status = Column(SAEnum(SuratStatus), default=SuratStatus.DRAFT, nullable=False)
    document_hash = Column(String, nullable=True, unique=True)
    pdf_path = Column(String, nullable=True)
    qr_path = Column(String, nullable=True)
    rejection_reason = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    mahasiswa = relationship("UserModel", back_populates="surat_list")
    signatures = relationship("SignatureModel", back_populates="surat")
