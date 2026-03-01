import time
from pathlib import Path
from fastapi.testclient import TestClient

from app.main import app
from app.database.db import SessionLocal
from app.database.models.audit_log_model import AuditLogModel
from app.utils.jwt_utils import JWTUtils


def _register(
    client: TestClient,
    name: str,
    email: str,
    password: str,
    role: str,
    nim: str | None = None,
    nip: str | None = None,
):
    response = client.post(
        "/register",
        json={
            "name": name,
            "email": email,
            "password": password,
            "role": role,
            "nim": nim,
            "nip": nip,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["email"] == email
    assert payload["role"] == role
    assert payload.get("nim") == nim
    assert payload.get("nip") == nip


def _login(client: TestClient, email: str, password: str) -> str:
    response = client.post(
        "/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["token_type"] == "bearer"
    return payload["access_token"]


def _user_id_from_token(token: str) -> int:
    decoded = JWTUtils.decode_token(token)
    return int(decoded["sub"])


def test_api_full_workflow_multi_dosen():
    """Multi-dosen internal surat workflow: create → two dosen sign → admin approve → verify."""
    client = TestClient(app)
    suffix = str(int(time.time() * 1000))
    password = "Pass1234!"

    mahasiswa_email = f"mahasiswa_{suffix}@agridesk.local"
    dosen1_email = f"dosen1_{suffix}@agridesk.local"
    dosen2_email = f"dosen2_{suffix}@agridesk.local"
    admin_email = f"admin_{suffix}@agridesk.local"

    _register(client, "Mahasiswa", mahasiswa_email, password, "MAHASISWA", nim=f"MHS{suffix}")
    _register(client, "Dosen Satu", dosen1_email, password, "DOSEN", nip=f"DS1{suffix}")
    _register(client, "Dosen Dua", dosen2_email, password, "DOSEN", nip=f"DS2{suffix}")
    _register(client, "Admin", admin_email, password, "ADMIN", nip=f"ADM{suffix}")

    mahasiswa_token = _login(client, mahasiswa_email, password)
    dosen1_token = _login(client, dosen1_email, password)
    dosen2_token = _login(client, dosen2_email, password)
    admin_token = _login(client, admin_email, password)

    dosen1_id = _user_id_from_token(dosen1_token)
    dosen2_id = _user_id_from_token(dosen2_token)

    # --- Create surat with two dosen ---
    create_response = client.post(
        "/surat",
        json={
            "jenis": "Surat Aktif Kuliah",
            "keperluan": "Beasiswa",
            "dosen_ids": [dosen1_id, dosen2_id],
        },
        headers={"Authorization": f"Bearer {mahasiswa_token}"},
    )
    assert create_response.status_code == 200
    create_payload = create_response.json()
    assert create_payload["status"] == "MENUNGGU_TTD_DOSEN"
    assert len(create_payload.get("signatures", [])) == 2
    surat_id = create_payload["surat_id"]

    # --- Dosen 1 sees pending ---
    pending1 = client.get(
        "/surat/pending-dosen",
        headers={"Authorization": f"Bearer {dosen1_token}"},
    )
    assert pending1.status_code == 200
    assert any(s["surat_id"] == surat_id for s in pending1.json())

    # --- Dosen 1 signs ---
    sign1 = client.post(
        f"/surat/{surat_id}/ttd-dosen",
        json={"image_path": "signatures/dosen1.png"},
        headers={"Authorization": f"Bearer {dosen1_token}"},
    )
    assert sign1.status_code == 200
    assert sign1.json()["status"] == "MENUNGGU_TTD_DOSEN"  # still waiting for dosen2

    # --- Dosen 2 signs ---
    sign2 = client.post(
        f"/surat/{surat_id}/ttd-dosen",
        json={"image_path": "signatures/dosen2.png"},
        headers={"Authorization": f"Bearer {dosen2_token}"},
    )
    assert sign2.status_code == 200
    assert sign2.json()["status"] == "MENUNGGU_PROSES_ADMIN"  # all signed

    # --- Admin approves ---
    approve_response = client.post(
        f"/surat/{surat_id}/approve-admin",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert approve_response.status_code == 200
    approve_payload = approve_response.json()
    assert approve_payload["status"] == "SELESAI"
    document_hash = approve_payload["document_hash"]
    assert approve_payload["pdf_path"]
    assert approve_payload["qr_path"]
    assert Path(approve_payload["pdf_path"]).exists()
    assert Path(approve_payload["qr_path"]).exists()

    # --- Public verification ---
    verify_response = client.get(f"/verify/{document_hash}")
    assert verify_response.status_code == 200
    verify_payload = verify_response.json()
    assert verify_payload["status"] == "VALID"
    assert verify_payload["document_hash"] == document_hash

    # --- Audit log check ---
    db = SessionLocal()
    try:
        surat_events = (
            db.query(AuditLogModel)
            .filter(AuditLogModel.target_type == "SURAT", AuditLogModel.target_id == str(surat_id))
            .all()
        )
        surat_event_names = {event.event_name for event in surat_events}
        assert "SURAT_SUBMIT" in surat_event_names
        assert "SURAT_SIGN_DOSEN" in surat_event_names
        assert "SURAT_APPROVE_ADMIN" in surat_event_names
    finally:
        db.close()


def test_api_no_dosen_workflow():
    """Surat without dosen requirement skips to admin stage directly."""
    client = TestClient(app)
    suffix = str(int(time.time() * 1000))
    password = "Pass1234!"

    mahasiswa_email = f"mhs_nodosen_{suffix}@agridesk.local"
    admin_email = f"admin_nodosen_{suffix}@agridesk.local"

    _register(client, "MHS NoDosen", mahasiswa_email, password, "MAHASISWA", nim=f"ND{suffix}")
    _register(client, "Admin NoDosen", admin_email, password, "ADMIN", nip=f"AND{suffix}")

    mahasiswa_token = _login(client, mahasiswa_email, password)
    admin_token = _login(client, admin_email, password)

    create_response = client.post(
        "/surat",
        json={"jenis": "Surat Pernyataan", "keperluan": "Pernyataan aktif"},
        headers={"Authorization": f"Bearer {mahasiswa_token}"},
    )
    assert create_response.status_code == 200
    assert create_response.json()["status"] == "MENUNGGU_PROSES_ADMIN"
    surat_id = create_response.json()["surat_id"]

    approve = client.post(
        f"/surat/{surat_id}/approve-admin",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert approve.status_code == 200
    assert approve.json()["status"] == "SELESAI"


def test_api_dosen_reject():
    """Dosen rejects a surat."""
    client = TestClient(app)
    suffix = str(int(time.time() * 1000))
    password = "Pass1234!"

    mhs_email = f"mhs_rej_{suffix}@agridesk.local"
    dosen_email = f"dosen_rej_{suffix}@agridesk.local"

    _register(client, "MHS Reject", mhs_email, password, "MAHASISWA", nim=f"RJ{suffix}")
    _register(client, "Dosen Reject", dosen_email, password, "DOSEN", nip=f"DRJ{suffix}")

    mhs_token = _login(client, mhs_email, password)
    dosen_token = _login(client, dosen_email, password)
    dosen_id = _user_id_from_token(dosen_token)

    create = client.post(
        "/surat",
        json={"jenis": "Surat Tugas", "dosen_ids": [dosen_id]},
        headers={"Authorization": f"Bearer {mhs_token}"},
    )
    assert create.status_code == 200
    surat_id = create.json()["surat_id"]

    reject = client.post(
        f"/surat/{surat_id}/reject-dosen",
        json={"reason": "Data tidak valid"},
        headers={"Authorization": f"Bearer {dosen_token}"},
    )
    assert reject.status_code == 200
    assert reject.json()["status"] == "DITOLAK"
    assert reject.json()["rejection_reason"] == "Data tidak valid"


def test_api_role_guard_blocks_non_mahasiswa_create_surat():
    client = TestClient(app)
    suffix = str(int(time.time() * 1000))
    password = "Pass1234!"

    dosen_email = f"dosen_only_{suffix}@agridesk.local"
    _register(client, "Dosen Guard", dosen_email, password, "DOSEN", nip=f"DG{suffix}")
    dosen_token = _login(client, dosen_email, password)

    response = client.post(
        "/surat",
        json={"jenis": "Surat Keterangan", "is_external": False},
        headers={"Authorization": f"Bearer {dosen_token}"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Akses ditolak"


def test_api_mahasiswa_history():
    """GET /surat/me returns the mahasiswa's surat list."""
    client = TestClient(app)
    suffix = str(int(time.time() * 1000))
    password = "Pass1234!"

    mhs_email = f"mhs_hist_{suffix}@agridesk.local"
    _register(client, "MHS Hist", mhs_email, password, "MAHASISWA", nim=f"HI{suffix}")
    mhs_token = _login(client, mhs_email, password)

    client.post(
        "/surat",
        json={"jenis": "Surat A"},
        headers={"Authorization": f"Bearer {mhs_token}"},
    )
    client.post(
        "/surat",
        json={"jenis": "Surat B"},
        headers={"Authorization": f"Bearer {mhs_token}"},
    )

    history = client.get(
        "/surat/me",
        headers={"Authorization": f"Bearer {mhs_token}"},
    )
    assert history.status_code == 200
    assert len(history.json()) == 2


def test_api_list_dosen():
    """GET /users/dosen returns dosen users for selection."""
    client = TestClient(app)
    suffix = str(int(time.time() * 1000))
    password = "Pass1234!"

    dosen_email = f"dosen_list_{suffix}@agridesk.local"
    mhs_email = f"mhs_list_{suffix}@agridesk.local"

    _register(client, "Dosen List", dosen_email, password, "DOSEN", nip=f"DL{suffix}")
    _register(client, "MHS List", mhs_email, password, "MAHASISWA", nim=f"ML{suffix}")

    mhs_token = _login(client, mhs_email, password)

    response = client.get(
        "/users/dosen",
        headers={"Authorization": f"Bearer {mhs_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(d["email"] == dosen_email for d in data)
