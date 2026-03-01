import pytest

from app.domain.surat import Surat
from app.domain.signature import Signature
from app.domain.exceptions import (
    SuratNotFoundException,
    InvalidDocumentError,
    InvalidStatusTransitionError,
    DomainException,
)
from app.domain.status_surat import StatusSurat
from app.repositories.surat_repository import SuratRepository
from app.repositories.signature_repository import SignatureRepository
from app.services.surat_service import SuratService


# ------------------------------------------------------------------
# Fakes
# ------------------------------------------------------------------


class FakeSuratRepository(SuratRepository):

    def __init__(self):
        self.storage = {}
        self._next_id = 1

    def save(self, surat: Surat):
        if surat.surat_id is None:
            surat.surat_id = self._next_id
            self._next_id += 1
        self.storage[surat.surat_id] = surat
        return surat

    def find_by_id(self, surat_id: int):
        return self.storage.get(surat_id)

    def find_by_hash(self, document_hash: str):
        for surat in self.storage.values():
            if surat.document_hash == document_hash:
                return surat
        return None

    def find_by_mahasiswa(self, mahasiswa_id: int):
        return [s for s in self.storage.values() if s.mahasiswa_id == mahasiswa_id]

    def find_by_status(self, status: str):
        return [s for s in self.storage.values() if s.status.value == status]

    def find_all(self):
        return list(self.storage.values())


class FakeSignatureRepository(SignatureRepository):

    def __init__(self):
        self.storage: dict[int, Signature] = {}
        self._next_id = 1

    def save(self, surat_id: int, signature: Signature) -> Signature:
        signature.signature_id = self._next_id
        signature.surat_id = surat_id
        self._next_id += 1
        self.storage[signature.signature_id] = signature
        return signature

    def update(self, signature: Signature) -> Signature:
        if signature.signature_id in self.storage:
            self.storage[signature.signature_id] = signature
        return signature

    def find_by_surat_id(self, surat_id: int):
        return [s for s in self.storage.values() if s.surat_id == surat_id]

    def find_by_surat_and_owner(self, surat_id: int, owner_id: int):
        for s in self.storage.values():
            if s.surat_id == surat_id and s.owner_id == owner_id:
                return s
        return None

    def find_pending_by_owner(self, owner_id: int):
        return [
            s
            for s in self.storage.values()
            if s.owner_id == owner_id and not s.is_signed()
        ]

    def find_signed_by_owner(self, owner_id: int):
        return [
            s
            for s in self.storage.values()
            if s.owner_id == owner_id and s.is_signed()
        ]


# ------------------------------------------------------------------
# Tests – creation
# ------------------------------------------------------------------


def test_create_surat_with_dosen_ids():
    surat_repo = FakeSuratRepository()
    sig_repo = FakeSignatureRepository()
    service = SuratService(surat_repo, signature_repository=sig_repo)

    surat = Surat(mahasiswa_id=101, jenis="Surat Aktif Kuliah")
    created = service.create_surat(surat, dosen_ids=[201, 202])

    assert created.status == StatusSurat.MENUNGGU_TTD_DOSEN
    # Two pending signature records should be created
    sigs = sig_repo.find_by_surat_id(created.surat_id)
    assert len(sigs) == 2
    assert all(not s.is_signed() for s in sigs)


def test_create_surat_without_dosen_skips_to_admin():
    surat_repo = FakeSuratRepository()
    service = SuratService(surat_repo)

    surat = Surat(mahasiswa_id=101, jenis="Surat Pernyataan")
    created = service.create_surat(surat, dosen_ids=None)

    assert created.status == StatusSurat.MENUNGGU_PROSES_ADMIN


# ------------------------------------------------------------------
# Tests – single dosen workflow
# ------------------------------------------------------------------


