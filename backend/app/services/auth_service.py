from app.repositories.user_repository import InMemoryUserRepository
from app.utils.password_utils import PasswordUtils
from app.utils.jwt_utils import JWTUtils
from app.domain.user import User, UserRole


class AuthService:

    def __init__(self, repository: InMemoryUserRepository):
        self.repository = repository

    def register(self, name: str, email: str, password: str, role: str):
        hashed = PasswordUtils.hash_password(password)
        user = User(
            user_id=len(self.repository.users) + 1,
            name=name,
            email=email,
            password_hash=hashed,
            role=UserRole(role)
        )
        return self.repository.save(user)

    def login(self, email: str, password: str):
        user = self.repository.find_by_email(email)

        if not user:
            raise Exception("User tidak ditemukan")

        if not PasswordUtils.verify_password(password, user.password_hash):
            raise Exception("Password salah")

        token = JWTUtils.create_access_token({
            "sub": user.email,
            "role": user.role.value
        })

        return {"access_token": token, "token_type": "bearer"}