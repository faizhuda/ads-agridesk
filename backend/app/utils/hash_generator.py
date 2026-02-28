import hashlib
from datetime import datetime


class HashGenerator:

    SECRET_KEY = "AGRIDESK_SECRET_KEY"

    @staticmethod
    def generate_document_hash(surat_id: int, mahasiswa_id: int):
        raw = f"{surat_id}-{mahasiswa_id}-{datetime.utcnow()}-{HashGenerator.SECRET_KEY}"
        return hashlib.sha256(raw.encode()).hexdigest()

    @staticmethod
    def generate_signature_hash(surat_id: int, dosen_id: int):
        raw = f"{surat_id}-{dosen_id}-{datetime.utcnow()}-{HashGenerator.SECRET_KEY}"
        return hashlib.sha256(raw.encode()).hexdigest()