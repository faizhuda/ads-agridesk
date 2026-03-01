from enum import Enum
from .exceptions import InvalidUserIdentityError


class UserRole(str, Enum):
    MAHASISWA = "MAHASISWA"
    DOSEN = "DOSEN"
    ADMIN = "ADMIN"


class User:

    def __init__(
        self,
        user_id: int,
        name: str,
        email: str,
        password_hash: str,
        role: UserRole,
        nim: str | None = None,
        nip: str | None = None,
    ):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.nim = nim
        self.nip = nip

        self._validate_identity_by_role()

    def check_role(self, role: UserRole):
        return self.role == role

    def _validate_identity_by_role(self):
        if self.role == UserRole.MAHASISWA:
            if not self.nim:
                raise InvalidUserIdentityError("MAHASISWA wajib memiliki NIM")
            if self.nip:
                raise InvalidUserIdentityError("MAHASISWA tidak boleh memiliki NIP")

        if self.role in {UserRole.DOSEN, UserRole.ADMIN}:
            if not self.nip:
                raise InvalidUserIdentityError(f"{self.role.value} wajib memiliki NIP")
            if self.nim:
                raise InvalidUserIdentityError(f"{self.role.value} tidak boleh memiliki NIM")