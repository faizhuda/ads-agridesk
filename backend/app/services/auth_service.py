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

        # Keep JWT subject as string for standards-compliant decoding.
        token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
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

    def search_lecturers(self, query: str, limit: int = 10) -> list[dict]:
        lecturers = self.user_repo.search_lecturers(query, limit=limit)
        return [
            {
                "id": lecturer.id,
                "name": lecturer.name,
                "nip": lecturer.nip,
                "email": lecturer.email,
            }
            for lecturer in lecturers
        ]
