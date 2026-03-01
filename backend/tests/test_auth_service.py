import pytest

from app.domain.user import User
from app.domain.exceptions import UserNotFoundException, InvalidCredentialsError, InvalidUserIdentityError, DuplicateEmailError
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService


class FakeUserRepository(UserRepository):

    def __init__(self):
        self.users_by_email = {}
        self._next_id = 1

    def save(self, user: User) -> User:
        if user.user_id is None:
            user.user_id = self._next_id
            self._next_id += 1
        self.users_by_email[user.email] = user
        return user

    def find_by_email(self, email: str):
        return self.users_by_email.get(email)

    def find_by_id(self, user_id: int):
        for user in self.users_by_email.values():
            if user.user_id == user_id:
                return user
        return None

    def find_by_ids(self, user_ids):
        return [u for u in self.users_by_email.values() if u.user_id in user_ids]

    def find_by_role(self, role: str):
        return [u for u in self.users_by_email.values() if u.role.value == role]


def test_register_hashes_password_and_persists_user():
    repository = FakeUserRepository()
    service = AuthService(repository)

    user = service.register("Alice", "alice@example.com", "secret123", "MAHASISWA", nim="23101122")

    assert user.user_id == 1
    assert user.email == "alice@example.com"
    assert user.password_hash != "secret123"
    assert user.role.value == "MAHASISWA"
    assert user.nim == "23101122"
    assert user.nip is None


def test_login_returns_access_token_for_valid_credentials():
    repository = FakeUserRepository()
    service = AuthService(repository)
    service.register("Bob", "bob@example.com", "secret123", "DOSEN", nip="198809122001")

    payload = service.login("bob@example.com", "secret123")

    assert payload["token_type"] == "bearer"
    assert isinstance(payload["access_token"], str)
    assert len(payload["access_token"]) > 20


def test_login_raises_when_user_not_found():
    repository = FakeUserRepository()
    service = AuthService(repository)

    with pytest.raises(UserNotFoundException):
        service.login("missing@example.com", "secret123")


def test_login_raises_for_invalid_password():
    repository = FakeUserRepository()
    service = AuthService(repository)
    service.register("Carol", "carol@example.com", "secret123", "ADMIN", nip="198709112002")

    with pytest.raises(InvalidCredentialsError):
        service.login("carol@example.com", "wrong-password")


def test_register_mahasiswa_without_nim_raises_error():
    repository = FakeUserRepository()
    service = AuthService(repository)

    with pytest.raises(InvalidUserIdentityError):
        service.register("No Nim", "nonim@example.com", "secret123", "MAHASISWA")


def test_register_dosen_without_nip_raises_error():
    repository = FakeUserRepository()
    service = AuthService(repository)

    with pytest.raises(InvalidUserIdentityError):
        service.register("No Nip", "nonip@example.com", "secret123", "DOSEN")


def test_register_duplicate_email_raises_error():
    repository = FakeUserRepository()
    service = AuthService(repository)
    service.register("Alice", "alice@dup.com", "secret123", "MAHASISWA", nim="111")

    with pytest.raises(DuplicateEmailError):
        service.register("Alice2", "alice@dup.com", "secret456", "MAHASISWA", nim="222")