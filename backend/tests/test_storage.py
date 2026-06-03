"""Unit tests for StorageService path-traversal guard (BUG-01).

These tests run without a database — they only need a real filesystem
temp directory.  The guard must raise PermissionError for any path that
resolves outside the configured upload directory.
"""
import os
import tempfile

import pytest

from app.utils.storage import StorageService


@pytest.fixture
def storage(tmp_path):
    """Return a StorageService whose upload_dir lives in a temp directory."""
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()

    svc = StorageService.__new__(StorageService)
    svc.upload_dir = str(upload_dir)
    return svc, upload_dir


class TestPathTraversalGuard:
    def test_classic_dotdot_traversal_raises(self, storage):
        svc, _ = storage
        with pytest.raises(PermissionError, match="outside upload directory"):
            svc.get_file_content("uploads/../../../etc/passwd")

    def test_dotdot_within_path_raises(self, storage):
        svc, _ = storage
        with pytest.raises(PermissionError, match="outside upload directory"):
            svc.get_file_content("../../sensitive_file.txt")

    def test_absolute_path_outside_upload_dir_raises(self, storage, tmp_path):
        svc, _ = storage
        # Create a file outside the upload_dir but still inside tmp_path
        secret = tmp_path / "secret.txt"
        secret.write_bytes(b"secret")
        with pytest.raises(PermissionError, match="outside upload directory"):
            svc.get_file_content(str(secret))

    def test_valid_path_inside_upload_dir_works(self, storage):
        svc, upload_dir = storage
        # Create a legit file
        legit = upload_dir / "valid.txt"
        legit.write_bytes(b"hello")
        content = svc.get_file_content("valid.txt")
        assert content == b"hello"

    def test_valid_path_with_upload_dir_prefix_works(self, storage):
        svc, upload_dir = storage
        legit = upload_dir / "doc.pdf"
        legit.write_bytes(b"%PDF")
        # Caller supplies the full upload_dir path as prefix, e.g. "/tmp/.../uploads/doc.pdf"
        full_path = str(upload_dir / "doc.pdf")
        content = svc.get_file_content(full_path)
        assert content == b"%PDF"

    def test_nonexistent_file_raises_file_not_found(self, storage):
        svc, _ = storage
        with pytest.raises(FileNotFoundError):
            svc.get_file_content("nonexistent_file_xyz.bin")

    def test_file_exists_returns_true_for_existing(self, storage):
        svc, upload_dir = storage
        f = upload_dir / "x.txt"
        f.write_bytes(b"x")
        assert svc.file_exists("x.txt") is True

    def test_file_exists_returns_false_for_missing(self, storage):
        svc, _ = storage
        assert svc.file_exists("no_such_file.txt") is False

    def test_upload_file_returns_path_inside_upload_dir(self, storage):
        svc, upload_dir = storage
        path = svc.upload_file(b"data", "test.pdf")
        assert path.startswith(str(upload_dir))
        assert os.path.exists(path)

    def test_upload_file_content_is_intact(self, storage):
        svc, _ = storage
        data = b"\x00\x01\x02\x03test content"
        path = svc.upload_file(data, "binary.bin")
        with open(path, "rb") as f:
            assert f.read() == data
