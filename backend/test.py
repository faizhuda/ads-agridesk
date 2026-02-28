from app.domain.surat import Surat
from app.services.surat_service import SuratService
from app.repositories.inmemory_surat_repository import InMemorySuratRepository

repo = InMemorySuratRepository()
service = SuratService(repo)

surat = Surat(mahasiswa_id=1, jenis="Surat Aktif")
saved = service.ajukan_surat(surat)

print(saved.status)