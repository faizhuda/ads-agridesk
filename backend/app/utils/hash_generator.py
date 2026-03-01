import hashlib
import uuid
from app.core.settings import settings


class HashGenerator:

    @staticmethod
    def _get_secret_key() -> str:
        return settings.hash_secret

    @staticmethod
    def generate_document_hash(surat_id: int, mahasiswa_id: int) -> str:
        raw = f"{surat_id}-{mahasiswa_id}-{uuid.uuid4()}-{HashGenerator._get_secret_key()}"
        return hashlib.sha256(raw.encode()).hexdigest()

    @staticmethod
    def generate_signature_hash(surat_id: int, owner_id: int) -> str:
        raw = f"{surat_id}-{owner_id}-{uuid.uuid4()}-{HashGenerator._get_secret_key()}"
        return hashlib.sha256(raw.encode()).hexdigest()