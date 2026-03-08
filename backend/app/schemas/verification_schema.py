from pydantic import BaseModel


class VerificationResponse(BaseModel):
    status: str
    surat_id: int | None = None
    jenis: str | None = None
    keperluan: str | None = None
