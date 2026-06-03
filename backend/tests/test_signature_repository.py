"""Repository-layer tests for SignatureRepository.

Focuses on get_next_to_sign() sequential vs parallel logic and the
for-update query (which degrades gracefully to a plain SELECT in SQLite).
"""
import pytest

from app.domain.enums import SuratStatus, UserRole
from app.models.signature import SignatureModel
from app.models.surat import SuratModel
from app.models.user import UserModel
from app.repositories.signature_repository import SignatureRepository


def _make_user(db, email, role=UserRole.DOSEN, nip=None, nim=None) -> UserModel:
    u = UserModel(name="U", email=email, password_hash="x", role=role, nip=nip, nim=nim)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def _make_surat(db, mahasiswa_id) -> SuratModel:
    s = SuratModel(
        mahasiswa_id=mahasiswa_id, jenis="t", keperluan="t",
        is_external=True, file_path="/f.pdf",
        status=SuratStatus.MENUNGGU_TTD_DOSEN,
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def _make_sig(db, surat_id, owner_id, signing_order=None) -> SignatureModel:
    sig = SignatureModel(
        surat_id=surat_id, owner_id=owner_id,
        role=UserRole.DOSEN, signing_order=signing_order,
    )
    db.add(sig)
    db.commit()
    db.refresh(sig)
    return sig


class TestGetNextToSign:
    def test_parallel_returns_all_unsigned(self, db):
        student = _make_user(db, "s@u.id", role=UserRole.MAHASISWA, nim="1")
        l1 = _make_user(db, "l1@u.id", nip="1")
        l2 = _make_user(db, "l2@u.id", nip="2")
        surat = _make_surat(db, student.id)
        _make_sig(db, surat.id, l1.id, signing_order=1)
        _make_sig(db, surat.id, l2.id, signing_order=2)

        repo = SignatureRepository(db)
        next_signers = repo.get_next_to_sign(surat.id, is_sequential=False)
        assert len(next_signers) == 2

    def test_sequential_returns_only_lowest_order(self, db):
        student = _make_user(db, "s@u.id", role=UserRole.MAHASISWA, nim="1")
        l1 = _make_user(db, "l1@u.id", nip="1")
        l2 = _make_user(db, "l2@u.id", nip="2")
        surat = _make_surat(db, student.id)
        _make_sig(db, surat.id, l1.id, signing_order=1)
        _make_sig(db, surat.id, l2.id, signing_order=2)

        repo = SignatureRepository(db)
        next_signers = repo.get_next_to_sign(surat.id, is_sequential=True)
        assert len(next_signers) == 1
        assert next_signers[0].owner_id == l1.id

    def test_sequential_advances_after_first_signs(self, db):
        from datetime import datetime, timezone
        student = _make_user(db, "s@u.id", role=UserRole.MAHASISWA, nim="1")
        l1 = _make_user(db, "l1@u.id", nip="1")
        l2 = _make_user(db, "l2@u.id", nip="2")
        surat = _make_surat(db, student.id)
        sig1 = _make_sig(db, surat.id, l1.id, signing_order=1)
        _make_sig(db, surat.id, l2.id, signing_order=2)

        # Mark l1 as signed
        sig1.signed_at = datetime.now(timezone.utc)
        db.commit()

        repo = SignatureRepository(db)
        next_signers = repo.get_next_to_sign(surat.id, is_sequential=True)
        assert len(next_signers) == 1
        assert next_signers[0].owner_id == l2.id

    def test_no_unsigned_returns_empty(self, db):
        from datetime import datetime, timezone
        student = _make_user(db, "s@u.id", role=UserRole.MAHASISWA, nim="1")
        l1 = _make_user(db, "l1@u.id", nip="1")
        surat = _make_surat(db, student.id)
        sig = _make_sig(db, surat.id, l1.id, signing_order=1)
        sig.signed_at = datetime.now(timezone.utc)
        db.commit()

        repo = SignatureRepository(db)
        assert repo.get_next_to_sign(surat.id, is_sequential=True) == []
        assert repo.get_next_to_sign(surat.id, is_sequential=False) == []


class TestGetByIdForUpdate:
    def test_returns_same_as_get_by_id(self, db):
        """SQLite ignores FOR UPDATE; confirm the query still returns the row."""
        student = _make_user(db, "s@u.id", role=UserRole.MAHASISWA, nim="1")
        l1 = _make_user(db, "l1@u.id", nip="1")
        surat = _make_surat(db, student.id)
        sig = _make_sig(db, surat.id, l1.id, signing_order=1)

        repo = SignatureRepository(db)
        normal = repo.get_by_id(sig.id)
        locked = repo.get_by_id_for_update(sig.id)
        assert locked is not None
        assert locked.id == normal.id
        assert locked.owner_id == normal.owner_id

    def test_nonexistent_returns_none(self, db):
        repo = SignatureRepository(db)
        assert repo.get_by_id_for_update(999999) is None
