from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.domain.enums import UserRole


class SignatureResponse(BaseModel):
    id: int
    surat_id: int
    owner_id: int
    role: UserRole
    image_path: Optional[str] = None
    signature_hash: Optional[str] = None
    signed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
