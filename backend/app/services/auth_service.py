from sqlalchemy.orm import Session

from app.models.user import UserModel
from app.repositories.user_repository import UserRepository
from app.utils.security import hash_password, verify_password, create_access_token
from app.domain.enums import UserRole


class AuthService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)

    def register(
        self,
        name: str,
        email: str,
        password: str,
        role: UserRole,
        nim: str | None = None,
        nip: str | None = None,
    ) -> UserModel:
        existing = self.user_repo.get_by_email(email)
        if existing:
            raise ValueError("Email sudah terdaftar")

        if role == UserRole.MAHASISWA and nim:
            if self.user_repo.get_by_nim(nim):
                raise ValueError("NIM sudah terdaftar")
        if role in (UserRole.DOSEN, UserRole.ADMIN) and nip:
            if self.user_repo.get_by_nip(nip):
                raise ValueError("NIP sudah terdaftar")

        user = UserModel(
            name=name,
            email=email,
            password_hash=hash_password(password),
            role=role,
            nim=nim,
            nip=nip,
        )
        return self.user_repo.create(user)

    def login(self, email: str, password: str) -> dict:
        user = self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise ValueError("Email atau password salah")

        token = create_access_token(data={"sub": user.id, "role": user.role.value})
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role.value,
            },
        }
