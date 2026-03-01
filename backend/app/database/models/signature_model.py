from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.database.db import Base


class SignatureModel(Base):
    __tablename__ = "signatures"

    id = Column(Integer, primary_key=True, index=True)
    surat_id = Column(Integer, ForeignKey("surat.id", ondelete="CASCADE"), nullable=False, index=True)
    owner_id = Column(Integer, nullable=False)
    role = Column(String, nullable=False)
    image_path = Column(String, nullable=True)
    signature_hash = Column(String, nullable=True, unique=True, index=True)
    signed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
