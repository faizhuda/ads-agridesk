from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import hashlib
import uuid

from app.domain.enums import UserRole


@dataclass
class Signature:
    id: Optional[int] = None
    surat_id: Optional[int] = None
    owner_id: Optional[int] = None
    role: UserRole = UserRole.MAHASISWA
    image_path: Optional[str] = None
    signature_hash: Optional[str] = None
    signed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def sign(self) -> None:
        self.signed_at = datetime.utcnow()
        self.generate_signature_hash()

    def generate_signature_hash(self) -> str:
        raw = f"{self.surat_id}:{self.owner_id}:{self.role}:{uuid.uuid4()}"
        self.signature_hash = hashlib.sha256(raw.encode()).hexdigest()
        return self.signature_hash

    def is_signed(self) -> bool:
        return self.signed_at is not None
