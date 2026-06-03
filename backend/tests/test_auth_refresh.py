"""Tests for refresh token rotation (IMP-04).

Verifies that:
- A valid refresh token issues new access + refresh tokens.
- The stored hash is updated on every rotation.
- A reused (old) refresh token is rejected after rotation.
- A token with a wrong type claim is rejected.
"""
import pytest

from app.domain.enums import UserRole
from app.domain.exceptions import UnauthorizedError
from app.services.auth_service import AuthService


def _register_and_login(db):
    svc = AuthService(db)
    svc.register(
        name="Budi", email="budi@u.id", password="secret",
        role=UserRole.MAHASISWA, nim="111",
    )
    return svc.login("budi@u.id", "secret")


class TestRefreshTokenRotation:
    def test_valid_refresh_returns_new_tokens(self, db):
        tokens = _register_and_login(db)
        svc = AuthService(db)
        result = svc.refresh(tokens["refresh_token"])
        assert result["access_token"]
        assert result["refresh_token"]
        assert result["token_type"] == "bearer"

    def test_new_refresh_token_differs_from_old(self, db):
        tokens = _register_and_login(db)
        svc = AuthService(db)
        result = svc.refresh(tokens["refresh_token"])
        assert result["refresh_token"] != tokens["refresh_token"]

    def test_reused_refresh_token_is_rejected(self, db):
        """After one rotation, the original token must no longer work."""
        tokens = _register_and_login(db)
        svc = AuthService(db)
        svc.refresh(tokens["refresh_token"])  # rotate once

        with pytest.raises(UnauthorizedError):
            svc.refresh(tokens["refresh_token"])  # original token now stale

    def test_second_rotation_uses_new_token(self, db):
        """The new refresh token issued after rotation must itself be rotatable."""
        tokens = _register_and_login(db)
        svc = AuthService(db)
        first_rotation = svc.refresh(tokens["refresh_token"])
        second_rotation = svc.refresh(first_rotation["refresh_token"])
        assert second_rotation["access_token"]

    def test_access_token_as_refresh_raises(self, db):
        """An access token (type != 'refresh') must be rejected."""
        tokens = _register_and_login(db)
        svc = AuthService(db)
        with pytest.raises(UnauthorizedError):
            svc.refresh(tokens["access_token"])

    def test_garbage_token_raises(self, db):
        svc = AuthService(db)
        with pytest.raises(UnauthorizedError):
            svc.refresh("this.is.not.a.real.token")
