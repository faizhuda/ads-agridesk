from datetime import datetime
from app.utils.hash_generator import HashGenerator

class Signature:

    def __init__(self, owner_id: int, role: str, image_path: str):
        self.owner_id = owner_id
        self.role = role  # "MAHASISWA" atau "DOSEN"
        self.image_path = image_path
        self.signed_at = datetime.utcnow()
        self.signature_hash = None

    def attach_hash(self, hash_value: str):
        self.signature_hash = hash_value

    def generate_signature_hash(self, surat_id: int):
        self.signature_hash = HashGenerator.generate_signature_hash(
            surat_id, self.owner_id
        )