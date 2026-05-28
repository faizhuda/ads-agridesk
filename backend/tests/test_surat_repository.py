"""Repository-layer tests for SuratRepository.

Covers ordering guarantees and the sequential-surat query helpers
that were added/fixed during the performance and architecture sessions.
"""
import time

import pytest

from app.domain.enums import SuratStatus, UserRole
from app.models.surat import SuratModel
from app.models.user import UserModel
from app.repositories.surat_repository import SuratRepository


def _make_student(db, email="s@u.id", nim="111") -> UserModel:
    u = UserModel(name="S", email=email, password_hash="x", role=UserRole.MAHASISWA, nim=nim)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def _make_surat(db, mahasiswa_id, jenis="test", is_sequential=False) -> SuratModel:
    s = SuratModel(
        mahasiswa_id=mahasiswa_id, jenis=jenis, keperluan="test",
        is_external=True, file_path="/f.pdf",
        status=SuratStatus.DRAFT,
        is_sequential=is_sequential,
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


class TestSuratRepositoryOrdering:
    def test_get_by_mahasiswa_id_ordered_desc(self, db):
        student = _make_student(db)
        s1 = _make_surat(db, student.id, jenis="first")
        # Tiny sleep so created_at timestamps differ in SQLite
        time.sleep(0.05)
        s2 = _make_surat(db, student.id, jenis="second")

        repo = SuratRepository(db)
        results = repo.get_by_mahasiswa_id(student.id)
        assert len(results) == 2
        # Most recent first
        assert results[0].id == s2.id
        assert results[1].id == s1.id

    def test_get_all_ordered_desc(self, db):
        s1 = _make_student(db, email="a@u.id", nim="111")
        s2 = _make_student(db, email="b@u.id", nim="222")
        surat1 = _make_surat(db, s1.id)
        time.sleep(0.05)
        surat2 = _make_surat(db, s2.id)

        repo = SuratRepository(db)
        results = repo.get_all()
        ids = [r.id for r in results]
        assert ids.index(surat2.id) < ids.index(surat1.id)

    def test_get_by_status_ordered_desc(self, db):
        student = _make_student(db)
        s1 = _make_surat(db, student.id)
        time.sleep(0.05)
        s2 = _make_surat(db, student.id)

        repo = SuratRepository(db)
        results = repo.get_by_status(SuratStatus.DRAFT)
        ids = [r.id for r in results]
        assert ids.index(s2.id) < ids.index(s1.id)


class TestSuratRepositorySequential:
    def test_get_is_sequential_true(self, db):
        student = _make_student(db)
        surat = _make_surat(db, student.id, is_sequential=True)
        repo = SuratRepository(db)
        assert repo.get_is_sequential(surat.id) is True

    def test_get_is_sequential_false(self, db):
        student = _make_student(db)
        surat = _make_surat(db, student.id, is_sequential=False)
        repo = SuratRepository(db)
        assert repo.get_is_sequential(surat.id) is False

    def test_get_sequential_ids_filters_correctly(self, db):
        student = _make_student(db)
        seq = _make_surat(db, student.id, is_sequential=True)
        non_seq = _make_surat(db, student.id, is_sequential=False)

        repo = SuratRepository(db)
        seq_ids = repo.get_sequential_ids({seq.id, non_seq.id})
        assert seq.id in seq_ids
        assert non_seq.id not in seq_ids

    def test_get_sequential_ids_empty_input(self, db):
        repo = SuratRepository(db)
        assert repo.get_sequential_ids(set()) == set()
