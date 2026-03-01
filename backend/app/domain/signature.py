from datetime import datetime, timezone


class Signature:
    """Domain entity representing a signature on a surat.

    A signature is created in *pending* state (``signed_at`` is None) when a
    dosen is assigned to sign a letter.  The ``sign`` method completes the
    signing action.
    """

    def __init__(self, owner_id: int, role: str, image_path: str | None = None):
        self.signature_id: int | None = None
        self.surat_id: int | None = None
        self.owner_id = owner_id
        self.role = role
        self.image_path = image_path
        self.signed_at: datetime | None = None
        self.signature_hash: str | None = None
        self.created_at = None
        self.updated_at = None

    def sign(self, image_path: str, signature_hash: str):
        """Complete the signing action."""
        self.image_path = image_path
        self.signature_hash = signature_hash
        self.signed_at = datetime.now(timezone.utc)

    def is_signed(self) -> bool:
        return self.signed_at is not None

    def set_signature_hash(self, hash_value: str):
        self.signature_hash = hash_value