"""Pure domain-entity unit tests — no database, no I/O.

These tests verify business rules encoded directly in the domain layer:
Surat FSM, Signature sign guards, and User identity helpers.
"""
import pytest

from app.domain.enums import SuratStatus, UserRole
from app.domain.exceptions import (
    InvalidStateTransitionError,
    UnauthorizedError,
    ValidationError,
)
from app.domain.signature import Signature
from app.domain.surat import Surat
from app.domain.user import User


# ─────────────────────────── User ───────────────────────────

class TestUserDomain:
    def test_get_identifier_mahasiswa_returns_nim(self):
        u = User(role=UserRole.MAHASISWA, nim="12345678", nip=None)
        assert u.get_identifier() == "12345678"

    def test_get_identifier_dosen_returns_nip(self):
        u = User(role=UserRole.DOSEN, nip="198001012000", nim=None)
        assert u.get_identifier() == "198001012000"

    def test_get_identifier_admin_returns_nip(self):
        u = User(role=UserRole.ADMIN, nip="000000000000", nim=None)
        assert u.get_identifier() == "000000000000"

    def test_role_predicates(self):
        mhs = User(role=UserRole.MAHASISWA)
        dosen = User(role=UserRole.DOSEN)
        admin = User(role=UserRole.ADMIN)

        assert mhs.is_mahasiswa() and not mhs.is_dosen() and not mhs.is_admin()
        assert dosen.is_dosen() and not dosen.is_mahasiswa() and not dosen.is_admin()
        assert admin.is_admin() and not admin.is_mahasiswa() and not admin.is_dosen()

    def test_update_signature_image(self):
        u = User()
        u.update_signature_image("/uploads/sig.png")
        assert u.signature_image_path == "/uploads/sig.png"


# ─────────────────────────── Signature ───────────────────────────

class TestSignatureDomain:
    def _make_sig(self, owner_id=1):
        return Signature(id=1, surat_id=10, owner_id=owner_id, role=UserRole.DOSEN)

    def test_sign_happy_path(self):
        sig = self._make_sig()
        sig.sign("/uploads/sig.png", "abc123hash")
        assert sig.is_signed()
        assert sig.image_path == "/uploads/sig.png"
        assert sig.signature_hash == "abc123hash"
        assert sig.signed_at is not None

    def test_sign_raises_on_double_sign(self):
        sig = self._make_sig()
        sig.sign("/uploads/sig.png", "hash1")
        with pytest.raises(ValidationError, match="Sudah ditandatangani"):
            sig.sign("/uploads/sig2.png", "hash2")

    def test_sign_raises_when_image_path_is_none(self):
        sig = self._make_sig()
        with pytest.raises(ValidationError, match="Path gambar"):
            sig.sign(None, "hash")

    def test_sign_raises_when_image_path_is_empty_string(self):
        sig = self._make_sig()
        with pytest.raises(ValidationError, match="Path gambar"):
            sig.sign("", "hash")

    def test_validate_owner_correct_owner_passes(self):
        sig = self._make_sig(owner_id=42)
        sig.validate_owner(42)  # should not raise

    def test_validate_owner_wrong_owner_raises(self):
        sig = self._make_sig(owner_id=42)
        with pytest.raises(UnauthorizedError, match="Bukan tanda tangan Anda"):
            sig.validate_owner(99)

    def test_is_signed_false_before_signing(self):
        sig = self._make_sig()
        assert not sig.is_signed()


# ─────────────────────────── Surat FSM ───────────────────────────

class TestSuratFSM:
    def _draft(self):
        return Surat(mahasiswa_id=1, jenis="test", keperluan="test")

    def test_initial_status_is_draft(self):
        s = self._draft()
        assert s.status == SuratStatus.DRAFT

    def test_direct_status_assignment_raises(self):
        s = self._draft()
        with pytest.raises(AttributeError):
            s.status = SuratStatus.SELESAI

    def test_submit_without_lecturers_goes_to_admin(self):
        s = self._draft()
        s.submit(has_lecturer_signatures=False)
        assert s.status == SuratStatus.MENUNGGU_PROSES_ADMIN

    def test_submit_with_lecturers_goes_to_menunggu_ttd(self):
        s = self._draft()
        s.submit(has_lecturer_signatures=True)
        assert s.status == SuratStatus.MENUNGGU_TTD_DOSEN

    def test_advance_to_admin_from_menunggu_ttd(self):
        s = self._draft()
        s.submit(has_lecturer_signatures=True)
        s.advance_to_admin()
        assert s.status == SuratStatus.MENUNGGU_PROSES_ADMIN

    def test_approve_sets_selesai_and_stores_hash(self):
        s = self._draft()
        s.submit(has_lecturer_signatures=False)
        s.approve("deadbeef", qr_path="/qr.png", final_pdf_path="/final.pdf")
        assert s.status == SuratStatus.SELESAI
        assert s.document_hash == "deadbeef"
        assert s.qr_path == "/qr.png"
        assert s.pdf_path == "/final.pdf"

    def test_reject_sets_ditolak_and_stores_reason(self):
        s = self._draft()
        s.submit(has_lecturer_signatures=False)
        s.reject("Dokumen tidak lengkap")
        assert s.status == SuratStatus.DITOLAK
        assert s.rejection_reason == "Dokumen tidak lengkap"

    def test_reject_from_menunggu_ttd(self):
        s = self._draft()
        s.submit(has_lecturer_signatures=True)
        s.reject("Perlu revisi")
        assert s.status == SuratStatus.DITOLAK

    def test_reject_empty_reason_raises(self):
        s = self._draft()
        s.submit(has_lecturer_signatures=False)
        with pytest.raises(ValidationError, match="Alasan penolakan"):
            s.reject("   ")

    def test_invalid_transition_raises(self):
        s = self._draft()
        # DRAFT → SELESAI is not a valid transition
        with pytest.raises(InvalidStateTransitionError):
            s._transition_to(SuratStatus.SELESAI)

    def test_selesai_is_terminal(self):
        s = self._draft()
        s.submit(has_lecturer_signatures=False)
        s.approve("hash")
        assert s.status == SuratStatus.SELESAI
        assert not s.can_transition_to(SuratStatus.DITOLAK)
        assert not s.can_transition_to(SuratStatus.DRAFT)

    def test_ditolak_is_terminal(self):
        s = self._draft()
        s.submit(has_lecturer_signatures=False)
        s.reject("reason")
        assert not s.can_transition_to(SuratStatus.SELESAI)

    def test_is_completed(self):
        s = self._draft()
        assert not s.is_completed()
        s.submit(has_lecturer_signatures=False)
        s.approve("h")
        assert s.is_completed()
