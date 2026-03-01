from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List


# ------------------------------------------------------------------
# Requests
# ------------------------------------------------------------------

class AjukanSuratRequest(BaseModel):
    jenis: str
    keperluan: Optional[str] = None
    is_external: bool = False
    dosen_ids: Optional[List[int]] = None


class TandaTanganDosenRequest(BaseModel):
    image_path: str


class RejectSuratRequest(BaseModel):
    reason: str


# ------------------------------------------------------------------
# Responses
# ------------------------------------------------------------------

class SignatureInfo(BaseModel):
    signature_id: Optional[int] = None
    owner_id: int
    owner_name: Optional[str] = None
    role: str
    signed: bool
    signed_at: Optional[datetime] = None


class SuratResponse(BaseModel):
    surat_id: Optional[int] = None
    mahasiswa_id: int
    jenis: str
    keperluan: Optional[str] = None
    is_external: bool
    file_path: Optional[str] = None
    status: str
    document_hash: Optional[str] = None
    pdf_path: Optional[str] = None
    qr_path: Optional[str] = None
    rejection_reason: Optional[str] = None
    created_at: Optional[datetime] = None
    signatures: Optional[List[SignatureInfo]] = None


class VerifyResponse(BaseModel):
    status: str
    message: Optional[str] = None
    mahasiswa_id: Optional[int] = None
    jenis: Optional[str] = None
    document_hash: Optional[str] = None


class DosenPublicInfo(BaseModel):
    user_id: int
    name: str
    email: str
    nip: Optional[str] = None
