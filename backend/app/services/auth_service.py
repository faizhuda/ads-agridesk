from app.repositories.user_repository import UserRepository
from app.utils.password_utils import PasswordUtils
from app.utils.jwt_utils import JWTUtils
from app.domain.user import User, UserRole
from app.domain.exceptions import UserNotFoundException, InvalidCredentialsError, DuplicateEmailError


class AuthService:

    def __init__(self, repository: UserRepository):
        self.repository = repository

    def register(
        self,
        name: str,
        email: str,
        password: str,
        role: str,
        nim: str | None = None,
        nip: str | None = None,
    ):
        existing = self.repository.find_by_email(email)
        if existing:
            raise DuplicateEmailError("Email sudah terdaftar")

        hashed = PasswordUtils.hash_password(password)
        user = User(
            user_id=None,
            name=name,
            email=email,
            password_hash=hashed,
            role=UserRole(role),
            nim=nim,
            nip=nip,
        )
        return self.repository.save(user)

    def login(self, email: str, password: str):
        user = self.repository.find_by_email(email)

        if not user:
            raise UserNotFoundException("User tidak ditemukan")

        if not PasswordUtils.verify_password(password, user.password_hash):
            raise InvalidCredentialsError("Password salah")

        token = JWTUtils.create_access_token({
            "sub": str(user.user_id),
            "email": user.email,
            "role": user.role.value,
            "name": user.name,
        })

        return {"access_token": token, "token_type": "bearer"}