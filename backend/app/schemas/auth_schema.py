from pydantic import BaseModel
from app.domain.user import UserRole
from typing import Optional


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    role: UserRole
    nim: Optional[str] = None
    nip: Optional[str] = None