def test_single_dosen_workflow():
    surat_repo = FakeSuratRepository()
    sig_repo = FakeSignatureRepository()
    service = SuratService(surat_repo, signature_repository=sig_repo)

    surat = Surat(mahasiswa_id=101, jenis="Surat Aktif Kuliah")
    created = service.create_surat(surat, dosen_ids=[201])
    assert created.status == StatusSurat.MENUNGGU_TTD_DOSEN

    signed = service.tanda_tangan_dosen(created.surat_id, dosen_id=201, image_path="sign.png")
    # Only one dosen → should advance to admin immediately
    assert signed.status == StatusSurat.MENUNGGU_PROSES_ADMIN


# ------------------------------------------------------------------
# Tests – multi-dosen workflow
# ------------------------------------------------------------------


def test_multi_dosen_partial_sign_stays_in_dosen_stage():
    surat_repo = FakeSuratRepository()
    sig_repo = FakeSignatureRepository()
    service = SuratService(surat_repo, signature_repository=sig_repo)

    surat = Surat(mahasiswa_id=101, jenis="Surat Tugas")
    created = service.create_surat(surat, dosen_ids=[201, 202])

    # First dosen signs
    updated = service.tanda_tangan_dosen(created.surat_id, 201, "sign1.png")
    assert updated.status == StatusSurat.MENUNGGU_TTD_DOSEN  # still waiting for 202


def test_multi_dosen_all_sign_advances_to_admin():
    surat_repo = FakeSuratRepository()
    sig_repo = FakeSignatureRepository()
    service = SuratService(surat_repo, signature_repository=sig_repo)

    surat = Surat(mahasiswa_id=101, jenis="Surat Tugas")
    created = service.create_surat(surat, dosen_ids=[201, 202])

    service.tanda_tangan_dosen(created.surat_id, 201, "sign1.png")
    updated = service.tanda_tangan_dosen(created.surat_id, 202, "sign2.png")

    assert updated.status == StatusSurat.MENUNGGU_PROSES_ADMIN


def test_unassigned_dosen_cannot_sign():
    surat_repo = FakeSuratRepository()
    sig_repo = FakeSignatureRepository()
    service = SuratService(surat_repo, signature_repository=sig_repo)

    surat = Surat(mahasiswa_id=101, jenis="Surat Keterangan")
    created = service.create_surat(surat, dosen_ids=[201])

    with pytest.raises(DomainException, match="tidak ditugaskan"):
        service.tanda_tangan_dosen(created.surat_id, 999, "sign.png")


def test_double_sign_raises():
    surat_repo = FakeSuratRepository()
    sig_repo = FakeSignatureRepository()
    service = SuratService(surat_repo, signature_repository=sig_repo)

    # Use two dosen so the first sign doesn't advance the status
    surat = Surat(mahasiswa_id=101, jenis="Surat Keterangan")
    created = service.create_surat(surat, dosen_ids=[201, 202])
    service.tanda_tangan_dosen(created.surat_id, 201, "sign.png")

    with pytest.raises(DomainException, match="sudah menandatangani"):
        service.tanda_tangan_dosen(created.surat_id, 201, "sign2.png")


# ------------------------------------------------------------------
# Tests – dosen rejection
# ------------------------------------------------------------------


def test_reject_dosen_sets_status():
    surat_repo = FakeSuratRepository()
    sig_repo = FakeSignatureRepository()
    service = SuratService(surat_repo, signature_repository=sig_repo)

    surat = Surat(mahasiswa_id=101, jenis="Surat Keterangan")
    created = service.create_surat(surat, dosen_ids=[201])

    rejected = service.reject_dosen(created.surat_id, 201, "Data salah")
    assert rejected.status == StatusSurat.DITOLAK
    assert rejected.rejection_reason == "Data salah"


# ------------------------------------------------------------------
# Tests – full workflow until verified
# ------------------------------------------------------------------


