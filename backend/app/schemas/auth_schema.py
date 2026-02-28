from pydantic import BaseModel
from app.domain.user import UserRole


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    role: UserRole