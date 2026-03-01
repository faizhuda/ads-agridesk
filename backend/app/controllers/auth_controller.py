import logging
from typing import List

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.services.auth_service import AuthService
from app.services.audit_service import AuditService
from app.schemas.auth_schema import RegisterRequest
from app.schemas.surat_schema import DosenPublicInfo
from app.database.db import get_db
from app.utils.jwt_utils import JWTUtils
from app.utils.dependencies import get_current_user
from app.repositories.postgres_user_repository import PostgresUserRepository
from app.repositories.postgres_audit_log_repository import PostgresAuditLogRepository

router = APIRouter()
logger = logging.getLogger(__name__)


def _safe_audit_log(
    db: Session,
    event_name: str,
    actor_id: int | None,
    actor_role: str | None,
    target_type: str | None,
    target_id: str | None,
    metadata: dict | None,
    ip_address: str | None,
):
    try:
        audit_service = AuditService(PostgresAuditLogRepository(db))
        audit_service.log_event(
            event_name=event_name,
            actor_id=actor_id,
            actor_role=actor_role,
            target_type=target_type,
            target_id=target_id,
            metadata=metadata,
            ip_address=ip_address,
        )
    except Exception as exc:
        logger.warning("Failed to write audit log: %s", exc)


@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    repo = PostgresUserRepository(db)
    service = AuthService(repo)

    user = service.register(
        request.name,
        request.email,
        request.password,
        request.role,
        request.nim,
        request.nip,
    )

    _safe_audit_log(
        db=db,
        event_name="AUTH_REGISTER",
        actor_id=user.user_id,
        actor_role=user.role.value,
        target_type="USER",
        target_id=str(user.user_id),
        metadata={"email": user.email},
        ip_address=None,
    )

    return {
        "email": user.email,
        "role": user.role.value,
        "nim": user.nim,
        "nip": user.nip,
    }


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    repo = PostgresUserRepository(db)
    service = AuthService(repo)

    token_payload = service.login(form_data.username, form_data.password)
    decoded_token = JWTUtils.decode_token(token_payload["access_token"])

    _safe_audit_log(
        db=db,
        event_name="AUTH_LOGIN",
        actor_id=int(decoded_token["sub"]),
        actor_role=decoded_token.get("role"),
        target_type="USER",
        target_id=decoded_token["sub"],
        metadata={"email": decoded_token.get("email")},
        ip_address=None,
    )

    return token_payload


@router.get("/users/dosen", response_model=List[DosenPublicInfo])
def list_dosen(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    """Return all users with DOSEN role (for dosen selection when creating surat)."""
    repo = PostgresUserRepository(db)
    dosen_list = repo.find_by_role("DOSEN")
    return [
        DosenPublicInfo(
            user_id=d.user_id,
            name=d.name,
            email=d.email,
            nip=d.nip,
        )
        for d in dosen_list
    ]