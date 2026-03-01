from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from app.database.db import Base


class SuratModel(Base):
    __tablename__ = "surat"

    id = Column(Integer, primary_key=True, index=True)
    mahasiswa_id = Column(Integer, nullable=False)
    jenis = Column(String, nullable=False)
    keperluan = Column(Text, nullable=True)
    is_external = Column(Boolean, default=False, nullable=False)
    file_path = Column(String, nullable=True)
    status = Column(String, nullable=False)
    document_hash = Column(String, nullable=True)
    pdf_path = Column(String, nullable=True)
    qr_path = Column(String, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)