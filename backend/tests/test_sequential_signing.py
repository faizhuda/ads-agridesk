"""Service-layer tests for sequential signing enforcement (BUG-11).

Verifies that SignatureService.sign_by_lecturer() respects signing order
when is_sequential=True, and imposes no order restriction when False.
"""
import pytest

from app.domain.enums import SuratStatus, UserRole
from app.domain.exceptions import EntityNotFoundError, InvalidStateTransitionError
from app.models.signature import SignatureModel
from app.models.surat import SuratModel
from app.models.user import UserModel
from app.services.signature_service import SignatureService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_user(db, email, role=UserRole.DOSEN, nip=None, nim=None) -> UserModel:
    u = UserModel(name="U", email=email, password_hash="x", role=role, nip=nip, nim=nim)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def _make_surat(db, mahasiswa_id, is_sequential=True) -> SuratModel:
    s = SuratModel(
        mahasiswa_id=mahasiswa_id,
        jenis="test",
        keperluan="test",
        is_external=True,
        file_path="/f.pdf",
        status=SuratStatus.MENUNGGU_TTD_DOSEN,
        is_sequential=is_sequential,
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def _make_sig(db, surat_id, owner_id, signing_order=None) -> SignatureModel:
    sig = SignatureModel(
        surat_id=surat_id,
        owner_id=owner_id,
        role=UserRole.DOSEN,
        signing_order=signing_order,
    )
    db.add(sig)
    db.commit()
    db.refresh(sig)
    return sig


# ---------------------------------------------------------------------------
# Sequential signing order enforcement
# ---------------------------------------------------------------------------

class TestSequentialSigningOrder:
    def test_first_signer_can_sign(self, db, tmp_path):
        """Order-1 signer may sign immediately in a sequential surat."""
        student = _make_user(db, "s@u.id", role=UserRole.MAHASISWA, nim="1")
        l1 = _make_user(db, "l1@u.id", nip="1")
        l2 = _make_user(db, "l2@u.id", nip="2")
        surat = _make_surat(db, student.id, is_sequential=True)
        sig1 = _make_sig(db, surat.id, l1.id, signing_order=1)
        _make_sig(db, surat.id, l2.id, signing_order=2)

        sig_img = tmp_path / "sig.png"
        sig_img.write_bytes(b"\x89PNG")

        svc = SignatureService(db)
        result = svc.sign_by_lecturer(sig1.id, l1.id, str(sig_img))
        assert result.is_signed()

    def test_second_signer_blocked_before_first_signs(self, db, tmp_path):
        """Order-2 signer must be rejected until order-1 has signed."""
        student = _make_user(db, "s@u.id", role=UserRole.MAHASISWA, nim="1")
        l1 = _make_user(db, "l1@u.id", nip="1")
        l2 = _make_user(db, "l2@u.id", nip="2")
        surat = _make_surat(db, student.id, is_sequential=True)
        _make_sig(db, surat.id, l1.id, signing_order=1)
        sig2 = _make_sig(db, surat.id, l2.id, signing_order=2)

        sig_img = tmp_path / "sig.png"
        sig_img.write_bytes(b"\x89PNG")

        svc = SignatureService(db)
        with pytest.raises(InvalidStateTransitionError, match="Belum giliran"):
            svc.sign_by_lecturer(sig2.id, l2.id, str(sig_img))

    def test_second_signer_allowed_after_first_signs(self, db, tmp_path):
        """After order-1 signs, order-2 must be allowed."""
        from datetime import datetime, timezone
        student = _make_user(db, "s@u.id", role=UserRole.MAHASISWA, nim="1")
        l1 = _make_user(db, "l1@u.id", nip="1")
        l2 = _make_user(db, "l2@u.id", nip="2")
        surat = _make_surat(db, student.id, is_sequential=True)
        sig1 = _make_sig(db, surat.id, l1.id, signing_order=1)
        sig2 = _make_sig(db, surat.id, l2.id, signing_order=2)

        # Manually mark sig1 as signed (bypass service for isolation)
        sig1.signed_at = datetime.now(timezone.utc)
        sig1.image_path = "/sig.png"
        sig1.signature_hash = "aaaa"
        db.commit()

        sig_img = tmp_path / "sig.png"
        sig_img.write_bytes(b"\x89PNG")

        svc = SignatureService(db)
        result = svc.sign_by_lecturer(sig2.id, l2.id, str(sig_img))
        assert result.is_signed()

    def test_wrong_owner_raises_even_in_sequential(self, db, tmp_path):
        """Ownership validation must run regardless of order position."""
        student = _make_user(db, "s@u.id", role=UserRole.MAHASISWA, nim="1")
        l1 = _make_user(db, "l1@u.id", nip="1")
        l2 = _make_user(db, "l2@u.id", nip="2")
        surat = _make_surat(db, student.id, is_sequential=True)
        sig1 = _make_sig(db, surat.id, l1.id, signing_order=1)

        sig_img = tmp_path / "sig.png"
        sig_img.write_bytes(b"\x89PNG")

        svc = SignatureService(db)
        from app.domain.exceptions import UnauthorizedError
        with pytest.raises(UnauthorizedError, match="Bukan tanda tangan Anda"):
            svc.sign_by_lecturer(sig1.id, l2.id, str(sig_img))


# ---------------------------------------------------------------------------
# Parallel signing (is_sequential=False)
# ---------------------------------------------------------------------------

class TestParallelSigning:
    def test_any_signer_can_sign_in_parallel_surat(self, db, tmp_path):
        """When is_sequential=False both signers can sign in any order."""
        student = _make_user(db, "s@u.id", role=UserRole.MAHASISWA, nim="1")
        l1 = _make_user(db, "l1@u.id", nip="1")
        l2 = _make_user(db, "l2@u.id", nip="2")
        surat = _make_surat(db, student.id, is_sequential=False)
        _make_sig(db, surat.id, l1.id, signing_order=1)
        sig2 = _make_sig(db, surat.id, l2.id, signing_order=2)

        sig_img = tmp_path / "sig.png"
        sig_img.write_bytes(b"\x89PNG")

        svc = SignatureService(db)
        # l2 signs before l1 — must succeed
        result = svc.sign_by_lecturer(sig2.id, l2.id, str(sig_img))
        assert result.is_signed()

    def test_both_signers_can_sign_in_parallel_surat(self, db, tmp_path):
        student = _make_user(db, "s@u.id", role=UserRole.MAHASISWA, nim="1")
        l1 = _make_user(db, "l1@u.id", nip="1")
        l2 = _make_user(db, "l2@u.id", nip="2")
        surat = _make_surat(db, student.id, is_sequential=False)
        sig1 = _make_sig(db, surat.id, l1.id, signing_order=1)
        sig2 = _make_sig(db, surat.id, l2.id, signing_order=2)

        sig_img = tmp_path / "sig.png"
        sig_img.write_bytes(b"\x89PNG")

        svc = SignatureService(db)
        r1 = svc.sign_by_lecturer(sig1.id, l1.id, str(sig_img))
        r2 = svc.sign_by_lecturer(sig2.id, l2.id, str(sig_img))
        assert r1.is_signed()
        assert r2.is_signed()


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestSignByLecturerEdgeCases:
    def test_nonexistent_signature_raises(self, db, tmp_path):
        svc = SignatureService(db)
        with pytest.raises(EntityNotFoundError):
            svc.sign_by_lecturer(999999, 1, "/sig.png")

    def test_double_sign_raises_validation_error(self, db, tmp_path):
        from app.domain.exceptions import ValidationError
        student = _make_user(db, "s@u.id", role=UserRole.MAHASISWA, nim="1")
        l1 = _make_user(db, "l1@u.id", nip="1")
        surat = _make_surat(db, student.id, is_sequential=False)
        sig = _make_sig(db, surat.id, l1.id, signing_order=1)

        sig_img = tmp_path / "sig.png"
        sig_img.write_bytes(b"\x89PNG")

        svc = SignatureService(db)
        svc.sign_by_lecturer(sig.id, l1.id, str(sig_img))

        with pytest.raises(ValidationError, match="Sudah ditandatangani"):
            svc.sign_by_lecturer(sig.id, l1.id, str(sig_img))

    def test_all_lecturers_signed_advances_surat_status(self, db, tmp_path):
        """After every lecturer signs, surat should advance to MENUNGGU_PROSES_ADMIN."""
        from app.repositories.surat_repository import SuratRepository
        student = _make_user(db, "s@u.id", role=UserRole.MAHASISWA, nim="1")
        l1 = _make_user(db, "l1@u.id", nip="1")
        surat = _make_surat(db, student.id, is_sequential=False)
        sig = _make_sig(db, surat.id, l1.id, signing_order=1)

        sig_img = tmp_path / "sig.png"
        sig_img.write_bytes(b"\x89PNG")

        svc = SignatureService(db)
        svc.sign_by_lecturer(sig.id, l1.id, str(sig_img))

        surat_after = SuratRepository(db).get_by_id(surat.id)
        assert surat_after.status == SuratStatus.MENUNGGU_PROSES_ADMIN
