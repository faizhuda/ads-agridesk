from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.domain.enums import SuratStatus


@dataclass
class Surat:
    id: Optional[int] = None
    mahasiswa_id: Optional[int] = None
    jenis: str = ""
    keperluan: str = ""
    is_external: bool = False
    file_path: Optional[str] = None
    status: SuratStatus = SuratStatus.DRAFT
    document_hash: Optional[str] = None
    pdf_path: Optional[str] = None
    qr_path: Optional[str] = None
    rejection_reason: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def submit(self) -> None:
        self.status = SuratStatus.DRAFT

    def update_status(self, new_status: SuratStatus) -> None:
        self.status = new_status

    def reject(self, reason: str) -> None:
        self.status = SuratStatus.DITOLAK
        self.rejection_reason = reason

    def set_document_hash(self, hash_value: str) -> None:
        self.document_hash = hash_value

    def attach_pdf(self, pdf_path: str) -> None:
        self.pdf_path = pdf_path

    def attach_qr(self, qr_path: str) -> None:
        self.qr_path = qr_path

    def is_completed(self) -> bool:
        return self.status == SuratStatus.SELESAI
