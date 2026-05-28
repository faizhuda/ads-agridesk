import hashlib
import uuid


class HashGenerator:
    @staticmethod
    def generate_hash(data: str) -> str:
        raw = f"{data}:{uuid.uuid4()}"
        return hashlib.sha256(raw.encode()).hexdigest()

    @staticmethod
    def generate_document_hash(surat_id: int, mahasiswa_id: int) -> str:
        raw = f"surat:{surat_id}:mahasiswa:{mahasiswa_id}:{uuid.uuid4()}"
        return hashlib.sha256(raw.encode()).hexdigest()

    # NOTE: Hashes include a random UUID component and are non-deterministic.
    # Verification is done via database lookup (get_by_signature_hash / get_by_document_hash),
    # not by re-computing — calling verify_hash() against a generated hash will never match.