def test_full_workflow_with_single_dosen():
    surat_repo = FakeSuratRepository()
    sig_repo = FakeSignatureRepository()
    service = SuratService(surat_repo, signature_repository=sig_repo)

    surat = Surat(mahasiswa_id=101, jenis="Surat Aktif Kuliah")
    created = service.create_surat(surat, dosen_ids=[201])
    assert created.status == StatusSurat.MENUNGGU_TTD_DOSEN

    signed = service.tanda_tangan_dosen(created.surat_id, 201, "sign.png")
    assert signed.status == StatusSurat.MENUNGGU_PROSES_ADMIN

    approved = service.approve_admin(created.surat_id)
    assert approved.status == StatusSurat.SELESAI
    assert approved.document_hash is not None

    verified = service.verify_surat(approved.document_hash)
    assert verified.surat_id == created.surat_id


# ------------------------------------------------------------------
# Tests – admin actions
# ------------------------------------------------------------------


def test_approve_admin_raises_when_surat_missing():
    service = SuratService(FakeSuratRepository())

    with pytest.raises(SuratNotFoundException):
        service.approve_admin(999)


def test_reject_surat_admin():
    surat_repo = FakeSuratRepository()
    service = SuratService(surat_repo)

    surat = Surat(mahasiswa_id=101, jenis="Surat Keterangan")
    created = service.create_surat(surat)  # no dosen → MENUNGGU_PROSES_ADMIN

    rejected = service.reject_surat(created.surat_id, "Dokumen tidak lengkap")
    assert rejected.status == StatusSurat.DITOLAK
    assert rejected.rejection_reason == "Dokumen tidak lengkap"


# ------------------------------------------------------------------
# Tests – verification
# ------------------------------------------------------------------


def test_verify_raises_when_hash_not_found():
    service = SuratService(FakeSuratRepository())

    with pytest.raises(InvalidDocumentError):
        service.verify_surat("unknown-hash")


# ------------------------------------------------------------------
# Tests – list / history
# ------------------------------------------------------------------


def test_list_by_mahasiswa():
    surat_repo = FakeSuratRepository()
    service = SuratService(surat_repo)

    service.create_surat(Surat(mahasiswa_id=101, jenis="Surat A"))
    service.create_surat(Surat(mahasiswa_id=101, jenis="Surat B"))
    service.create_surat(Surat(mahasiswa_id=999, jenis="Surat C"))

    assert len(service.list_by_mahasiswa(101)) == 2


def test_list_pending_dosen():
    surat_repo = FakeSuratRepository()
    sig_repo = FakeSignatureRepository()
    service = SuratService(surat_repo, signature_repository=sig_repo)

    s1 = service.create_surat(Surat(mahasiswa_id=101, jenis="A"), dosen_ids=[201])
    s2 = service.create_surat(Surat(mahasiswa_id=102, jenis="B"), dosen_ids=[201, 202])
    s3 = service.create_surat(Surat(mahasiswa_id=103, jenis="C"), dosen_ids=[202])

    pending_201 = service.list_pending_dosen(201)
    assert len(pending_201) == 2

    pending_202 = service.list_pending_dosen(202)
    assert len(pending_202) == 2

    # After dosen 201 signs s1
    service.tanda_tangan_dosen(s1.surat_id, 201, "sig.png")
    pending_201 = service.list_pending_dosen(201)
    assert len(pending_201) == 1  # only s2 remaining


def test_list_history_dosen():
    surat_repo = FakeSuratRepository()
    sig_repo = FakeSignatureRepository()
    service = SuratService(surat_repo, signature_repository=sig_repo)

    s1 = service.create_surat(Surat(mahasiswa_id=101, jenis="A"), dosen_ids=[201])
    service.tanda_tangan_dosen(s1.surat_id, 201, "sig.png")

    history = service.list_history_dosen(201)
    assert len(history) == 1
    assert history[0].surat_id == s1.surat_id


def test_list_history_admin():
    surat_repo = FakeSuratRepository()
    service = SuratService(surat_repo)

    service.create_surat(Surat(mahasiswa_id=101, jenis="A"))
    service.create_surat(Surat(mahasiswa_id=102, jenis="B"))

    assert len(service.list_history_admin()) == 2