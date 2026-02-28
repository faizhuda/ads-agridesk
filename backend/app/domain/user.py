from enum import Enum


class UserRole(str, Enum):
    MAHASISWA = "MAHASISWA"
    DOSEN = "DOSEN"
    ADMIN = "ADMIN"


class User:

    def __init__(self, user_id: int, name: str, email: str, password_hash: str, role: UserRole):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.role = role

    def check_role(self, role: UserRole):
        return self.role == role